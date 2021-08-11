import asyncio
import os
import random
import json
import requests

from discord.ext import commands
from discord import Embed, AllowedMentions

from libs import check_permission


class Game(commands.Cog):
    """トレーニングといったお遊び系のコマンドがあるカテゴリーです"""
    def __init__(self, bot):
        self.bot = bot
        self.stage_info = None
        self.s_endpoint = 'https://stat.ink/api/v2'
        self.spla_api_key = os.getenv('SPLATOON2_KEY')

    @commands.command(description='Splatoon2のステージ情報を取得します',
                      usage='[対戦ルールタイプ] <-n(次の時間帯)>')
    async def spla2(self, ctx, s_type=None, s_next=None):
        def get_stage(game, time_next: bool):
            if game == 'regular':
                if time_next:
                    res = requests.get('https://spla2.yuu26.com/regular/next')
                    return res.json()['result'][0]
                else:
                    res = requests.get('https://spla2.yuu26.com/regular/now')
                    return res.json()['result'][0]
            elif game == 'gachi':
                if time_next:
                    res = requests.get('https://spla2.yuu26.com/gachi/next')
                    return res.json()['result'][0]
                else:
                    res = requests.get('https://spla2.yuu26.com/gachi/now')
                    return res.json()['result'][0]
            elif game == 'league':
                if time_next:
                    res = requests.get('https://spla2.yuu26.com/league/next')
                    return res.json()['result'][0]
                else:
                    res = requests.get('https://spla2.yuu26.com/league/now')
                    return res.json()['result'][0]
            elif game == 'coop':
                if time_next:
                    res = requests.get('https://spla2.yuu26.com/coop/schedule')
                    return res.json()['result'][1]
                else:
                    res = requests.get('https://spla2.yuu26.com/coop/schedule')
                    return res.json()['result'][0]

        if s_type is None:
            no_type_msg = Embed(description='ステージ情報のタイプ(r, g, l, s)を指定してください\n'
                                            '```r: レギュラーマッチ\ng: ガチマッチ\nl: リーグマッチ\ns: サーモンラン```')
            await ctx.reply(embed=no_type_msg, allowed_mentions=AllowedMentions.none())
        elif s_type == 'r':
            if s_next is None:
                self.stage_info = get_stage('regular', False)
            elif s_next == '-n':
                self.stage_info = get_stage('regular', True)

            stage_info = self.stage_info
            rule_name = stage_info["rule"]
            stage = f'・{stage_info["maps"][0]}\n・{stage_info["maps"][1]}'
            s_t = str(stage_info['start']).replace('-', '/', 2).replace('T', ' | ')
            e_t = str(stage_info['end']).replace('-', '/', 2).replace('T', ' | ')
            image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

            de_msg = f'**ルール**\n```\n{rule_name}```\n**ステージ**\n```\n{stage}\n```\n' \
                     f'**時間帯**\n```\nSTART: {s_t}\nEND: {e_t}\n```'
            embed = Embed(title='Splatoon2 ステージ情報 | レギュラーマッチ',
                          description=de_msg,
                          color=261888)  # カラー:ライトグリーン)
            embed.set_image(url=image_url)
            await ctx.reply(embed=embed, allowed_mentions=AllowedMentions.none())

        elif s_type == 'g':
            if s_next is None:
                self.stage_info = get_stage('gachi', False)
            elif s_next == '-n':
                self.stage_info = get_stage('gachi', True)

            stage_info = self.stage_info
            rule_name = stage_info["rule"]
            stage = f'・{stage_info["maps"][0]}\n・{stage_info["maps"][1]}'
            s_t = str(stage_info['start']).replace('-', '/', 2).replace('T', ' | ')
            e_t = str(stage_info['end']).replace('-', '/', 2).replace('T', ' | ')
            image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

            de_msg = f'**ルール**\n```\n{rule_name}\n```\n**ステージ**\n```\n{stage}\n```\n' \
                     f'**時間帯**\n```\nSTART: {s_t}\nEND: {e_t}\n```'
            embed = Embed(title='Splatoon2 ステージ情報 | ガチマッチ',
                          description=de_msg,
                          color=14840346)  # カラー:オレンジ
            embed.set_image(url=image_url)
            await ctx.reply(embed=embed, allowed_mentions=AllowedMentions.none())

        elif s_type == 'l':
            if s_next is None:
                self.stage_info = get_stage('league', False)
            elif s_next == '-n':
                self.stage_info = get_stage('league', True)

            stage_info = self.stage_info
            rule_name = stage_info["rule"]
            stage = f'・{stage_info["maps"][0]}\n・{stage_info["maps"][1]}'
            s_t = str(stage_info['start']).replace('-', '/', 2).replace('T', ' | ')
            e_t = str(stage_info['end']).replace('-', '/', 2).replace('T', ' | ')
            image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

            de_msg = f'**ルール**\n```\n{rule_name}\n```\n**ステージ**\n```\n{stage}\n```\n' \
                     f'**時間帯**\n```\nSTART: {s_t}\nEND: {e_t}\n```'
            embed = Embed(title='Splatoon2 ステージ情報 | リーグマッチ',
                          description=de_msg,
                          color=15409787)  # カラー:ピンク
            embed.set_image(url=image_url)
            await ctx.reply(embed=embed, allowed_mentions=AllowedMentions.none())

        elif s_type == 's':
            if s_next is None:
                self.stage_info = get_stage('coop', False)
            elif s_next == '-n':
                self.stage_info = get_stage('coop', True)

            stage_info = self.stage_info
            stage = stage_info["stage"]["name"]
            image_url = stage_info['stage']['image']
            s_t = str(stage_info['start']).replace('-', '/', 2).replace('T', ' | ')
            e_t = str(stage_info['end']).replace('-', '/', 2).replace('T', ' | ')
            weapons = ''
            for we in stage_info['weapons']:
                weapons += f'・{we["name"]}\n'

            de_msg = f'**ステージ**\n```\n{stage}\n```\n**支給ブキ**\n```\n{weapons}```\n' \
                     f'**時間帯**\n```\nSTART: {s_t}\nEND: {e_t}\n```'
            embed = Embed(title='Splatoon2 ステージ情報 | サーモンラン',
                          description=de_msg,
                          color=15442812)  # カラー:薄橙
            embed.set_image(url=image_url)
            await ctx.reply(embed=embed, allowed_mentions=AllowedMentions.none())

    @check_permission([])
    @commands.group(description='Splatoon2のいろんな情報を取得します',
                    usage='[取得キー] <find/f> <su=名前/sp=名前>',
                    aliases=['splainfo', 'sp-info', 'spinfo'],
                    brief=['【取得キーリスト】we: ブキ\n'
                           '【絞り込み検索】su=名前: サブウェポン, sp=名前: スペシャル\n'
                           '【実行例】\n'
                           '・ブキリスト: {cmd}spinfo we f sp=ナイスダマ\n'
                           '・ブキリスト: {cmd}spinfo we f su=クイックボム']
                    )
    async def spla_info(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @check_permission([])
    @spla_info.command()
    async def we(self, ctx, search=None, name=None):
        endpoint = f'{self.s_endpoint}/weapon'
        num_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        if search is None:
            response = requests.get(endpoint)
            status = response.status_code
            res_data = response.json()
            if status != 200:
                print(res_data)
            else:
                des_msg = []
                we_list = {'shooter': 'シューター', 'blaster': 'ブラスター', 'reelgun': 'リールガン', 'maneuver': 'マニューバー',
                           'roller': 'ローラー', 'brush': 'フデ', 'charger': 'チャージャー', 'slosher': 'スロッシャー',
                           'splatling': 'スピナー', 'brella': 'シェルター'}
                for num in range(len(we_list)):
                    des_msg.append(f'{num_list[num]} : {we_list[list(we_list)[int(num)]]}')
                msg_embed = Embed(title='武器リスト',
                                  description='武器の種類を選んでください\n\n{}'.format('\n'.join(des_msg)))

                def check(reaction, user):
                    return user == ctx.author and (str(reaction.emoji) in num_list or str(reaction.emoji) == '⏹') \
                           and reaction.message.channel == ctx.channel

                def check_2(reaction, user):
                    return user == ctx.author and (str(reaction.emoji) == '◀' or str(reaction.emoji) == '⏹') \
                           and reaction.message.channel == ctx.channel

                def get_weapon(emoji):
                    e_n = num_list.index(emoji)
                    weapon_type = list(we_list)[e_n]
                    weapon_list = []
                    for data in res_data:
                        if data['type']['key'] == weapon_type:
                            w_name = data['name']['ja_JP']
                            w_sp = data['special']['name']['ja_JP']
                            weapon_list.append(f'・{w_name} ({w_sp})')
                    return weapon_list, we_list[list(we_list)[int(num)]]

                while_msg = True
                while while_msg:
                    msg = await ctx.reply(embed=msg_embed, allowed_mentions=AllowedMentions.none())
                    for num in range(len(we_list)):
                        await msg.add_reaction(num_list[num])
                    await msg.add_reaction('⏹')
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                    except asyncio.TimeoutError:
                        await msg.clear_reactions()
                        while_msg = False
                    else:
                        await msg.clear_reactions()
                        if str(reaction.emoji) == '⏹':
                            await msg.edit(embed=Embed(description='終了しました'))
                            while_msg = False
                        else:
                            we_r, we_t = get_weapon(str(reaction.emoji))
                            we_msg = Embed(title=f'{we_t} の一覧', description='```\n{}\n```'.format('\n'.join(we_r)))
                            await msg.edit(embed=we_msg)
                            await msg.add_reaction('◀')
                            await msg.add_reaction('⏹')
                            try:
                                reaction_2, user_2 = await self.bot.wait_for('reaction_add', timeout=60, check=check_2)
                            except asyncio.TimeoutError:
                                await msg.clear_reactions()
                                while_msg = False
                            else:
                                if str(reaction_2.emoji) == '◀':
                                    await msg.clear_reactions()
                                    await msg.delete()
                                    continue
                                elif str(reaction_2.emoji) == '⏹':
                                    await msg.clear_reactions()
                                    while_msg = False

        elif (search == 'find' and name is not None) or (search == 'f' and name is not None):
            if name.startswith('sp='):
                sp_name = name.replace('sp=', '')
                res = self.bot.splatoon.get_weapons('special', sp_name)
                if res is None:
                    await ctx.reply(embed=Embed(description='ブキが見つかりませんでした'), allowed_mentions=AllowedMentions.none())
                else:
                    re_embed = self.bot.splatoon.sort_weapons(sp_name, res)
                    await ctx.reply(embed=re_embed, allowed_mentions=AllowedMentions.none())
            elif name.startswith('su='):
                su_name = name.replace('su=', '')
                res = self.bot.splatoon.get_weapons('sub', su_name)
                if res is None:
                    await ctx.reply(embed=Embed(description='ブキが見つかりませんでした'), allowed_mentions=AllowedMentions.none())
                else:
                    re_embed = self.bot.splatoon.sort_weapons(su_name, res)
                    await ctx.reply(embed=re_embed, allowed_mentions=AllowedMentions.none())

    @check_permission([])
    @commands.command(description='三字熟語のトレーニングが出来ます')
    async def tt(self, ctx):
        with open("./data/tt_data.json", "r", encoding='UTF-8') as config:
            data = json.load(config)
        q = data[random.randint(1, 128)]

        question_embed = Embed(title=f'{ctx.author} さんの問題',
                               description=f'【 {q[0]} 】の読み方をひらがなで答えよ！',
                               color=2263275)
        q_msg = await ctx.reply(embed=question_embed, allowed_mentions=AllowedMentions.none())

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

    @check_permission([])
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

    @check_permission([])
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
