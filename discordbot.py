import json
import os
import traceback
import discord
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

config = {
    'log_channel_id': os.getenv('LOG_CHANNEL_ID'),
    'err_channel_id': os.getenv('ERR_CHANNEL_ID'),
    'prefix': os.getenv('PREFIX')
}

intents = discord.Intents.all()
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
bot = commands.Bot(
    command_prefix=config['prefix'],
    intents=intents,
    help_command=None
)


@bot.event
async def on_ready():
    print(f"{bot.user.name} でログインしました")
    ch = bot.get_channel(int(config['log_channel_id']))
    await bot.change_presence(activity=discord.Game(name=f"{bot.command_prefix}help | {len(bot.guilds)}Guilds |"
                                                         f" {len(bot.users)}Users", type=1))
    log_msg = discord.Embed(description=f'BOTが起動しました\n```\nユーザー数: {len(bot.users)}\n'
                                        f'サーバー数: {len(bot.guilds)}\n```')
    log_msg.set_author(name=f'{bot.user} 起動ログ', url=bot.user.avatar_url)
    log_msg.set_footer(text=f'{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
    await ch.send(embed=log_msg)


@bot.event
async def on_command_error(ctx, error):
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
                print(missing_perm)
                err_embed = discord.Embed(title='権限エラー', description='このコマンドを利用するには以下の権限が必要です。')
                err_embed.add_field(name='必要な権限', value=f'{",".join(missing_perm)}')
                return await ctx.reply(embed=err_embed, allowed_mentions=discord.AllowedMentions.none())
            except:
                raise error

        # NotOwner
        elif isinstance(error, commands.NotOwner):
            return await ctx.reply("このコマンドは開発者専用コマンドです")

        # BotMissingPermissions
        elif isinstance(error, commands.BotMissingPermissions):
            permission = {'read_messages': "メッセージを読む", 'send_messages': "メッセージを送信",
                          'read_message_history': "メッセージ履歴を読む", 'manage_messages': "メッセージの管理",
                          'embed_links': "埋め込みリンク", 'add_reactions': "リアクションの追加",
                          'manage_channels': "チャンネルの管理"}
            text = ""
            for all_error_permission in error.missing_perms:
                text += f"❌:{permission[all_error_permission]}\n"
                del permission[all_error_permission]
            for all_arrow_permission in list(permission.values()):
                text += f"✅:{all_arrow_permission}\n"
            app_info = await bot.application_info()
            no_msg = discord.Embed(title='Missing Permission',
                                   description=f'『{ctx.guild.name}』での{bot.user}の必要な権限\n'
                                               f'```\n{text}\n```')
            await app_info.owner.send(embed=no_msg)

        elif isinstance(error, commands.CommandOnCooldown):
            r_after = error.retry_after

            cooldown_msg = discord.Embed(title='クールダウン中',
                                         description=f'このコマンドは `{error.cooldown.per}` 秒/回 のクールダウンがあります。\n'
                                                     f'あと {round(r_after)} 秒後に、このコマンドは利用可能です。')
            err_msg = await ctx.reply(embed=cooldown_msg, allowed_mentions=discord.AllowedMentions.none())
            await err_msg.delete(delay=5)

        else:
            raise error

    except Exception as e:
        err_ch = await bot.fetch_channel(config['err_channel_id'])
        err_msg = discord.Embed(title='⚠エラーが発生しました',
                                description='**内容**\n予期しないエラーが発生しました。\n'
                                            'コマンドを正しく入力してもエラーが発生する場合は、お手数ですが\n'
                                            '[公式サーバー](https://discord.gg/pvyMQhf)までお問い合わせ下さい。\n')
        await ctx.reply(embed=err_msg, allowed_mentions=discord.AllowedMentions.none())

        orig_error = getattr(error, "original", error)
        error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
        error_log_msg = discord.Embed(description=f'```py\n{error_msg}\n```')
        error_log_msg.set_footer(text=f'サーバー: {ctx.guild.name} | 送信者: {ctx.author}')

        app_info = await bot.application_info()
        await app_info.owner.send(embed=error_log_msg)
        await err_ch.send(embed=error_log_msg)

if __name__ == '__main__':
    bot.config = config
    extensions = [
        'cogs.admin',
        'cogs.owner',
        'cogs.utils',
        'cogs.refe',
        'cogs.game',
        'cogs.bot',
        'cogs.info',
        'cogs.join',
        'cogs.leave',
        'jishaku'
    ]
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
