from discord.ext.commands import CheckFailure


class MuteUserCommand(Exception):
    """Mute中のユーザーがコマンド使った時に走る例外クラス"""
    pass


class MissingBotPermission(CheckFailure):
    def __init__(self, missing_permissions, *args):
        self.missing_permissions = missing_permissions

        missing = [perm for perm in missing_permissions]

        if len(missing) > 2:
            fmt = '{}, and {}'.format(", ".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        message = f'Bot requires {fmt} permission(s) to run this command.'
        super().__init__(message, *args)
