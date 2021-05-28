import asyncio
import re
import discord
from discord.ext import commands


class Admin(commands.Cog):
    """Admin関連コマンド"""
    def __init__(self, bot):
        self.bot = bot
        self.get_user = None

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user=None, reason=None):
        if user is None:
            no_user = discord.Embed(description='BANを行うユーザーをIDで指定してください')
            return await ctx.reply(embed=no_user, allowed_mentions=discord.AllowedMentions.none())
        elif ctx.message.mentions:
            self.get_user = ctx.message.mentions[0]
        elif re.search(r'[0-9]{18}', user) is not None:
            pre_user = ctx.guild.get_member(int(user))
            if pre_user:
                self.get_user = pre_user
            else:
                no_user_msg = discord.Embed(description='ユーザーが見つかりませんでした\n**考えられる原因**```'
                                                        '\n・IDは間違っていませんか？\n・ユーザーはサーバーにいますか？\n```')
                return await ctx.reply(embed=no_user_msg, allowed_mentions=discord.AllowedMentions.none())
        if self.get_user is not None:
            veri_msg = discord.Embed(title='BAN確認画面',
                                     description='以下のユーザーにBANを行います。\n行う場合は`y`、キャンセルする場合は`n`を送信してください。')
            veri_msg.add_field(name='名前', value=f'{self.get_user}')
            veri_msg.add_field(name='ID', value=f'{self.get_user.id}')
            if reason is not None:
                veri_msg.add_field(name='理由', value=f'{reason}', inline=False)
            else:
                veri_msg.add_field(name='理由', value='なし', inline=False)

            veri_embed = await ctx.send(embed=veri_msg)

            def check(c_msg):
                return c_msg.author == ctx.author and c_msg.channel == ctx.channel

            try:
                msg = await self.bot.wait_for('message', timeout=20, check=check)
            except asyncio.TimeoutError:
                return await veri_embed.edit(embed=discord.Embed(description='時間切れです...'))
            else:
                if msg.content == 'y':
                    await msg.delete()
                    if reason is not None:
                        await ctx.guild.ban(user=self.get_user, reason=f'{reason}')
                    else:
                        await ctx.guild.ban(user=self.get_user, reason='なし')
                    s_embed = discord.Embed(description='指定ユーザーのBANが完了しました')
                    s_embed.add_field(name='名前', value=f'{self.get_user}')
                    s_embed.add_field(name='ID', value=f'{self.get_user.id}')
                    s_embed.set_footer(text=f'実行者: {ctx.author}')
                    return await veri_embed.edit(embed=s_embed)
                if msg.content == 'n':
                    await msg.delete()
                    return await veri_embed.edit(embed=discord.Embed(description='操作をキャンセルしました'))


def setup(bot):
    bot.add_cog(Admin(bot))
