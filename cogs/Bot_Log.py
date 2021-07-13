import json
import sys
import traceback

from discord import Embed, AllowedMentions
from discord.ext import commands
from datetime import datetime
from pytz import timezone


class BotLog(commands.Cog):
    """BOTのログ関係"""
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = int(self.bot.config['log_channel_id'])
        self.err_channel_id = int(self.bot.config['err_channel_id'])
        self.cmd_log_channel_id = int(self.bot.config['cmd_log_channel_id'])
        self.jl_log_channel_id = int(self.bot.config['jl_log_channel_id'])

    @commands.Cog.listener()
    async def on_command(self, ctx):
        log_channel = await self.bot.fetch_channel(self.cmd_log_channel_id)
        if log_channel:
            msg_content = str(ctx.message.content).replace('`', r'\`', -1)
            log_embed = Embed(title='コマンド実行ログ', color=2474073)
            log_embed.add_field(name='ユーザー名', value=f'`{ctx.author}`')
            log_embed.add_field(name='ユーザーID', value=f'`{ctx.author.id}`')
            log_embed.add_field(name='発言場所', value=f'```\n・サーバー名 : {ctx.guild.name}\n・サーバーID : {ctx.guild.id}\n'
                                                   f'・チャンネル名 : {ctx.channel.name}\n・チャンネルID : {ctx.channel.id}\n```',
                                inline=False)
            log_embed.add_field(name='実行コマンド', value=f'```\n{msg_content}\n```', inline=False)
            log_embed.set_thumbnail(url=ctx.author.avatar_url)
            log_embed.set_footer(text=f'{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
            await log_channel.send(embed=log_embed)

    @commands.Cog.listener()
    async def on_error(self, event, args):
        if sys.exc_info()[0].__name__ == 'MuteUserCommand':
            msg = sys.exc_info()[1].args[0]
            log_channel = await self.bot.fetch_channel(self.cmd_log_channel_id)
            if msg.content.startswith(self.bot.command_prefix):
                if log_channel:
                    msg_content = str(msg.content).replace('`', r'\`', -1)
                    log_embed = Embed(title='コマンド実行ログ', color=14363178)
                    log_embed.add_field(name='ユーザー名', value=f'`{msg.author}`')
                    log_embed.add_field(name='ユーザーID', value=f'`{msg.author.id}`')
                    log_embed.add_field(name='発言場所',
                                        value=f'```\n・サーバー名 : {msg.guild.name}\n・サーバーID : {msg.guild.id}\n```',
                                        inline=False)
                    log_embed.add_field(name='実行コマンド', value=f'```\n{msg_content}\n```', inline=False)
                    log_embed.set_thumbnail(url=msg.author.avatar_url)
                    log_embed.set_footer(text=f'{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
                    await log_channel.send(embed=log_embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            # CommandNotFound
            if isinstance(error, commands.CommandNotFound):
                return

            # CommandMissingPermission
            elif isinstance(error, commands.MissingPermissions):
                try:
                    with open("./data/permission_list.json", "r", encoding='UTF-8') as perm_list:
                        data = json.load(perm_list)
                    missing_perm = []
                    for error_permission in error.missing_perms:
                        if error_permission in data:
                            missing_perm.append(f'`{data[error_permission]}`')
                    err_embed = Embed(title='権限エラー', description='このコマンドを利用するには以下の権限が必要です。')
                    err_embed.add_field(name='必要な権限', value=f'{",".join(missing_perm)}')
                    return await ctx.reply(embed=err_embed, allowed_mentions=AllowedMentions.none())
                except Exception:
                    raise error

            # NotOwner
            elif isinstance(error, commands.NotOwner):
                return await ctx.reply("このコマンドは開発者専用コマンドです")

            # BotMissingPermissions
            elif isinstance(error, commands.BotMissingPermissions):
                with open("./data/permission_list.json", "r", encoding='UTF-8') as perm_list:
                    data = json.load(perm_list)
                text = []
                for error_permission in error.missing_perms:
                    if error_permission in data:
                        text.append(f'`{data[error_permission]}`')

                owner = await self.bot.fetch_user((await self.bot.application_info()).owner.id)
                no_msg = Embed(title='Missing Permission',
                               description=f'『{ctx.guild.name}』での{self.bot.user}の必要な権限\n```\n{",".join(text)}\n```')
                await owner.send(embed=no_msg)
                await ctx.reply(embed=no_msg, allowed_mentions=AllowedMentions.none())

            elif isinstance(error, commands.CommandOnCooldown):
                r_after = error.retry_after

                cooldown_msg = Embed(title='クールダウン中',
                                     description=f'このコマンドは `{error.cooldown.per}` 秒/回 のクールダウンがあります。\n'
                                                 f'あと {round(r_after)} 秒後に、このコマンドは利用可能です。')
                err_msg = await ctx.reply(embed=cooldown_msg, allowed_mentions=AllowedMentions.none())
                await err_msg.delete(delay=3)

            else:
                raise error

        except Exception:
            err_ch = await self.bot.fetch_channel(self.err_channel_id)
            err_msg = Embed(title='⚠エラーが発生しました',
                            description='**内容**\n予期しないエラーが発生しました。\n'
                                        'コマンドを正しく入力してもエラーが発生する場合は、お手数ですが\n'
                                        '[公式サーバー](https://discord.gg/pvyMQhf)までお問い合わせ下さい。\n')
            await ctx.reply(embed=err_msg, allowed_mentions=AllowedMentions.none())

            orig_error = getattr(error, "original", error)
            error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
            error_log_msg = Embed(description=f'```py\n{error_msg}\n```')
            error_log_msg.set_footer(text=f'サーバー: {ctx.guild.name} | 送信者: {ctx.author}')

            owner = await self.bot.fetch_user((await self.bot.application_info()).owner.id)
            await owner.send(embed=error_log_msg)
            await err_ch.send(embed=error_log_msg)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        channel = await self.bot.fetch_channel(self.jl_log_channel_id)

        if channel:
            datetime_now = datetime.now().astimezone(timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")
            value_text = f'```\nサーバー名: {guild.name}\nオーナーさん: {guild.owner}\n```'

            leave_msg = Embed(title=f'{self.bot.user}が退出しました', description='サーバーから退出しました')
            leave_msg.add_field(name='サーバー情報', value=value_text)
            leave_msg.set_footer(text=f'{datetime_now}')

            return await channel.send(embed=leave_msg)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = await self.bot.fetch_channel(self.jl_log_channel_id)

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
        """公式鯖用の機能　[ユーザー入室時 自動役職付与]"""
        if member.guild.id == 574802637598228480:
            member_role = member.guild.get_role(601283421310025729)
            bot_role = member.guild.get_role(601284694205792276)
            if member_role:
                if member.bot:
                    await member.add_roles(member_role)
                else:
                    await member.add_roles(bot_role)


def setup(bot):
    bot.add_cog(BotLog(bot))
