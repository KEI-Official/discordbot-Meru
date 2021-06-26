import re
from discord import Embed, AllowedMentions
from discord.ext import commands
import sqlite3

discord_message_url = (
    'https://(ptb.|canary.)?discord(app)?.com/channels/'
    '(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})'
)


class MUrl(commands.Cog):
    """メッセージURL展開"""

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
                      aliases=['expand-on'])
    @commands.has_permissions(manage_messages=True)
    async def _expand_on(self, ctx):
        if ctx.guild:
            try:
                res = self.bot.db.message_expand_set(ctx.guild.id)
                if res:
                    success_embed = Embed(description='メッセージURL展開の機能をオンにしました')
                    return await ctx.reply(embed=success_embed, allowed_mentions=AllowedMentions.none())
            except sqlite3.IntegrityError:
                integrity_error = Embed(description='メッセージURL展開の機能をオンにしました')
                return await ctx.reply(embed=integrity_error, allowed_mentions=AllowedMentions.none())

    @commands.command(name='url-off',
                      description='メッセージURL展開の機能をオフにします',
                      aliases=['expand-off'])
    @commands.has_permissions(manage_messages=True)
    async def _expand_off(self, ctx):
        if ctx.guild:
            res = self.bot.db.message_expand_unset(ctx.guild.id)
            if res:
                success_embed = Embed(description='メッセージURL展開の機能をオフにしました')
                return await ctx.reply(embed=success_embed, allowed_mentions=AllowedMentions.none())

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild
        if guild.id in self.expander:
            if message.author.bot:
                return
            messages = []

            for con in re.finditer(discord_message_url, message.content):
                guild = self.bot.get_guild(int(con['guild']))
                channel = guild.get_channel(int(con['channel']))
                fetched_message = await channel.fetch_message(int(con['message']))
                messages.append(fetched_message)

            for m in messages:
                embed = Embed(
                    description=f'{m.content if not m.channel.is_nsfw() else "NSFWメッセージのため非表示"}\n\n'
                                f'[元メッセージへ]({m.jump_url})',
                    timestamp=m.created_at,
                    color=0x2ECC69,
                )
                embed.set_author(name=m.author.display_name, icon_url=m.author.avatar_url)
                embed.set_footer(text=f'{m.channel}', icon_url=m.guild.icon_url)
                if m.attachments:
                    embed.set_image(url=m.attachments[0].url)
                embeds = embed

                await message.channel.send(embed=embeds)


def setup(bot):
    bot.add_cog(MUrl(bot))
