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
        return await ctx.send(f'招待リンクです\n{self.bot.oauth_url}')

    @commands.command(description='BOTの情報を表示します')
    async def about(self, ctx):
        owner = await self.bot.fetch_user((await self.bot.application_info()).team.owner.id)
        info_guilds = len(self.bot.guilds)
        info_user = len(self.bot.users)
        info_ch = 0
        for guild in self.bot.guilds:
            info_ch += len(guild.channels)
        embed = discord.Embed(title=f'{self.bot.user}')
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name='開発者',
                        value=f'```c\n# discord: {owner}\n```',
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
                        value='・コマンド名「rtfm」: [Rapptz/RoboDanny](https://github.com/Rapptz/RoboDanny)',
                        inline=False)
        embed.add_field(name='各種リンク',
                        value=f'[BOTの招待リンク]({self.bot.oauth_url}) | [公式サーバー](https://discord.com/invite/pvyMQhf)'
                              ' | [ブログサイト](https://syutarou.xyz)',
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(description='BOTの利用規約を表示します')
    async def terms(self, ctx):
        await ctx.send('terms')

    @commands.command(description='Botの負荷状況を表示します')
    async def status(self, ctx):
        await ctx.send('負荷情報を送信します')

    @commands.command(description='Botのヘルプを表示します')
    async def help(self, ctx, command_names=None):
        command_prefix = self.bot.command_prefix

        def send_embed(command):
            command_aliases = []
            command_usage = ''
            if not command.aliases:
                command_aliases.append('`なし`')
            else:
                for ca in command.aliases:
                    command_aliases.append(f'`{ca}`')

            if command.usage:
                command_usage += command.usage
            else:
                command_usage += ''

            command_embed = discord.Embed(title=f'📃 CommandHelp - `{command.name}`',
                                          description=f'{command.description}')
            command_embed.add_field(name='エイリアス', value=f'{",".join(command_aliases)}', inline=False)
            command_embed.add_field(name='使い方', value=f'`{command_prefix}{command.name} {command_usage}`', inline=False)
            if command.brief:
                command_brief = command.brief.replace('{cmd}', command_prefix, -1)
                command_embed.add_field(name='例', value=f'```\n{command_brief}\n```',
                                        inline=False)
            return command_embed

        if command_names is None:
            embed = discord.Embed(title='📃 Help', description=f'Command Prefix: ` {command_prefix} `')
            embed.set_footer(text=f'コマンドの詳しい説明: {command_prefix} <コマンド名>')
            commands_list = list(self.bot.commands)
            if ctx.author.id == 534994298827964416:
                command_group = {'Bot': '🤖 Botコマンド', 'Utils': '🔧 ユーティリティーコマンド', 'Info': '💻 情報コマンド',
                                 'Game': '🎮 ゲームコマンド', 'Image': '🖼 フォトコマンド', 'RTFM': '📃リファレンスコマンド',
                                 'MUrl': '🔗 メッセージURL展開機能', 'Admin': '🛠 サーバー管理者用コマンド', 'Owner': '⛏ BOT開発者用コマンド'
                                 }
            else:
                command_group = {'Bot': '🤖 Botコマンド', 'Utils': '🔧 ユーティリティーコマンド', 'Info': '💻 情報コマンド',
                                 'Game': '🎮 ゲームコマンド', 'Image': '🖼 フォトコマンド',
                                 'RTFM': '📃リファレンスコマンド', 'MUrl': '🔗 メッセージURL展開機能', 'Admin': '🛠 サーバー管理者用コマンド'
                                 }
            help_cmg_list = []
            for cg in command_group:
                for cl in commands_list:
                    if cl.cog_name == cg:
                        help_cmg_list.append(f'`{cl.name}`')
                if not help_cmg_list:
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
                                         description='指定されたコマンドが見つかりませんでした')
            if cmd_get_name is None:
                if cmd_find_name is not None:
                    no_cmd_error.add_field(name='もしかして...', value=f'`{cmd_find_name}`')
                await ctx.reply(embed=no_cmd_error, allowed_mentions=discord.AllowedMentions.none())

            elif cmd_get_name.hidden:
                if ctx.author.id != 534994298827964416:
                    beta_command = discord.Embed(title=f'📃 CommandHelp - `{cmd_get_name.name}`',
                                                 description='非公開コマンドです')
                    return await ctx.send(embed=beta_command)
                else:
                    help_command = send_embed(cmd_get_name)
                    return await ctx.send(embed=help_command)
            else:
                help_command = send_embed(cmd_get_name)
                return await ctx.send(embed=help_command)


def setup(bot):
    bot.add_cog(Bot(bot))
