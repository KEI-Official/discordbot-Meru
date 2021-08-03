import discord
from discord.ext import commands


class User_Value(commands.Cog):
    """ユーザーのスコアに関するコマンドなどが入っています"""
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db

    @commands.is_owner()
    @commands.group(description='ユーザースコアを操作します')
    async def score(self, ctx):
        if not ctx.invoked_subcommand:
            return

    @commands.is_owner()
    @score.command()
    async def update(self, ctx, user: discord.User = None, value=None, reason=''):
        if not user:
            return await ctx.reply('ユーザーを指定してください', allowed_mentions=discord.AllowedMentions.none())

        if not value:
            return await ctx.reply('スコアと理由を記入してください', allowed_mentions=discord.AllowedMentions.none())

        if ctx.guild:
            res = self.db.user_evaluation_get(user.id)
            if res:
                ban_count = res[0][2]
                reason_list = str(res[0][3]).split(',')
                print(reason_list)
                reason_list.append(str(reason))
                print(','.join(reason_list))
                check = self.db.user_evaluation_update(user.id, str(value), str(ban_count), ','.join(reason_list))
                if check:
                    return await ctx.reply('設定が完了しました', allowed_mentions=discord.AllowedMentions.none())
            else:
                check = self.db.user_evaluation_set(user.id, str(value), '0', str(reason))
                if check:
                    return await ctx.reply('設定が完了しました', allowed_mentions=discord.AllowedMentions.none())

    @commands.is_owner()
    @score.command()
    async def remove(self, ctx, user: discord.User = None):
        if not user:
            return await ctx.reply('ユーザーを指定してください', allowed_mentions=discord.AllowedMentions.none())

        if ctx.guild:
            res = self.bot.db.user_evaluation_del(user.id)
            if res:
                return await ctx.reply('スコアデータをリセットしました', allowed_mentions=discord.AllowedMentions.none())

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        res = self.db.user_evaluation_get(user.id)
        if res:
            old_ban_count = res[0][2]
            old_score = res[0][2]
            reason = res[0][3]
            new_ban_count = 1 + int(old_ban_count)
            if new_ban_count == 3:
                new_score = int(old_score) - 1
            elif new_ban_count == 5:
                new_score = int(old_score) - 1.5
            elif new_ban_count > 7:
                new_score = int(old_score) - 1.5

            check = self.db.user_evaluation_update(user.id, str(new_score), new_ban_count, reason)
            if check:
                owner = await self.bot.fetch_user((await self.bot.application_info()).owner.id)
                return await owner.send(f'{user} が {guild} にてBanされたため、スコアが {new_score}　になりました')
        else:
            check = self.db.user_evaluation_set(user.id, '9.5', '1', '[メル]Banによる減少')
            if check:
                owner = await self.bot.fetch_user((await self.bot.application_info()).owner.id)
                return await owner.send(f'{user} が {guild} にてBanされたため、スコアが 9.5 になりました')


def setup(bot):
    bot.add_cog(User_Value(bot))
