from discord import Embed, AllowedMentions, utils, File
from discord.ext import commands
import requests
import random
import re
import os
import uuid
import json


class Utils(commands.Cog):
    """Utils関連コマンド"""
    def __init__(self, bot):
        self.bot = bot
        self.stage_info = None
        self.user_info = None
        self.avatar_url = None
        self.lang = None
        self.azure_endpoint = os.getenv('AZURE_ENDPOINT')
        self.azure_api_key = os.getenv('AZURE_API_KEY')
        self.azure_translate_key = os.getenv('AZURE_TRANS_KEY')
        self.azure_translate_endpoint = os.getenv('AZURE_TRANS_ENDPOINT')

    @commands.command(description='ユーザーのアイコンを表示します',
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

    @commands.command(description='送られた文字を指定された言語に翻訳します',
                      usage='[翻訳先言語 | <-list>] [翻訳する文章]',
                      aliases=['trans'])
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def translate(self, ctx, tolang=None, translate_text=None):

        with open('./data/translate_lang_list.json', 'r', encoding='UTF-8') as lang_list:
            data = json.load(lang_list)

        if tolang is None:
            no_lang_msg = Embed(description='翻訳先の言語を指定してください')
            return await ctx.reply(embed=no_lang_msg, allowed_mentions=AllowedMentions.none())

        elif tolang == '--list':
            return await ctx.reply(file=File('./data/lang_list.md'), allowed_mentions=AllowedMentions.none())

        elif translate_text is None:
            no_text_msg = Embed(description='翻訳する文章を送信してください')
            return await ctx.reply(embed=no_text_msg, allowed_mentions=AllowedMentions.none())

        else:
            if tolang in data:
                load_emoji = self.bot.get_emoji(852849151628935198)
                await_msg = await ctx.reply(embed=Embed(description=f'{load_emoji} 翻訳中です...'),
                                            allowed_mentions=AllowedMentions.none())
                params = '&to=' + tolang
                constructed_url = f'{self.azure_translate_endpoint}/translate?api-version=3.0{params}'
                headers = {
                    'Ocp-Apim-Subscription-Key': f'{self.azure_translate_key}',
                    'Ocp-Apim-Subscription-Region': 'japaneast',
                    'Content-type': 'application/json',
                    'X-ClientTraceId': str(uuid.uuid4())
                }
                body = [{
                    'text': f'{translate_text}'
                }]
                request = requests.post(constructed_url, headers=headers, json=body)
                response = request.json()
                trans_done = Embed(title='翻訳結果',
                                   description=f'```\n{response[0]["translations"][0]["text"]}\n```')
                trans_done.add_field(name='翻訳前言語', value=f'{data[response[0]["detectedLanguage"]["language"]]}')
                trans_done.add_field(name='翻訳先言語', value=f'{data[tolang]}')
                return await await_msg.edit(embed=trans_done, allowed_mentions=AllowedMentions.none())
            else:
                lang_none = Embed(title='翻訳言語エラー',
                                  description=f'指定された言語が見つかりませんでした\n'
                                              f'言語リストは、`{self.bot.command_prefix}translate --list` で見ることが出来ます')
                return await ctx.reply(embed=lang_none, allowed_mentions=AllowedMentions.none())

    @commands.command(description='ユーザーのアイコンを表示します',
                      usage='<User ID/名前/メンション>')
    async def avatar(self, ctx, user=None):
        if user is None:
            self.avatar_url = f'{ctx.author.avatar_url}'.replace('1024', '128')
            self.user_info = ctx.author
        elif ctx.message.mentions:
            self.user_info = ctx.message.mentions[0]
            self.avatar_url = f'{self.user_info.avatar_url}'.replace('1024', '128')
        elif re.search(r'[0-9]{18}', str(user)) is not None:
            pre_user = ctx.guild.get_member(int(user))
            if pre_user:
                self.user_info = pre_user
                self.avatar_url = f'{self.user_info.avatar_url}'.replace('1024', '128')
            else:
                no_user_msg = Embed(description='ユーザーが見つかりませんでした\n**考えられる原因**```'
                                                '\n・IDは間違っていませんか？\n・ユーザーはサーバーにいますか？\n```')
                return await ctx.reply(embed=no_user_msg, allowed_mentions=AllowedMentions.none())
        else:
            pre_user = utils.get(ctx.guild.members, name=user)
            if pre_user:
                self.user_info = pre_user
                self.avatar_url = f'{self.user_info.avatar_url}'.replace('1024', '128')
            else:
                no_user_msg = Embed(description='ユーザーが見つかりませんでした\n**考えられる原因**```'
                                                '\n・名前は間違っていませんか？\n・ユーザーはサーバーにいますか？\n```')
                return await ctx.reply(embed=no_user_msg, allowed_mentions=AllowedMentions.none())

        avatar_png_url = self.avatar_url.replace('webp', 'png')
        avatar_jpg_url = self.avatar_url.replace('webp', 'jpg')
        avatar_jpeg_url = self.avatar_url.replace('webp', 'jpeg')
        embed = Embed(description=f'[webp]({self.avatar_url}) | [png]({avatar_png_url}) | '
                                  f'[jpg]({avatar_jpg_url}) | [jpeg]({avatar_jpeg_url})')
        embed.set_author(name=f'{self.user_info}')
        embed.set_image(url=self.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(description='指定された画像の文字をおこして、送信します',
                      usage='[画像URL | 画像を添付する] ',
                      aliases=['iw', 'imageword'])
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def image_word(self, ctx, url=None):
        if url is None:
            no_image_msg = Embed(description='画像URLを指定してください')
            await ctx.reply(embed=no_image_msg, allowed_mentions=AllowedMentions.none())
        else:
            params = {'visualFeatures': 'Categories,Description,Color'}

            if url is not None:
                headers = {
                    'Ocp-Apim-Subscription-Key': self.azure_api_key,
                    'Content-Type': 'application/json',
                }
                data = {'url': url}
                response = requests.post(
                    self.azure_endpoint,
                    headers=headers,
                    params=params,
                    json=data
                )

            status = response.status_code
            data = response.json()

            if status != 200:

                if data['error']['code'] == 'InvalidImageSize':
                    text = '画像のサイズが大きすぎます\n50MB以下のものを指定してください。'

                elif data['error']['code'] == 'InvalidImageURL':
                    text = 'この画像URLからは取得できません\nURLを確認してください。'

                elif data['error']['code'] == 'UnsupportedImageFormat':
                    text = '対応していない画像形式です\n\n対応拡張子\n```\n・JPEG\n・PNG\n・BMP\n```'

                elif data['error']['code'] == 'InvalidImageDimension':
                    text = '入力画像の大きさが範囲外です\n```\n最小: 50x50 ピクセル\n最大: 10000x10000 ピクセル\n```'
                else:
                    text = '予期しないエラーが発生しました'

                err_msg = Embed(title='APIエラー', description=text)
                return await ctx.reply(embed=err_msg, allowed_mentions=AllowedMentions.none())

            text = ''
            for region in data['regions']:
                for line in region['lines']:
                    for word in line['words']:
                        text += word.get('text', '')
                        if data['language'] != 'ja':
                            text += ' '
                text += '\n'

            if len(text) == 0:
                text += '文字が検出できませんでした'

            su_msg = Embed(title='文字認識 - 結果', description=f'```\n{text}\n```')
            return await ctx.reply(embed=su_msg, allowed_mentions=AllowedMentions.none())


def setup(bot):
    bot.add_cog(Utils(bot))
