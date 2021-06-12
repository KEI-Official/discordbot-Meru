from discord.ext import commands
from discord import Embed, AllowedMentions
import requests


class Image(commands.Cog):
    """Image関連のコマンド"""
    def __init__(self, bot):
        self.bot = bot

    async def get_image(self, ctx, endpoint: str):
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

    @commands.command(description='nekoの画像をランダムに表示します')
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def neko(self, ctx):
        await self.get_image(ctx, 'neko')

    @commands.command(description='kitsuneの画像をランダムに表示します',
                      aliases=['kitune'])
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def kitsune(self, ctx):
        await self.get_image(ctx, 'kitsune')

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


def setup(bot):
    bot.add_cog(Image(bot))
