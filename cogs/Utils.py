import asyncio
import datetime
import io
import json
import os
import uuid

from discord import Embed, AllowedMentions, File, TextChannel, VoiceChannel, Member
from discord.ext import commands
import requests


class Utils(commands.Cog):
    """ユーザー向けのさまざまなコマンドがあるカテゴリーです"""

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
        self.bitly_key = os.getenv('BITLY_KEY')

    @commands.command(description='送られた文字を指定された言語に翻訳します',
                      usage='[翻訳先言語 | <-list>] [翻訳する文章]',
                      aliases=['trans'],
                      brief=['【実行例】\n'
                             '・言語リスト: {cmd}translate -list\n'
                             '・翻訳: {cmd}translate ja Hello!'])
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def translate(self, ctx, tolang=None, *translate_text) -> None:

        with open('./data/translate_lang_list.json', 'r', encoding='UTF-8') as lang_list:
            data = json.load(lang_list)

        if tolang is None:
            no_lang_msg = Embed(description='翻訳先の言語を指定してください')
            return await ctx.reply(embed=no_lang_msg, allowed_mentions=AllowedMentions.none())

        elif tolang == '--list':
            return await ctx.reply(file=File('./data/lang_list.md'), allowed_mentions=AllowedMentions.none())

        elif not translate_text:
            no_text_msg = Embed(description='翻訳する文章を送信してください')
            return await ctx.reply(embed=no_text_msg, allowed_mentions=AllowedMentions.none())

        else:
            if tolang in data:
                t_text = ' '.join(translate_text)
                if len(t_text) > 1000:
                    long_text_msg = Embed(description='翻訳する文章は1000文字以内に収めてください')
                    return await ctx.reply(embed=long_text_msg, allowed_mentions=AllowedMentions.none())
                else:
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
                        'text': f'{t_text}'
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
                      usage='<User ID/名前/メンション>',
                      aliases=['icon'])
    async def avatar(self, ctx, user: Member = None):
        if user is None:
            self.avatar_url = f'{ctx.author.avatar_url}'.replace('1024', '128')
            self.user_info = ctx.author
        else:
            self.avatar_url = f'{user.avatar_url}'.replace('1024', '128')
            self.user_info = user

        avatar_png_url = self.avatar_url.replace('webp', 'png')
        avatar_jpg_url = self.avatar_url.replace('webp', 'jpg')
        avatar_jpeg_url = self.avatar_url.replace('webp', 'jpeg')
        embed = Embed(description=f'[webp]({self.avatar_url}) | [png]({avatar_png_url}) | '
                                  f'[jpg]({avatar_jpg_url}) | [jpeg]({avatar_jpeg_url})')
        embed.set_author(name=f'{self.user_info}')
        embed.set_image(url=self.avatar_url)
        await ctx.reply(embed=embed, allowed_mentions=AllowedMentions.none())

    @commands.command(description='指定された画像の文字をおこして、送信します',
                      usage='[画像URL] ',
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

    @commands.command(description='指定されたURLの短縮リンクを作成します。',
                      usage='[短縮するURL]',
                      aliases=['surl', 'shurl', 'shorturl'])
    async def short_url(self, ctx, url=None):
        if url is None:
            no_url_msg = Embed(description='短縮するURLを指定してください')
            await ctx.reply(embed=no_url_msg, allowed_mentions=AllowedMentions.none())
        elif not url.startswith('https://') or url.startswith('http://'):
            no_url_type = Embed(description='URLの形式で指定してください')
            await ctx.reply(embed=no_url_type, allowed_mentions=AllowedMentions.none())
        else:

            headers = {
                'Authorization': f'Bearer {self.bitly_key}',
                'Content-Type': 'application/json',
            }
            data = {'long_url': f'{url}'}
            response = requests.post(
                'https://api-ssl.bitly.com/v4/shorten',
                headers=headers,
                json=data
            )
            status = response.status_code
            re_data = response.json()

            if status != 200:
                try:
                    api_err_msg = Embed(title=f'APIエラー - {status}',
                                        description=f'エラーメッセージ\n```\n{re_data.get("errors")[0]["message"]}\n```')
                    await ctx.reply(embed=api_err_msg, allowed_mentions=AllowedMentions.none())
                except Exception:
                    return
            else:
                await ctx.reply('短縮URLを作成しました', allowed_mentions=AllowedMentions.none())
                await ctx.reply(f'`{re_data["link"]}`', allowed_mentions=AllowedMentions.none())

    @commands.command(description='指定されたキーワードの画像をPixaBay上から検索します',
                      usage='[キーワード]',
                      aliases=['simage', 'pixabay', 's_image'],
                      brief=['【実行例】\n'
                             '{cmd}search_image 東京'])
    async def search_image(self, ctx, *keyword: str) -> None:
        pixabay_key = os.getenv('PIXABAY_KEY')
        if not keyword:
            no_key_msg = Embed(description='検索する画像のキーワードを指定してください')
            await ctx.reply(embed=no_key_msg, allowed_mentions=AllowedMentions.none())
        else:
            keyword_text = '+'.join(keyword)
            data = {
                'key': pixabay_key,
                'q': keyword_text,
                'lang': 'ja'
            }
            res_pixabay = requests.get(
                'https://pixabay.com/api/',
                params=data
            )
            status = res_pixabay.status_code
            re_data = res_pixabay.json()

            if status != 200:
                api_err_msg = Embed(title=f'APIエラー - {status}',
                                    description=f'エラーメッセージ\n```\n{re_data["errors"][0]["message"]}\n```')
                await ctx.reply(embed=api_err_msg, allowed_mentions=AllowedMentions.none())
            else:
                if not re_data["hits"]:
                    no_image_msg = Embed(title='PixaBay - 画像検索ツール',
                                         description='画像が見つかりませんでした')
                    no_image_msg.set_author(name='PixaBay', url='https://pixabay.com/ja/')
                    await ctx.reply(embed=no_image_msg, allowed_mentions=AllowedMentions.none())
                else:
                    image = re_data["hits"][0]
                    related_images = []
                    related_image_text = ''
                    for num in range(1, 6):
                        try:
                            related_images.append(f'[{num}枚目]({re_data["hits"][num]["pageURL"]})')
                        except IndexError:
                            pass
                    if not related_images:
                        related_image_text += 'なし'
                    else:
                        related_image_text += ' | '.join(related_images)

                    res_image = Embed(title='PixaBay - 画像検索ツール',
                                      description=f'総Hit数: {re_data["total"]}\nダウンロードする際はライセンスをよくお読みください')
                    res_image.add_field(name='総閲覧数', value=f'{image["views"]} 回')
                    res_image.add_field(name='総ダウンロード数', value=f'{image["downloads"]} 回')
                    res_image.add_field(name='関連画像', value=related_image_text, inline=False)
                    res_image.set_image(url=image["webformatURL"])
                    res_image.set_author(name='PixaBay', url=image["pageURL"])
                    res_image.set_footer(text=f'👍: {image.get("likes") if image.get("likes") else "0"} | '
                                              f'💬: {image.get("comments") if image.get("comments") else "0"}')
                    return await ctx.reply(embed=res_image, allowed_mentions=AllowedMentions.none())

    @commands.command(description='見ることが出来るチャンネルの一覧を表示します',
                      aliases=['chlist', 'ch_tree', 'chtree']
                      )
    async def ch_list(self, ctx):
        ches = ctx.guild.channels

        user_deny_ch = []
        for channel in ches:
            ch_perm = channel.permissions_for(ctx.author)
            deny_perm = [str(perm) for perm, b in dict(ch_perm).items() if not b]
            if 'read_messages' in deny_perm:
                user_deny_ch.append(channel)

        all_list = ctx.guild.by_category()
        if not user_deny_ch:
            pass
        else:
            for ch in user_deny_ch:
                for a, b in all_list:
                    if ch in b:
                        b.remove(ch)
        allow_ch_list = []

        for category, ch_list in all_list:
            if category:
                allow_ch_list.append(f'C# {category.name}')
            for ch in ch_list:
                if isinstance(ch, TextChannel):
                    allow_ch_list.append(f'　T# {ch.name}')
                elif isinstance(ch, VoiceChannel):
                    allow_ch_list.append(f'　V# {ch.name}')

        text = '\n'.join(allow_ch_list)

        if len(text) > 1000:
            send_msg = await ctx.reply(
                '閲覧できるチャンネルリスト',
                file=File(
                    io.StringIO(text),
                    f'ChannelTree-{datetime.datetime.utcnow().timestamp()}.txt',
                ),
                allowed_mentions=AllowedMentions.none()
            )
        else:
            send_embed = Embed(title='閲覧できるチャンネルリスト',
                               description=f'```\n{text}\n```')
            send_msg = await ctx.reply(embed=send_embed, allowed_mentions=AllowedMentions.none())

        await send_msg.add_reaction('🗑')

        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == '🗑') and reaction.message.channel == ctx.channel
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
        except asyncio.TimeoutError:
            await send_msg.clear_reactions()
        else:
            if str(reaction.emoji) == '🗑':
                await send_msg.clear_reactions()
                await send_msg.delete()

    @commands.group(description='テキストにタグを付けることができます',
                    usage='[タグ名] / [add/remove] [タグ名] / [list]',
                    brief=['【実行例】\n'
                           '・検索: {cmd}tag タグ名\n'
                           '・追加/削除: {cmd}tag add/remove タグ名\n'
                           '・一覧: {cmd}tag list'])
    async def tag(self, ctx):
        if ctx.invoked_subcommand is None:
            res = self.bot.db.user_tag_get(ctx.author.id, ctx.subcommand_passed)
            if res:
                return await ctx.reply(res[0][0], allowed_mentions=AllowedMentions.none())
            else:
                return await ctx.reply('見つかりませんでした', allowed_mentions=AllowedMentions.none())

    @tag.command(description='テキストにタグを追加します')
    async def add(self, ctx, tag_name=None, *, context=None):
        if not tag_name or not context:
            return await ctx.reply('追加するタグの名前又は内容を記入してください', allowed_mentions=AllowedMentions.none())
        elif tag_name in ['add', 'remove', 'list']:
            return await ctx.reply('タグの名前にサブコマンド名は利用できません', allowed_mentions=AllowedMentions.none())
        else:
            res = self.bot.db.user_tag_set(ctx.author.id, tag_name, context)
            if res:
                return await ctx.reply('追加しました', allowed_mentions=AllowedMentions.none())

    @tag.command(description='テキストについているタグを削除します')
    async def remove(self, ctx, tag_name=None):
        if not tag_name:
            return await ctx.reply('削除するタグの名前を記入してください', allowed_mentions=AllowedMentions.none())

        res = self.bot.db.user_tag_del(ctx.author.id, tag_name)
        if res:
            return await ctx.reply('削除しました', allowed_mentions=AllowedMentions.none())

    @tag.command(description='追加したタグの一覧を表示します')
    async def list(self, ctx):
        res = self.bot.db.user_tag_all_get(ctx.author.id)
        if not res:
            no_tag = Embed(title='Tag List', description='何も追加されていません')
            no_tag.set_footer(text=f'{ctx.author}')
            return await ctx.reply(embed=no_tag, allowed_mentions=AllowedMentions.none())
        else:
            user_data_list = []
            count = 1
            for data in res:
                user_data_list.append(f'{count}. {data[1]}: {data[2]}')
                count += 1
            tag_list = Embed(title='Tag List',
                             description='```\n{}\n```'.format('\n'.join(user_data_list)))
            tag_list.set_footer(text=f'{ctx.author}')
            return await ctx.reply(embed=tag_list, allowed_mentions=AllowedMentions.none())


def setup(bot):
    bot.add_cog(Utils(bot))
