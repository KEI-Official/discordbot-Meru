import math
import sys
import discord
from discord.ext import commands


class Bot(commands.Cog):
    """Bot関連コマンド"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Botの応答速度を測ります')
    async def ping(self, ctx):
        await ctx.send(f'🏓 Pong! - {math.floor(self.bot.latency * 1000)} ms')

    @commands.command(description='BOTの招待リンクを出します')
    async def invite(self, ctx):
        pe = 0
        bid = 689713740316540979
        await ctx.send(f'招待リンクです\n'
                       f'https://discord.com/api/oauth2/authorize?client_id={str(bid)}&permissions={str(pe)}&scope=bot')

    @commands.command(description='BOTの情報を表示します')
    async def about(self, ctx):
        info_guilds = len(self.bot.guilds)
        info_user = len(self.bot.users)
        info_ch = 0
        for guild in self.bot.guilds:
            info_ch += len(guild.channels)
        oauth_url = 'https://discord.com/oauth2/authorize?client_id=702326747894644836&permissions=268528881&scope=bot'
        embed = discord.Embed(title=f'{self.bot.user}')
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name='開発者',
                        value=f'```c\n# discord: {(await self.bot.application_info()).owner}\n```',
                        inline=False)
        embed.add_field(name='開発言語',
                        value=f'```yml\nPython:\n{sys.version}\ndiscord.py: {discord.__version__}\n```',
                        inline=False)
        embed.add_field(name='Prefix',
                        value=f'```yml\n{self.bot.command_prefix}\n'
                              f'{self.bot.command_prefix}help でコマンドの説明を見ることが出来ます```',
                        inline=False)
        embed.add_field(name='詳細',
                        value=f'```yml\n[導入サーバー数] {info_guilds}\n[ユーザー数] {info_user}\n[チャンネル数] {info_ch}\n```',
                        inline=False)
        embed.add_field(name='一部機能の引用元',
                        value=f'・コマンド名「rtfm」: [Rapptz/RoboDanny](https://github.com/Rapptz/RoboDanny)',
                        inline=False)
        embed.add_field(name='各種リンク',
                        value=f'[BOTの招待リンク]({oauth_url}) | [公式サーバー](https://discord.com/invite/pvyMQhf)'
                              f' | [ブログサイト](https://syutarou.xyz)',
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(description='BOTの利用規約を表示します')
    async def terms(self, ctx):
        await ctx.send(f'terms')

    @commands.command(description='Botの負荷状況を表示します')
    async def status(self, ctx):
        await ctx.send(f'')

    @commands.command(description='Botのヘルプを表示します')
    async def help(self, ctx, command_names=None):
        if command_names is None:
            embed = discord.Embed(title='📃 Help', description=f'Command Prefix: ` {self.bot.command_prefix} `')
            embed.set_footer(text=f'コマンドの詳しい説明: {self.bot.command_prefix} <コマンド名>')
            commands_list = list(self.bot.commands)
            if ctx.author.id == 534994298827964416:
                command_group = {'Bot': '🤖 Botコマンド', 'Utils': '🔧 ユーティリティーコマンド', 'Info': '💻 情報コマンド',
                                 'Game': '🎮 ゲームコマンド', 'RTFM': '📃リファレンスコマンド', 'Admin': '🛠 サーバー管理者用コマンド',
                                 'Owner': '⛏ BOT開発者用コマンド'}
            else:
                command_group = {'Bot': '🤖 Botコマンド', 'Utils': '🔧 ユーティリティーコマンド', 'Info': '💻 情報コマンド',
                                 'Game': '🎮 ゲームコマンド', 'RTFM': '📃リファレンスコマンド', 'Admin': '🛠 サーバー管理者用コマンド'}
            help_cmg_list = []
            for cg in command_group:
                for cl in commands_list:
                    if cl.cog_name == cg:
                        help_cmg_list.append(f'`{cl.name}`')
                if help_cmg_list == []:
                    help_cmg_list.append('`コマンドなし`')
                else:
                    help_cmg_list.sort()
                embed.add_field(name=command_group.get(cg), value=f'> {", ".join(help_cmg_list)}', inline=False)
                help_cmg_list = []
            await ctx.send(embed=embed)
        else:
            cmd_get_name = self.bot.get_command(command_names)
            cmd_find_name = discord.utils.find(lambda cm: command_names in cm.name, list(self.bot.commands))
            no_cmd_error = discord.Embed(title='📃 CommandHelp Error',
                                         description='指定されたコマンド又はカテゴリーが見つかりませんでした')
            if cmd_get_name is None:
                if cmd_find_name is not None:
                    no_cmd_error.add_field(name='もしかして...', value=f'`{cmd_find_name}`')
                await ctx.reply(embed=no_cmd_error, allowed_mentions=discord.AllowedMentions.none())
            else:
                command = cmd_get_name
                command_aliase = []
                if command.aliases == [] or command.aliases == ():
                    command_aliase.append('`なし`')
                else:
                    for ca in command.aliases:
                        command_aliase.append(f'`{ca}`')

                help_command = discord.Embed(title=f'📃 CommandHelp - `{command.name}`',
                                             description=f'{command.description}')
                help_command.add_field(name='エイリアス', value=f'{",".join(command_aliase)}', inline=False)
                await ctx.send(embed=help_command)


def setup(bot):
    bot.add_cog(Bot(bot))
