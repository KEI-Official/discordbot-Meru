import discord
from discord.ext import commands


class Game(commands.Cog):
    """Game関連コマンド"""
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Game(bot))
