import json
from discord.ext import commands
from .Error import MissingBotPermission


def check_permission(p_list: list):
    async def predicate(ctx):
        request_perm = ['add_reactions', 'read_messages', 'send_messages', 'embed_links']
        for rep in request_perm:
            p_list.append(rep)
        perm_list = [perm for perm, b in dict(ctx.guild.get_member(ctx.bot.user.id).guild_permissions).items() if b]
        deny_list = []
        for permission in p_list:
            if not (permission in perm_list):
                deny_list.append(permission)
        print(deny_list)
        for permission in deny_list:
            if permission in request_perm:
                raise MissingBotPermission([permission])

        deny_ja_list = []
        with open("./data/permission_list.json", "r", encoding='UTF-8') as json_perm:
            data = json.load(json_perm)

        for perm in deny_list:
            if deny_list:
                deny_ja_list.append(f'・{data[perm]}')

        if deny_ja_list:
            raise MissingBotPermission(deny_ja_list)
        else:
            return True

    return commands.check(predicate)
