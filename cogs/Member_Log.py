from datetime import datetime, timedelta
import sqlite3

from discord import Embed, AllowedMentions
from discord.ext import commands
from pytz import timezone


class Member_Log(commands.Cog):
    """メンバー用のログ機能関連のコマンドがあります。"""
    def __init__(self, bot):
        self.bot = bot
        self.welcome_notice = []
        self.bot.loop.create_task(self.setup())

    async def setup(self):
        await self.bot.wait_until_ready()
        data = self.bot.db.welcome_notice_get()
        if len(data) > 0:
            for g in data[0]:
                self.welcome_notice.append(g)

    @commands.command(name='notice-on',
                      description='メンバー参加通知の機能をオンにします',
                      brief=['この機能の説明は、メンバーのアカウント作成日が3日以内の際に、'
                             'サーバーの管理者にDMを送信する機能です。\n'
                             'このコマンドの実行には、権限:管理者が必要です', 'administrator', 'notice-function'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def _notice_on(self, ctx):
        try:
            res = self.bot.db.welcome_notice_set(ctx.guild.id)
            if res:
                self.welcome_notice.append(ctx.guild.id)
                success_embed = Embed(description='メンバー参加通知の機能をオンにしました')
                return await ctx.reply(embed=success_embed, allowed_mentions=AllowedMentions.none())
        except sqlite3.IntegrityError:
            integrity_error = Embed(description='メッセージURL展開の機能をオンにしました')
            return await ctx.reply(embed=integrity_error, allowed_mentions=AllowedMentions.none())

    @commands.command(name='notice-off',
                      description='メンバー参加通知の機能をオフにします',
                      brief=['この機能の説明は、メンバーのアカウント作成日が3日以内の際に、'
                             'サーバーの管理者にDMを送信する機能です。\n'
                             'このコマンドの実行には、権限:管理者が必要です', 'administrator', 'notice-function'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def _notice_off(self, ctx):
        res = self.bot.db.welcome_notice_unset(ctx.guild.id)
        if res:
            self.welcome_notice.remove(ctx.guild.id)
            success_embed = Embed(description='メンバー参加通知の機能をオフにしました')
            return await ctx.reply(embed=success_embed, allowed_mentions=AllowedMentions.none())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id in self.welcome_notice:
            if not member.bot:
                if datetime.utcnow() - member.created_at < timedelta(days=4):
                    created_jst = member.created_at.astimezone(timezone("Asia/Tokyo"))
                    created_at = (created_jst + timedelta(hours=9)).strftime("%Y/%m/%d %H:%M:%S")
                    notice_embed = Embed(title='メンバー参加通知',
                                         description='次のユーザーのアカウント作成日が3日以内だっため通知しました')
                    notice_embed.add_field(name='参加ユーザー', value=f'> {member}', inline=False)
                    notice_embed.add_field(name='参加サーバー', value=f'> {member.guild.name}', inline=False)
                    notice_embed.add_field(name='アカウント作成日', value=f'> {created_at}', inline=False)
                    notice_embed.set_thumbnail(url=member.avatar_url)
                    notice_embed.set_author(name=f'{member}', icon_url=member.avatar_url)
                    await member.guild.owner.send(embed=notice_embed)


def setup(bot):
    bot.add_cog(Member_Log(bot))
