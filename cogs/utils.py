from discord import Embed, AllowedMentions
from discord.ext import commands
import requests
import random


class Utils(commands.Cog):
    """Utils関連コマンド"""
    def __init__(self, bot):
        self.bot = bot
        self.stage_info = None

    @commands.command()
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
            embed = Embed(title='Splatoon2 ステージ情報 | レギュラーマッチ', description=de_msg)
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)

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
            embed = Embed(title='Splatoon2 ステージ情報 | ガチマッチ', description=de_msg)
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)

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
            embed = Embed(title='Splatoon2 ステージ情報 | リーグマッチ', description=de_msg)
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)

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
            embed = Embed(title='Splatoon2 ステージ情報 | サーモンラン', description=de_msg)
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)

    @commands.command()
    async def translate(self, ctx, target_language, *, text: str) -> None:
        encode_length = len(text.encode('utf-8'))
        if encode_length > 1024:
            return await ctx.send('文字数が多すぎます。1024文字までで指定してください。')
        print(target_language, text)

        await ctx.send(f'翻訳結果：\n >>> {ctx}')


def setup(bot):
    bot.add_cog(Utils(bot))
