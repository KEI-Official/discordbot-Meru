import re
from discord import Embed, AllowedMentions
from discord.ext import commands
import sqlite3

discord_message_url = (
    '(?!<)https://(ptb.|canary.)?discord(app)?.com/channels/'
    '(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})(?!>)'
)


class MUrl(commands.Cog):
    """メッセージURL展開に関するコマンドが載っています"""

    def __init__(self, bot):
        self.bot = bot
        self.expander = []
        self.bot.loop.create_task(self.setup())

    async def setup(self):
        await self.bot.wait_until_ready()
        data = self.bot.db.message_expand_get()
        for g in data[0]:
            self.expander.append(g)

    @commands.command(name='url-on',
                      description='メッセージURL展開の機能をオンにします',
                      aliases=['expand-on'],
                      brief='このコマンドの実行には、権限:メッセージの管理が必要です')
    @commands.has_permissions(manage_messages=True)
    async def _expand_on(self, ctx):
        if ctx.guild:
            try:
                res = self.bot.db.message_expand_set(ctx.guild.id)
                if res:
                    self.expander.append(ctx.guild.id)
                    success_embed = Embed(description='メッセージURL展開の機能をオンにしました')
                    return await ctx.reply(embed=success_embed, allowed_mentions=AllowedMentions.none())
            except sqlite3.IntegrityError:
                integrity_error = Embed(description='メッセージURL展開の機能をオンにしました')
                return await ctx.reply(embed=integrity_error, allowed_mentions=AllowedMentions.none())

    @commands.command(name='url-off',
                      description='メッセージURL展開の機能をオフにします',
                      aliases=['expand-off'],
                      brief='このコマンドの実行には、権限:メッセージの管理が必要です')
    @commands.has_permissions(manage_messages=True)
    async def _expand_off(self, ctx):
        if ctx.guild:
            res = self.bot.db.message_expand_unset(ctx.guild.id)
            if res:
                success_embed = Embed(description='メッセージURL展開の機能をオフにしました')
                self.expander.remove(ctx.guild.id)
                return await ctx.reply(embed=success_embed, allowed_mentions=AllowedMentions.none())

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild
        if guild.id in self.expander:
            regex_res = re.findall(discord_message_url, message.content)
            if regex_res and regex_res[0] == '<' and regex_res[-1] == '>':
                return
            if message.author.bot:
                return
            messages = []

            for con in re.finditer(discord_message_url, message.content):
                guild = self.bot.get_guild(int(con['guild']))
                channel = guild.get_channel(int(con['channel']))
                fetched_message = await channel.fetch_message(int(con['message']))
                messages.append(fetched_message)

            for msg in messages:
                embed = Embed(
                    description=f'{msg.content if not msg.channel.is_nsfw() else "NSFWメッセージのため非表示"}\n\n'
                                f'[元メッセージへ]({msg.jump_url})',
                    timestamp=msg.created_at,
                    color=0x2ECC69,
                )
                embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
                embed.set_footer(text=f'{msg.channel}', icon_url=msg.guild.icon_url)
                if msg.attachments:
                    embed.set_image(url=msg.attachments[0].proxy_url)

                await message.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(MUrl(bot))
