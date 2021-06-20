from discord import Embed, AllowedMentions
from discord.ext import commands

import io
import traceback
import textwrap
from pytz import timezone
from contextlib import redirect_stdout
import os

import cogs


class Owner(commands.Cog):
    """Owner関連コマンド"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = cogs.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            e_msg1 = f'Error\n```py\n{e.__class__.__name__}: {e}\n```'
            return await ctx.reply(e_msg1, allowed_mentions=AllowedMentions.none())

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            e_msg2 = f'Error\n```py\n{value}{traceback.format_exc()}\n```'
            await ctx.reply(e_msg2, allowed_mentions=AllowedMentions.none())
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except Exception:
                pass

            if ret is None:
                if value:
                    s_msg1 = f'Success\n```py\n{value}\n```'
                    return await ctx.reply(s_msg1, allowed_mentions=AllowedMentions.none())
            else:
                self._last_result = ret
                s_msg2 = f'Success\n```py\n{value}{ret}\n```'
                return await ctx.reply(s_msg2, allowed_mentions=AllowedMentions.none())

    @commands.command(pass_context=True, hidden=True,
                      aliases=['api_user', 'api_ui'],
                      description='ユーザーをAPI上から検索します')
    @commands.is_owner()
    async def search_user(self, ctx, args=None):
        if not args:
            return await ctx.reply('ユーザーIDを指定してください', allowed_mentions=AllowedMentions.none())

        fetched_user = await self.bot.fetch_user(int(args))
        if not fetched_user:
            return await ctx.reply('ユーザーが見つかりませんでした', allowed_mentions=AllowedMentions.none())

        user_info = {
            'user_id': fetched_user.id,
            'user_name': fetched_user.display_name,
            'user_avatar': fetched_user.avatar_url,
            'user_created_at': fetched_user.created_at,
            'user_guilds': fetched_user.mutual_guilds
        }
        created_at_jst = user_info["user_created_at"].astimezone(timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")

        info_msg = Embed()
        info_msg.set_author(name=f'{fetched_user}')
        info_msg.set_thumbnail(url=user_info['user_avatar'])
        info_msg.add_field(name='ユーザーID', value=f'{user_info["user_id"]}', inline=False)
        info_msg.add_field(name='ユーザー名', value=f'{user_info["user_name"]}', inline=False)
        info_msg.add_field(name='アカウント作成日時', value=f'{created_at_jst}')
        info_msg.add_field(name='共通サーバー数', value=f'{len(user_info["user_guilds"])}')

        return await ctx.reply(embed=info_msg, allowed_mentions=AllowedMentions.none())

    @commands.command(pass_context=True, hidden=True,
                      aliases=['api_server', 'api_si'],
                      description='サーバーをAPI上から検索します')
    @commands.is_owner()
    async def search_server(self, ctx, args=None):
        if not args:
            return await ctx.reply('サーバーIDを指定してください', allowed_mentions=AllowedMentions.none())

        fetched_guild = self.bot.get_guild(int(args))
        if not fetched_guild:
            return await ctx.reply('ユーザーが見つかりませんでした', allowed_mentions=AllowedMentions.none())

        guild = fetched_guild
        server_name = guild.name
        server_id = guild.id
        server_icon = guild.icon_url
        server_owner = guild.owner
        server_created = guild.created_at
        server_region = guild.region

        server_all_ch_count = len(guild.channels)
        server_t_ch_count = len(guild.text_channels)
        server_v_ch_count = len(guild.voice_channels)
        server_c_ch_count = len(guild.categories)

        server_all_member_count = len(guild.members)
        server_m_count = len([m for m in guild.members if not m.bot])
        server_b_count = len([b for b in guild.members if b.bot])
        server_ban_m_count = len(await guild.bans())
        server_e_count = len([e for e in guild.emojis if not e.animated])
        server_ani_e_count = len([ae for ae in guild.emojis if ae.animated])
        server_e_limit = guild.emoji_limit

        embed = Embed(title=server_name, description=f'ID: `{server_id}`')
        embed.add_field(name='オーナー', value=f'{server_owner} ({server_owner.id})', inline=False)
        embed.add_field(name='作成日時',
                        value=f'{server_created.astimezone(timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")}')
        embed.add_field(name='地域', value=server_region)
        embed.add_field(name=f'チャンネル - {server_all_ch_count}/500',
                        value=f'```diff\n+ カテゴリーチャンネル: {server_c_ch_count}\n+ テキストチャンネル: {server_t_ch_count}'
                              f'\n+ ボイスチャンネル: {server_v_ch_count}\n```',
                        inline=False)
        embed.add_field(name=f'メンバー - {server_all_member_count}',
                        value=f'```diff\n+ メンバー: {server_m_count}\n+ BOT: {server_b_count}'
                              f'\n+ Banされた人数: {server_ban_m_count}\n```',
                        inline=False)
        embed.add_field(name='絵文字',
                        value=f'```diff\n+ 通常: {server_e_count}/{server_e_limit}'
                              f'\n+ アニメーション: {server_ani_e_count}/{server_e_limit}\n```',
                        inline=False)
        embed.set_thumbnail(url=server_icon)
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, hidden=True,
                      description='サーバーをAPI上から検索します')
    @commands.is_owner()
    async def leave(self, ctx, args=None):
        if args is None:
            return await ctx.reply('サーバーIDを指定してください', allowed_mentions=AllowedMentions.none())

        i_get_guild = self.bot.get_guild(int(args))
        if i_get_guild is None:
            return await ctx.reply('サーバーが見つかりませんでした', allowed_mentions=AllowedMentions.none())
        await i_get_guild.leave()
        return await ctx.reply('サーバーから退出しました', allowed_mentions=AllowedMentions.none())

    @commands.command(pass_context=True, hidden=True,
                      description='指定されたCog名を再読み込みします',
                      usage='[Cog/-all]')
    @commands.is_owner()
    async def reload(self, ctx, args=None):
        extensions = [filename[:-3] for filename in os.listdir("./cogs") if filename.endswith(".py")]
        cog_blacklist = ['__init__', 'owner']
        if args is None:
            cog_error = Embed(description='再読み込みするCog名を指定してください')
            return await ctx.reply(embed=cog_error, allowed_mentions=AllowedMentions.none())
        elif args == '-all':
            for name in extensions:
                if name in cog_blacklist:
                    continue
                self.bot.reload_extension(f'cogs.{name}')
            cog_all_done = Embed(description='Cogを全て再読み込みしました')
            return await ctx.reply(embed=cog_all_done, allowed_mentions=AllowedMentions.none())

        elif args in extensions:
            self.bot.reload_extension(f'cogs.{args}')
            cog_done = Embed(description='Cogを再読み込みしました')
            return await ctx.reply(embed=cog_done, allowed_mentions=AllowedMentions.none())

        else:
            cog_error = Embed(description=f'`{args}`が見つかりませんでした')
            return await ctx.reply(embed=cog_error, allowed_mentions=AllowedMentions.none())


def setup(bot):
    bot.add_cog(Owner(bot))
