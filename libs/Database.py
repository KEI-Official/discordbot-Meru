import sqlite3
dbpath = './db/data.sqlite'
connection = sqlite3.connect(dbpath)
connection.isolation_level = None


class Database:
    def __init__(self):
        self.cursor = connection.cursor()

    def execute(self, sql):
        self.cursor.execute(sql)

    def setup(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS cmd_mute(user_id integer primary key)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS welcome_notice(guild_id integer primary key)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msg_expand(guild_id integer primary key)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                            'member_log(guild_id integer primary key, join_msg, left_msg, join_id, left_id)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                            'tao_help(guild_id integer primary key, func, log_id, role_t, role_g, role_r, premium)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                            'user_evaluation(user_id integer primary key, value_count, ban_count, reason)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS user_tag(user_id integer, tag_name, context)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                            'bot_commands(cog_name, cmd_name, description, brief, cmd_usage, alias)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS custom_prefix(guild_id integer primary key, prefix)')

    # コマンド制限
    def mute_user_set(self, user_id):
        self.setup()
        self.cursor.execute('INSERT INTO cmd_mute VALUES (?)', (user_id,))
        return True

    def mute_user_unset(self, user_id):
        self.setup()
        self.cursor.execute('DELETE FROM cmd_mute WHERE user_id = ?', (user_id,))
        return True

    def mute_user_get(self):
        self.setup()
        res = self.cursor.execute('SELECT user_id FROM cmd_mute')
        data = res.fetchall()
        return data

    # メンバー参加通知
    def welcome_notice_set(self, guild_id):
        self.setup()
        self.cursor.execute('INSERT INTO welcome_notice VALUES (?)', (guild_id,))
        return True

    def welcome_notice_unset(self, guild_id):
        self.setup()
        self.cursor.execute('DELETE FROM welcome_notice WHERE guild_id = ?', (guild_id,))
        return True

    def welcome_notice_get(self):
        self.setup()
        res = self.cursor.execute('SELECT guild_id FROM welcome_notice')
        data = res.fetchall()
        return data

    # メッセージURL展開
    def message_expand_set(self, guild_id):
        self.setup()
        self.cursor.execute('INSERT INTO msg_expand VALUES (?)', (guild_id,))
        return True

    def message_expand_unset(self, guild_id):
        self.setup()
        self.cursor.execute('DELETE FROM msg_expand WHERE guild_id = ?', (guild_id,))
        return True

    def message_expand_get(self):
        self.setup()
        res = self.cursor.execute('SELECT guild_id FROM msg_expand')
        data = res.fetchall()
        return data

    # ユーザー用ログ
    def member_log_set(self, guild_id, join_msg, left_msg, join_id, left_id):
        self.setup()
        self.cursor.execute('INSERT INTO member_log VALUES (?,?,?,?,?)',
                            (guild_id, join_msg, left_msg, join_id, left_id))
        return True

    def member_log_update(self, guild_id, args, content):
        self.setup()
        self.cursor.execute(f'UPDATE member_log SET {args}={content} WHERE guild_id = ?', (guild_id,))
        return True

    def member_log_unset(self, guild_id):
        self.setup()
        self.cursor.execute('DELETE FROM member_log WHERE guild_id = ?', (guild_id,))
        return True

    def member_log_get(self, guild_id):
        self.setup()
        res = self.cursor.execute('SELECT * FROM member_log WHERE guild_id = ?', (guild_id,))
        data = res.fetchall()
        return data

    # ユーザー評価値 機能
    def user_evaluation_set(self, user_id, value, ban_count, reason):
        self.setup()
        self.cursor.execute('INSERT INTO user_evaluation VALUES (?,?,?,?)',
                            (user_id, value, ban_count, reason))
        return True

    def user_evaluation_del(self, user_id):
        self.setup()
        self.cursor.execute('DELETE FROM user_evaluation WHERE user_id = ?', (user_id,))
        return True

    def user_evaluation_update(self, user_id, value, ban_count, reason):
        self.setup()
        self.cursor.execute('UPDATE user_evaluation SET value_count = ?, ban_count = ?, reason = ? '
                            'WHERE user_id = ?', (value, ban_count, reason, user_id))
        return True

    def user_evaluation_get(self, user_id):
        self.setup()
        res = self.cursor.execute('SELECT * FROM user_evaluation WHERE user_id = ?', (user_id,))
        data = res.fetchall()
        return data

    # タグコマンド
    def user_tag_set(self, user_id, tag_name, context):
        self.setup()
        self.cursor.execute('INSERT INTO user_tag VALUES (?,?,?)',
                            (user_id, tag_name, context))
        return True

    def user_tag_del(self, user_id, tag_name):
        self.setup()
        self.cursor.execute('DELETE FROM user_tag WHERE user_id = ? and tag_name = ?',
                            (user_id, tag_name))
        return True

    def user_tag_get(self, user_id, tag_name):
        self.setup()
        res = self.cursor.execute('SELECT context FROM user_tag WHERE user_id = ? and tag_name = ?',
                                  (user_id, tag_name))
        data = res.fetchall()
        return data

    def user_tag_all_get(self, user_id):
        self.setup()
        res = self.cursor.execute('SELECT * FROM user_tag WHERE user_id = ?',
                                  (user_id,))
        data = res.fetchall()
        return data

    # ダッシュボード用 コマンド
    def command_set(self, command) -> bool:
        self.setup()
        cmd_des = command.description
        cmd_usage = command.usage
        cmd_cog = command.cog_name
        cmd_name = command.name
        cmd_brief = None if not command.brief else command.brief[0]
        cmd_aliases = None if not command.aliases else ', '.join(command.aliases)
        print(type(cmd_name), type(cmd_usage), type(cmd_cog), type(cmd_des), type(cmd_brief), type(cmd_aliases))
        self.cursor.execute('INSERT INTO bot_commands VALUES (?,?,?,?,?,?)',
                            (cmd_cog, cmd_name, cmd_des, cmd_brief, cmd_usage, cmd_aliases))
        return True

    def command_get(self, cog_name):
        self.setup()
        res = self.cursor.execute('SELECT * FROM bot_commands WHERE cog_name = ?', (cog_name,))
        data = res.fetchall()
        return data

    def command_all_get(self) -> tuple:
        self.setup()
        res = self.cursor.execute('SELECT * FROM bot_commands')
        data = res.fetchall()
        command_list = [d[1] for d in data]
        return len(data), command_list

    def command_del(self) -> bool:
        self.cursor.execute('DROP TABLE bot_commands')
        return True

    # カスタムprefix
    def custom_prefix_set(self, guild_id, prefix):
        self.setup()
        self.cursor.execute('INSERT INTO custom_prefix VALUES (?,?)', (guild_id, prefix))
        return True

    def custom_prefix_del(self, guild_id):
        self.setup()
        self.cursor.execute('DELETE FROM custom_prefix WHERE guild_id = ?', (guild_id,))
        return True

    def custom_prefix_get(self, guild_id):
        self.setup()
        res = self.cursor.execute('SELECT prefix FROM custom_prefix WHERE guild_id = ?', (guild_id,))
        data = res.fetchall()
        return data
