from typing import AnyStr, List


class Almighty:

    def __init__(self):
        self.server_permission = {
            'administrator': '管理者', 'read_messages': 'チャンネルを見る', 'manage_channels': 'チャンネルの管理',
            'manage_roles': 'ロールの管理', 'manage_emojis': '絵文字の管理',
            'view_audit_log': '監査ログの表示', 'view_guild_insights': 'サーバーインサイトを見る',
            'manage_webhooks': 'ウェブフックの管理', 'manage_guild': 'サーバー管理'
        }
        self.member_permission = {
            'create_instant_invite': '招待を作成', 'change_nickname': 'ニックネームの変更',
            'manage_nicknames': 'ニックネームの管理', 'kick_members': 'メンバーをキック',
            'ban_members': 'メンバーをBAN'
        }
        self.ch_permission = {
            'send_messages': 'メッセージを送信', 'embed_links': '埋め込みリンク', 'attach_files': 'ファイルを添付',
            'add_reactions': 'リアクションの追加', 'external_emojis': '外部の絵文字の利用',
            'mention_everyone': '@everyone、@here、全てのロールにメンション', 'manage_messages': 'メッセージの管理',
            'read_message_history': 'メッセージ履歴を読む', 'send_tts_messages': 'テキスト読み上げメッセージを送信する',
            'use_slash_commands': 'スラッシュコマンドを使用'
        }
        self.voice_permission = {
            'connect': '接続', 'speak': '発言', 'stream': '動画',
            'use_voice_activation': '音声検出を使用', 'priority_speaker': '優先スピーカー',
            'mute_members': 'メンバーをミュート', 'deafen_members': 'メンバーのスピーカーをミュート',
            'move_members': 'メンバーを移動', 'request_to_speak': 'スピーカー参加をリクエスト'
        }

    def sort_permissions(self, permission) -> List:
        s_perm_text = ''
        m_perm_text = ''
        c_perm_text = ''
        v_perm_text = ''

        for sp in self.server_permission:
            if sp in permission:
                s_perm_text += f"✅:{self.server_permission[sp]}\n"
            else:
                s_perm_text += f"❌:{self.server_permission[sp]}\n"
        for sp in self.member_permission:
            if sp in permission:
                m_perm_text += f"✅:{self.member_permission[sp]}\n"
            else:
                m_perm_text += f"❌:{self.member_permission[sp]}\n"
        for sp in self.ch_permission:
            if sp in permission:
                c_perm_text += f"✅:{self.ch_permission[sp]}\n"
            else:
                c_perm_text += f"❌:{self.ch_permission[sp]}\n"
        for sp in self.voice_permission:
            if sp in permission:
                v_perm_text += f"✅:{self.voice_permission[sp]}\n"
            else:
                v_perm_text += f"❌:{self.voice_permission[sp]}\n"
        res = [s_perm_text, m_perm_text, c_perm_text, v_perm_text]
        return res
