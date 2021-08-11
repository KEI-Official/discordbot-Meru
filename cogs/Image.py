from discord.ext import commands
from discord import Embed, AllowedMentions
import requests
import os

from libs import check_permission


class Image(commands.Cog):
    """主に画像検索のコマンドがあるカテゴリーです"""

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def get_image(ctx, endpoint: str):
        res = requests.get(f'https://neko-love.xyz/api/v1/{endpoint}')
        res_data = res.json()
        if res.status_code == 200:
            embed_msg = Embed()
            embed_msg.set_image(url=res_data['url'])
            embed_msg.set_footer(text='Powered By neko-love.xyz')
            return await ctx.reply(embed=embed_msg, allowed_mentions=AllowedMentions.none())
        else:
            none_msg = Embed(description='Image is None.')
            return await ctx.reply(embed=none_msg, allowed_mentions=AllowedMentions.none())

    @check_permission([])
    @commands.command(description='nekoの画像をランダムに表示します')
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def neko(self, ctx):
        await self.get_image(ctx, 'neko')

    @check_permission([])
    @commands.command(description='kitsuneの画像をランダムに表示します',
                      aliases=['kitune'])
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def kitsune(self, ctx):
        await self.get_image(ctx, 'kitsune')

    @check_permission([])
    @commands.command(description='イヌの画像をランダムに表示します')
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def dog(self, ctx):
        res = requests.get('https://dog.ceo/api/breeds/image/random')
        res_data = res.json()
        if res.status_code == 200:
            embed_msg = Embed()
            embed_msg.set_image(url=res_data['message'])
            embed_msg.set_footer(text='Powered By dog.ceo')
            return await ctx.reply(embed=embed_msg, allowed_mentions=AllowedMentions.none())
        else:
            none_msg = Embed(description='Image is None.')
            return await ctx.reply(embed=none_msg, allowed_mentions=AllowedMentions.none())

    @check_permission([])
    @commands.command(description='指定されたキーワードのGIF画像をGIPHY上から検索します',
                      usage='[キーワード]',
                      aliases=['sgif', 'searchgif', 'find_gif', 'findgif'],
                      brief=['【コマンド例】\n'
                             '{cmd}search_gif 夜景'])
    async def search_gif(self, ctx, *keyword: str):
        giphy_key = os.getenv('GIPHY_KEY')
        if not keyword:
            no_key_msg = Embed(description='検索するGIF画像のキーワードを指定してください')
            await ctx.reply(embed=no_key_msg, allowed_mentions=AllowedMentions.none())
        else:
            keyword_text = ' '.join(keyword)
            data = {
                'api_key': giphy_key,
                'q': keyword_text,
                'lang': 'ja'
            }
            res_giphy = requests.get(
                'https://api.giphy.com/v1/gifs/search',
                params=data
            )
            status = res_giphy.status_code
            re_data = res_giphy.json()

            if status != 200:
                api_err_msg = Embed(title=f'APIエラー - {status}',
                                    description=f'エラーメッセージ\n```\n{re_data["message"]}\n```\n'
                                                '解決できない際はお手数ですが、公式サーバーまでお越しください。')
                await ctx.reply(embed=api_err_msg, allowed_mentions=AllowedMentions.none())
            else:
                if not re_data["data"]:
                    no_image_msg = Embed(title='GIPHY - GIF画像検索ツール',
                                         description='GIF画像が見つかりませんでした')
                    no_image_msg.set_author(name='GIPHY', url='https://giphy.com/')
                    await ctx.reply(embed=no_image_msg, allowed_mentions=AllowedMentions.none())
                else:
                    image = re_data["data"][0]
                    res_image = Embed(title='GIPHY - GIF画像検索ツール',
                                      description=f'総Hit数: {re_data["pagination"]["total_count"]}'
                                                  '\nダウンロードする際はライセンスをよくお読みください')
                    res_image.set_author(name='GIPHY - ImageLink', url=image["url"])
                    res_image.add_field(name='タイトル', value=f'{image["title"] if "" else "No title"}')
                    res_image.set_image(url=image["images"]["original"]["url"])
                    try:
                        res_image.add_field(name='アップロードユーザー',
                                            value=f'[{image["user"]["display_name"]}]({image["user"]["profile_url"]})')
                        res_image.set_footer(text=f'インポート日時: {image["import_datetime"]}',
                                             icon_url=image["user"]["avatar_url"])
                    except KeyError:
                        res_image.add_field(name='アップロードユーザー', value='No User')
                        res_image.set_footer(text=f'インポート日時: {image["import_datetime"]}')

                    return await ctx.reply(embed=res_image, allowed_mentions=AllowedMentions.none())


def setup(bot):
    bot.add_cog(Image(bot))
