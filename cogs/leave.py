from discord import Embed
from discord.ext import commands
from pytz import timezone
from datetime import datetime


class Leave(commands.Cog):
    """退出時"""
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = int(self.bot.config['log_channel_id'])

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        channel = await self.bot.fetch_channel(self.log_channel_id)

        if channel:
            datetime_now = datetime.now().astimezone(timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")
            value_text = f'```\nサーバー名: {guild.name}\nオーナーさん: {guild.owner}\n```'

            leave_msg = Embed(title=f'{self.bot.user}が退出しました', description=f'サーバーから退出しました')
            leave_msg.add_field(name='サーバー情報', value=value_text)
            leave_msg.set_footer(text=f'{datetime_now}')

            return await channel.send(embed=leave_msg)


def setup(bot):
    bot.add_cog(Leave(bot))
