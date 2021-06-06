import asyncio
import random
import json
from discord.ext import commands
from discord import Embed


class Game(commands.Cog):
    """Game関連コマンド"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='三字熟語のトレーニングが出来ます。')
    async def tt(self, ctx):
        with open("./data/tt_data.json", "r", encoding='UTF-8') as config:
            data = json.load(config)
        q = data[random.randint(1, 128)]

        question_embed = Embed(title=f'{ctx.author} さんの問題',
                               description=f'【 {q[0]} 】の読み方をひらがなで答えよ！')
        q_msg = await ctx.send(embed=question_embed)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            message = await self.bot.wait_for('message', timeout=20, check=check)
        except asyncio.TimeoutError:
            return await q_msg.edit(embed=Embed(description='残念！時間切れです...'))
        else:
            if message.content == q[1]:
                return await q_msg.edit(embed=Embed(description='おめでとう！正解です！'))
            else:
                return await q_msg.edit(embed=Embed(description=f'**残念..不正解です..**\n答えは【 {q[1]} 】みたいでした'))


def setup(bot):
    bot.add_cog(Game(bot))
