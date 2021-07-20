import asyncio
import random
import json
from discord.ext import commands
from discord import Embed, AllowedMentions


class Game(commands.Cog):
    """トレーニングといったお遊び系のコマンドがあるカテゴリーです"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='三字熟語のトレーニングが出来ます')
    async def tt(self, ctx):
        with open("./data/tt_data.json", "r", encoding='UTF-8') as config:
            data = json.load(config)
        q = data[random.randint(1, 128)]

        question_embed = Embed(title=f'{ctx.author} さんの問題',
                               description=f'【 {q[0]} 】の読み方をひらがなで答えよ！',
                               color=2263275)
        q_msg = await ctx.send(embed=question_embed)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            message = await self.bot.wait_for('message', timeout=20, check=check)
        except asyncio.TimeoutError:
            return await q_msg.edit(embed=Embed(description='残念！時間切れです...'))
        else:
            if message.content == q[1]:
                return await q_msg.edit(embed=Embed(description='おめでとう！正解です！', color=261888))
            else:
                fal_embed = Embed(description=f'**残念..不正解です..**\n答えは【 {q[1]} 】みたいでした',
                                  color=15409787)
                return await q_msg.edit(embed=fal_embed)

    @commands.group(description='難易度別のマルバツクイズが出来ます',
                    usage='[e(簡単) | n(普通) | h(難しい)]',
                    aliases=['mb'])
    async def marubatu(self, ctx):
        if ctx.invoked_subcommand is None:
            no_sub_msg = Embed(description='難易度を指定してください\n```\n・e | 簡単\n・n | 普通\n・h | 難しい\n```')
            return await ctx.reply(embed=no_sub_msg, allowed_mentions=AllowedMentions.none())

    # TODO: 問題を1日5個増やす
    @staticmethod
    def get_question(level):
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
                              description=f'ちなみに...\n```\n{q[2]}\n```',
                              color=261888)
                return await q_msg.edit(embed=a_msg)
            else:
                w_msg = Embed(title='残念！不正解',
                              description=f'答え：{q[1]}\n\nちなみに...\n```\n{q[2]}\n```',
                              color=15409787)
                return await q_msg.edit(embed=w_msg)

    @marubatu.command(name='e')
    async def sub_e(self, ctx):
        q = self.get_question('easy')
        q_embed = Embed(title=f'{ctx.author} さんの問題',
                        description=f'難易度 - 簡単```\n{q[0]}\n```\n⭕ か ❌ か。',
                        color=2263275)  # カラー:水色
        await self.send_question(ctx, q_embed, q)

    @marubatu.command(name='n')
    async def sub_n(self, ctx):
        q = self.get_question('normal')
        q_embed = Embed(title=f'{ctx.author} さんの問題',
                        description=f'難易度 - 普通\n```\n{q[0]}\n```\n⭕ か ❌ か。',
                        color=15449378)  # カラー:暗め黄色
        await self.send_question(ctx, q_embed, q)

    @marubatu.command(name='h')
    async def sub_h(self, ctx):
        q = self.get_question('hard')
        q_embed = Embed(title=f'{ctx.author} さんの問題',
                        description=f'難易度 - 難しい\n```\n{q[0]}\n```\n⭕ か ❌ か。',
                        color=15409787)
        await self.send_question(ctx, q_embed, q)

    @commands.command(description='サイコロを振ります')
    async def dice(self, ctx):
        image = {
            'dice_1': 'https://cdn.discordapp.com/attachments/867004595079479296/867004682983047169/dice_1.jpg',
            'dice_2': 'https://cdn.discordapp.com/attachments/867004595079479296/867004694625648650/dice_2.jpg',
            'dice_3': 'https://cdn.discordapp.com/attachments/867004595079479296/867004690960482314/dice_3.jpg',
            'dice_4': 'https://cdn.discordapp.com/attachments/867004595079479296/867004690175492096/dice_4.jpg',
            'dice_5': 'https://cdn.discordapp.com/attachments/867004595079479296/867004688132997130/dice_5.jpg',
            'dice_6': 'https://cdn.discordapp.com/attachments/867004595079479296/867004685352042516/dice_6.jpg'
        }

        des_text = ['コロコロコロ...\n> **[dice]**', 'コロコロコロ...\n転がってゆく\n> **[dice]**',
                    'コロ..コロ..コロ..\nまだ転がる\n> **[dice]**']
        dice_embed = Embed(title='サイコロ')
        dice_embed.set_thumbnail(url=image['dice_1'])
        dice_msg = await ctx.reply(embed=dice_embed, allowed_mentions=AllowedMentions.none())
        await asyncio.sleep(2)
        for t in des_text:
            random_int = random.randint(1, 6)
            edit_embed = Embed(title='サイコロ',
                               description=t.replace('[dice]', f'{random_int}'))
            edit_embed.set_thumbnail(url=image[f'dice_{random_int}'])
            await dice_msg.edit(embed=edit_embed)
            await asyncio.sleep(1.5)

        random_int = random.randint(1, 6)
        edit_embed = Embed(title='サイコロ',
                           description=f'結果！！ \n> **{random_int}** が出ました！')
        edit_embed.set_thumbnail(url=image[f'dice_{random_int}'])
        await dice_msg.edit(embed=edit_embed)


def setup(bot):
    bot.add_cog(Game(bot))
