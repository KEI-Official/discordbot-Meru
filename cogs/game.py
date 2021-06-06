import asyncio
import random
import json
from discord.ext import commands
from discord import Embed, AllowedMentions


class Game(commands.Cog):
    """Game関連コマンド"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='三字熟語のトレーニングが出来ます')
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

    @commands.group(description='難易度別のマルバツクイズが出来ます',
                    usage='[e(簡単) | n(普通) | h(難しい)]',
                    aliases=['mb'])
    async def marubatu(self, ctx):
        if ctx.invoked_subcommand is None:
            no_sub_msg = Embed(description='難易度を指定してください\n```\n・e | 簡単\n・n | 普通\n・h | 難しい\n```')
            return await ctx.reply(embed=no_sub_msg, allowed_mentions=AllowedMentions.none())

    # TODO: 問題を1日5個増やす
    def get_question(self, level):
        with open(f'./data/{level}_marubatu.json', 'r', encoding='UTF-8') as e_data:
            data = json.load(e_data)
        return data[random.randint(0, len(data)-1)]

    async def send_question(self, ctx, q_embed, q):
        def check_q(q_answer, user_answer):
            if q_answer == user_answer:
                return True
            else:
                return False

        q_msg = await ctx.reply(embed=q_embed, allowed_mentions=AllowedMentions.none())
        await q_msg.add_reaction('\U00002b55')
        await q_msg.add_reaction('\U0000274c')

        def check(p_reaction, p_user):
            return p_user == ctx.author and p_reaction.message == q_msg

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
        except asyncio.TimeoutError:
            return await q_msg.edit(embed=Embed(description='残念！時間切れです...'))
        else:
            if check_q(q[1], str(reaction)):
                a_msg = Embed(title='正解！',
                              description=f'ちなみに...\n```\n{q[2]}\n```')
                return await q_msg.edit(embed=a_msg)
            else:
                w_msg = Embed(title='残念！不正解',
                              description=f'答え：{q[1]}\n\nちなみに...\n```\n{q[2]}\n```')
                return await q_msg.edit(embed=w_msg)

    @marubatu.command(name='e')
    async def sub_e(self, ctx):
        q = self.get_question('easy')
        q_embed = Embed(title=f'{ctx.author} さんの問題',
                        description=f'難易度 - 簡単```\n{q[0]}\n```\n⭕ か ❌ か。')
        await self.send_question(ctx, q_embed, q)

    @marubatu.command(name='n')
    async def sub_n(self, ctx):
        q = self.get_question('normal')
        q_embed = Embed(title=f'{ctx.author} さんの問題',
                        description=f'難易度 - 普通\n```\n{q[0]}\n```\n⭕ か ❌ か。')
        await self.send_question(ctx, q_embed, q)

    @marubatu.command(name='h')
    async def sub_h(self, ctx):
        q = self.get_question('hard')
        q_embed = Embed(title=f'{ctx.author} さんの問題',
                        description=f'難易度 - 難しい\n```\n{q[0]}\n```\n⭕ か ❌ か。')
        await self.send_question(ctx, q_embed, q)


def setup(bot):
    bot.add_cog(Game(bot))
