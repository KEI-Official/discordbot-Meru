import asyncio
import json
import math
import sys
from datetime import datetime

import discord
import psutil
from discord.ext import commands


class Bot(commands.Cog):
    """主にBOTのヘルプや概要を表示するコマンドがあるカテゴリーです"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Botの応答速度を測ります')
    async def ping(self, ctx):
        await ctx.reply(f'🏓 Pong! - {math.floor(self.bot.latency * 1000)} ms',
                        allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='BOTの招待リンクを出します')
    async def invite(self, ctx):
        return await ctx.reply('招待リンクです\n{self.bot.config["oauth_url"]}',
                               allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='BOTの情報を表示します')
    async def about(self, ctx):
        owner = await self.bot.fetch_user((await self.bot.application_info()).owner.id)
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
                        value=f'[BOTの招待リンク]({self.bot.config["oauth_url"]}) | [公式サーバー](https://discord.com/invite/pvyMQhf)'
                              ' | [ブログサイト](https://syutarou.xyz)',
                        inline=False)
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='BOTの利用規約を表示します')
    async def terms(self, ctx):
        await ctx.send('terms')

    @commands.command(description='Botの負荷状況を表示します')
    async def status(self, ctx):

        def get_dashes(perc):
            dashes = "█" * int((float(perc) / 10 * 3))
            empty_dashes = " " * (30 - len(dashes))
            return dashes, empty_dashes

        def format_memory(mem):
            return round(mem / 1024 / 1024 / 1024, 2)

        def get_color(n):
            n = int(n)
            if n < 30:
                return 55039
            elif n < 70:
                return 15827480
            elif n <= 100:
                return 16715008

        cpu_emoji = self.bot.get_emoji(862959901227221022)
        memory_emoji = self.bot.get_emoji(862959530399629332)
        wifi_emoji = self.bot.get_emoji(862960959916343336)
        cpu_percent = psutil.cpu_percent()
        embed_color = get_color(cpu_percent)

        status_embed = discord.Embed(title=f'{self.bot.user} - Status', color=embed_color)

        dashes, empty_dashes = get_dashes(cpu_percent)
        status_embed.add_field(name=f'> {cpu_emoji} **CPU**',
                               value=f'```ini\n[ {dashes}{empty_dashes} ] [ {cpu_percent}% ]\n```',
                               inline=False)

        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        dashes, empty_dashes = get_dashes(mem_percent)
        status_embed.add_field(name=f'> {memory_emoji} **Memory**',
                               value=f'```ini\n[ {format_memory(mem.used)} / {format_memory(mem.total)} GiB]\n'
                                     f'[ {dashes}{empty_dashes} ] [ {mem_percent}% ]\n```',
                               inline=False)

        web_ping = round(self.bot.latency * 1000, 1)
        message_ping = round((datetime.utcnow().timestamp() - ctx.message.created_at.timestamp()) * 1000, 1)
        status_embed.add_field(name=f'> {wifi_emoji} **Latency**',
                               value=f'```ini\n[ WebSocket ]\n{web_ping}ms\n[ Message ]\n{message_ping}ms\n```',
                               inline=False)

        await ctx.reply(embed=status_embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='Botのヘルプを表示します')
    async def help(self, ctx, command_names=None):
        command_prefix = self.bot.command_prefix

        def send_embed(command):
            command_aliases = []
            if not command.aliases:
                command_aliases.append('なし')
            else:
                for ca in command.aliases:
                    command_aliases.append(f'`{ca}`')

            how_use_text = f'`{command_prefix}{command.name} {command.usage if command.usage else ""}`'

            command_embed = discord.Embed(title=f'📃 CommandHelp - `{command.name}`',
                                          description=f'{command.description}',
                                          color=261888)  # カラー:ライトグリーン
            command_embed.set_footer(text='[]: 必要引数 | <>: オプション引数')
            command_embed.add_field(name='エイリアス', value=f'> {", ".join(command_aliases)}')
            command_embed.add_field(name='コマンドの権限',
                                    value=f'> {command.brief[1]}'
                                    if command.brief is not None and len(command.brief) == 2 else '> 誰でも利用可能')
            command_embed.add_field(name='使い方', value=f'> {how_use_text}', inline=False)
            command_embed.add_field(name='カテゴリー',
                                    value=f'> 【 {command.cog_name} 】'
                                          f'{self.bot.get_cog(command.cog_name).description}',
                                    inline=False)

            if command.brief:
                command_brief = command.brief[0].replace('{cmd}', command_prefix, -1)
                command_embed.add_field(name='説明', value=f'```\n{command_brief}\n```',
                                        inline=False)

            return command_embed

        if command_names is None:
            embed = discord.Embed(title='📃 Help',
                                  description=f'Command Prefix: ` {command_prefix} `',
                                  color=261888)  # カラー:ライトグリーン
            embed.set_footer(text=f'コマンドの詳しい説明: {command_prefix} <コマンド名> | 1ページ目/2ページ')
            commands_list = list(self.bot.commands)
            if ctx.author.id == 534994298827964416:
                command_group = {'Bot': '🤖 Botコマンド', 'Utils': '🔧 ユーティリティーコマンド', 'Info': '💻 情報コマンド',
                                 'Game': '🎮 ゲームコマンド', 'Image': '🖼 フォトコマンド',
                                 'Admin': '🛠 サーバー管理者用コマンド', 'Owner': '⛏ BOT開発者用コマンド'
                                 }
            else:
                command_group = {'Bot': '🤖 Botコマンド', 'Utils': '🔧 ユーティリティーコマンド', 'Info': '💻 情報コマンド',
                                 'Game': '🎮 ゲームコマンド', 'Image': '🖼 フォトコマンド',
                                 'Admin': '🛠 サーバー管理者用コマンド'
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
            help_embed_msg = await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            await help_embed_msg.add_reaction('▶')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == '▶'

            try:
                await self.bot.wait_for('reaction_add', timeout=20, check=check)
            except asyncio.TimeoutError:
                try:
                    await help_embed_msg.clear_reactions()
                except discord.errors.NotFound:
                    return
            else:
                try:
                    await help_embed_msg.clear_reactions()

                    with open('./data/function_info.json', 'r', encoding='UTF-8') as config:
                        data = json.load(config)
                    chenged_msg = discord.Embed(title='📃 Help - コマンド以外の機能',
                                                description=f'他についている機能についての説明が載っています\nCommand Prefix:` {command_prefix} `',
                                                color=261888)  # カラー:ライトグリーン
                    chenged_msg.set_footer(text='2ページ目/2ページ | 他の機能のHelp')
                    for cl in data:
                        cog_meta = self.bot.get_cog(data[cl]['cog_name'])
                        cmd_list = [cmd.name for cmd in cog_meta.get_commands() if data[cl]["brief"] == cmd.brief[2]]
                        chenged_msg.add_field(name=f'🔹 {cl}', value=f'```\n{data[cl]["text"]}\n```', inline=False)
                        chenged_msg.add_field(name='> コマンドリスト', value=f'`{", ".join(cmd_list)}`')

                    await help_embed_msg.edit(embed=chenged_msg)
                except discord.errors.NotFound:
                    return
        else:
            cmd_get_name = self.bot.get_command(command_names)
            cmd_find_name = discord.utils.find(lambda cm: command_names in cm.name, list(self.bot.commands))
            no_cmd_error = discord.Embed(title='📃 CommandHelp Error',
                                         description='指定されたコマンドが見つかりませんでした',
                                         color=16715008)  # カラー:赤色
            if cmd_get_name is None:
                if cmd_find_name is not None:
                    no_cmd_error.add_field(name='もしかして...', value=f'`{cmd_find_name}`')
                await ctx.reply(embed=no_cmd_error, allowed_mentions=discord.AllowedMentions.none())

            elif cmd_get_name.hidden:
                if ctx.author.id != 534994298827964416:
                    beta_command = discord.Embed(title=f'📃 CommandHelp - `{cmd_get_name.name}`',
                                                 description='非公開コマンドです',
                                                 color=16770304)  # カラー:黄色
                    return await ctx.reply(embed=beta_command, allowed_mentions=discord.AllowedMentions.none())
                else:
                    help_command = send_embed(cmd_get_name)
                    return await ctx.reply(embed=help_command, allowed_mentions=discord.AllowedMentions.none())
            else:
                help_command = send_embed(cmd_get_name)
                return await ctx.reply(embed=help_command, allowed_mentions=discord.AllowedMentions.none())


def setup(bot):
    bot.add_cog(Bot(bot))
