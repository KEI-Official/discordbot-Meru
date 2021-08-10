import json
import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
from dotenv import load_dotenv
from libs import Database, Splatoon, Almighty
from libs.Error import MuteUserCommand
load_dotenv()

config = {
    'log_channel_id': os.getenv('LOG_CHANNEL_ID'),
    'err_channel_id': os.getenv('ERR_CHANNEL_ID'),
    'cmd_log_channel_id': os.getenv('CMD_LOG_CHANNEL_ID'),
    'jl_log_channel_id': os.getenv('JOIN_LEFT_LOG_CHANNEL_ID'),
    'prefix': os.getenv('PREFIX'),
    'owner_id': os.getenv('OWNER_ID'),
    'oauth_url': discord.utils.oauth_url(os.getenv('BOT_ID'), permissions=discord.Permissions(1345711223))
}

extensions_list = [f[:-3] for f in os.listdir("./cogs") if f.endswith(".py")]


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ban_users = []

    async def get_context(self, message, *args, **kwargs):
        if message.author.id in bot.ban_users:
            raise MuteUserCommand(message)
        return await super().get_context(message, *args, **kwargs)


async def prefix_from_db(bot, msg):
    prefix = Database.Database().custom_prefix_get(msg.guild.id)
    if not prefix:
        return config['prefix']
    else:
        return prefix[0]


intents = discord.Intents.all()
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
bot = MyBot(
    command_prefix=prefix_from_db,
    intents=intents,
    help_command=None
)

bot.db = Database.Database()
bot.splatoon = Splatoon.Splatoon()
bot.almighty = Almighty.Almighty()


@tasks.loop(minutes=10)
async def pre_loop():
    await bot.wait_until_ready()
    await bot.change_presence(
        activity=discord.Game(name=f'{config["prefix"]}help | {len(bot.guilds)} Servers')
    )
    data = {
        "bot_guilds": len(bot.guilds),
        "bot_users": len(bot.users),
        "bot_commands": len(bot.commands),
        "bot_ping": round(bot.latency * 1000, 1)
    }
    file = open('./data/bot_data.json', 'w')
    json.dump(data, file, indent=4)


@bot.event
async def on_ready():
    print(f'{bot.user.name} でログインしました')
    ch = bot.get_channel(int(config['log_channel_id']))
    log_msg = discord.Embed(description=f'BOTが起動しました\n```\nユーザー数: {len(bot.users)}\n'
                                        f'サーバー数: {len(bot.guilds)}\n```')
    log_msg.set_author(name=f'{bot.user} 起動ログ', url=bot.user.avatar_url)
    log_msg.set_footer(text=f'{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
    await ch.send(embed=log_msg)
    if not pre_loop.is_running():
        pre_loop.start()


@bot.listen('on_ready')
async def get_ban_users():
    bot.ban_users = bot.db.mute_user_get()

    commands_list = list(bot.commands)
    print(f'ロードしているコマンド数: {len(commands_list)}')
    db_command = bot.db.command_all_get()
    if commands_list:
        if db_command[0] < len(commands_list):
            for cmd in commands_list:
                if cmd.name in db_command[1]:
                    commands_list.remove(cmd)
            for cmd in commands_list:
                bot.db.command_set(cmd)
            print(f'success - {bot.db.command_all_get()[0]}')


if __name__ == '__main__':
    bot.config = config
    other_extension = ['jishaku']
    blacklist = ['refe']
    for o_extension in other_extension:
        try:
            bot.load_extension(o_extension)
        except commands.ExtensionAlreadyLoaded:
            bot.reload_extension(o_extension)
    for extension in extensions_list:
        try:
            if extension in blacklist:
                pass
            else:
                bot.load_extension(f'cogs.{extension}')
        except commands.ExtensionAlreadyLoaded:
            if extension in blacklist:
                pass
            else:
                bot.reload_extension(f'cogs.{extension}')

    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
