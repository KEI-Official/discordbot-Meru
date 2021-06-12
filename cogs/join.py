from discord import Embed
from discord.ext import commands
from pytz import timezone
from datetime import datetime


class Join(commands.Cog):
    """入室時"""
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = int(self.bot.config['log_channel_id'])

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = await self.bot.fetch_channel(self.log_channel_id)

        if channel:
            datetime_now = datetime.now().astimezone(timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")
            datetime_jst = guild.created_at.astimezone(timezone("Asia/Tokyo"))
            value_text = f'```\nサーバー人数: {len(guild.members)}\nチャンネル数: {len(guild.channels)}\n' \
                         f'サーバー作成日: {datetime_jst.strftime("%Y/%m/%d %H:%M:%S")}\nオーナーさん: {guild.owner}\n```'

            join_msg = Embed(title=f'{self.bot.user}を導入してもらいました',
                             description=f'サーバー名: {guild.name} ({guild.id})')
            join_msg.add_field(name='サーバー情報', value=value_text)
            join_msg.set_footer(text=f'{datetime_now}')

            return await channel.send(embed=join_msg)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 574802637598228480:
            member_role = member.guild.get_role(601283421310025729)
            bot_role = member.guild.get_role(601284694205792276)
            if member_role:
                if member.bot:
                    await member.add_roles(member_role)
                else:
                    await member.add_roles(bot_role)


def setup(bot):
    bot.add_cog(Join(bot))
