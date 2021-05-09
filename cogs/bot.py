import math
import discord
from discord.ext import commands


class Bot(commands.Cog):
    """Bot関連コマンド"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Botの応答速度を測ります')
    async def ping(self, ctx):
        await ctx.reply(f'🏓 Pong! - {math.floor(self.bot.latency * 1000)} ms',
                        allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='BOTの招待リンクを出します')
    async def invite(self, ctx):
        await ctx.reply(f'invite',
                        allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='BOTの情報を表示します')
    async def about(self, ctx):
        await ctx.reply(f'about',
                        allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='BOTの利用規約を表示します')
    async def terms(self, ctx):
        await ctx.reply(f'terms',
                        allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='Botの負荷状況を表示します')
    async def status(self, ctx):
        await ctx.replay(f'',
                         allowed_mentions=discord.AllowedMentions.none())


def setup(bot):
    bot.add_cog(Bot(bot))
