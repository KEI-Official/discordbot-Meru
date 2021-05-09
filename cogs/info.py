import discord
from discord.ext import commands


class Info(commands.Cog):
    """Info関連コマンド"""
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Info(bot))
