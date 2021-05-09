import discord
from discord.ext import commands


class Utils(commands.Cog):
    """Utils関連コマンド"""
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Utils(bot))
