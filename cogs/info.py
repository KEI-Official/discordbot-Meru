import asyncio
import discord
from discord.ext import commands
from pytz import timezone


class Info(commands.Cog):
    """チャンネルなどの情報を見るためなどのコマンドがあるカテゴリーです"""
    def __init__(self, bot):
        self.bot = bot
        self.user_info = None

    @commands.command(description='サーバーの情報を表示します',
                      aliases=['si', 'server_info'])
    async def serverinfo(self, ctx):
        guild = ctx.guild
        server_name = guild.name
        server_id = guild.id
        server_icon = guild.icon_url
        server_owner = guild.owner
        server_created = guild.created_at
        server_region = guild.region
        server_system_ch = ""
        if guild.system_channel:
            server_system_ch += guild.system_channel.name
        else:
            server_system_ch += "なし"
        server_all_ch_count = len(guild.channels)
        server_t_ch_count = len(guild.text_channels)
        server_v_ch_count = len(guild.voice_channels)
        server_c_ch_count = len(guild.categories)
        server_all_member_count = len(guild.members)
        server_m_count = len([m for m in guild.members if not m.bot])
        server_b_count = len([b for b in guild.members if b.bot])
        server_ban_m_count = len(await guild.bans())
        server_e_count = len([e for e in guild.emojis if not e.animated])
        server_e_limit = guild.emoji_limit
        server_ani_e_count = len([ae for ae in guild.emojis if ae.animated])
        server_role_count = len(guild.roles)
        server_role = ""
        for num in reversed(range(server_role_count-5, server_role_count)):
            server_role += (guild.roles[num].mention + ' | ')

        embed = discord.Embed(title=server_name, description=f'ID: `{server_id}`')
        embed.set_thumbnail(url=server_icon)
        embed.add_field(name='オーナー', value=f'{server_owner} ({server_owner.id})', inline=False)
        embed.add_field(name='作成日時',
                        value=f'{server_created.astimezone(timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")}')
        embed.add_field(name='地域', value=server_region)
        embed.add_field(name='サーバーアイコン', value=f'[Here]({server_icon})')
        embed.add_field(name=f'チャンネル - {server_all_ch_count}/500',
                        value=f'```diff\n+ カテゴリーチャンネル: {server_c_ch_count}\n+ テキストチャンネル: {server_t_ch_count}'
                              f'\n+ ボイスチャンネル: {server_v_ch_count}\n+ システムチャンネル: {server_system_ch}\n```',
                        inline=False)
        embed.add_field(name=f'メンバー - {server_all_member_count}',
                        value=f'```diff\n+ メンバー: {server_m_count}\n+ BOT: {server_b_count}'
                              f'\n+ Banされた人数: {server_ban_m_count}\n```',
                        inline=False)
        embed.add_field(name='絵文字',
                        value=f'```diff\n+ 通常: {server_e_count}/{server_e_limit}'
                              f'\n+ アニメーション: {server_ani_e_count}/{server_e_limit}\n```',
                        inline=False)
        embed.add_field(name=f'役職 - {server_role_count}',
                        value=server_role + '..以下略',
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(description='指定された役職の情報を表示します',
                      usage='[ID/メンション/名前]',
                      aliases=['ri', 'role_info'],
                      brief=['【実行例】\n'
                             '・ID: {cmd}roleinfo 123456789012345678\n'
                             '・メンション: {cmd}roleinfo <@&123456789012345678>\n'
                             '・名前: {cmd}roleinfo Bot'])
    async def roleinfo(self, ctx, role: discord.Role = None):
        if role is None:
            no_role_msg = discord.Embed(description='役職を以下の形で指定してください\n```\n・ID\n・名前\n・メンション\n```')
            return await ctx.reply(embed=no_role_msg, allowed_mentions=discord.AllowedMentions.none())
        else:
            role_info = role
            role_id = role_info.id
            role_name = role_info.name
            role_created = role_info.created_at
            role_mentionable = role_info.mentionable
            role_managed = role_info.managed
            role_color = role_info.color
            role_permission = role_info.permissions
            role_members = role_info.members
            role_member = ''
            if len(role_members) == 0:
                role_member += 'なし'
            elif len(role_members) < 15:
                for m in range(len(role_members)):
                    role_member += role_members[m].mention + ', '
            else:
                role_member += '`上位15人を表示`\n'
                for m in range(15):
                    role_member += role_members[m].mention + ', '
                role_member += ' ...以下略'

            embed = discord.Embed(title=f'Role - {role_name}', color=role_color, description=f'**ID**: `{role_id}`')
            embed.add_field(name='作成日時',
                            value=f'{role_created.astimezone(timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")}')
            embed.add_field(name='メンション可/不可', value=f'{role_mentionable}')
            embed.add_field(name='外部サービスとの連携', value=f'{role_managed}')
            embed.add_field(name='役職の色', value=f'{role_color}')
            embed.add_field(name='権限', value=f'{role_permission.value}')
            embed.add_field(name=f'持っている人 - {len(role_members)}人',
                            value=f'{role_member}', inline=False)
            embed_msg = await ctx.send(embed=embed)
            await embed_msg.add_reaction('▶')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == '▶'

            try:
                await self.bot.wait_for('reaction_add', timeout=20, check=check)
            except asyncio.TimeoutError:
                await embed_msg.clear_reactions()
            else:
                await embed_msg.clear_reactions()
                server_permission = {
                    'administrator': '管理者', 'read_messages': 'チャンネルを見る', 'manage_channels': 'チャンネルの管理',
                    'manage_roles': 'ロールの管理', 'manage_emojis': '絵文字の管理',
                    'view_audit_log': '監査ログの表示', 'view_guild_insights': 'サーバーインサイトを見る',
                    'manage_webhooks': 'ウェブフックの管理', 'manage_guild': 'サーバー管理'
                }
                member_permission = {
                    'create_instant_invite': '招待を作成', 'change_nickname': 'ニックネームの変更',
                    'manage_nicknames': 'ニックネームの管理', 'kick_members': 'メンバーをキック',
                    'ban_members': 'メンバーをBAN'
                }
                ch_permission = {
                    'send_messages': 'メッセージを送信', 'embed_links': '埋め込みリンク', 'attach_files': 'ファイルを添付',
                    'add_reactions': 'リアクションの追加', 'external_emojis': '外部の絵文字の利用',
                    'mention_everyone': '@everyone、@here、全てのロールにメンション', 'manage_messages': 'メッセージの管理',
                    'read_message_history': 'メッセージ履歴を読む', 'send_tts_messages': 'テキスト読み上げメッセージを送信する',
                    'use_slash_commands': 'スラッシュコマンドを使用'
                }
                voice_permission = {
                    'connect': '接続', 'speak': '発言', 'stream': '動画',
                    'use_voice_activation': '音声検出を使用', 'priority_speaker': '優先スピーカー',
                    'mute_members': 'メンバーをミュート', 'deafen_members': 'メンバーのスピーカーをミュート',
                    'move_members': 'メンバーを移動', 'request_to_speak': 'スピーカー参加をリクエスト'
                }

                s_perm_text = ''
                m_perm_text = ''
                c_perm_text = ''
                v_perm_text = ''
                role_permission_list = []
                for rp in list(role_permission):
                    if rp[1]:
                        role_permission_list.append(rp[0])

                for sp in server_permission:
                    if sp in role_permission_list:
                        s_perm_text += f"✅:{server_permission[sp]}\n"
                    else:
                        s_perm_text += f"❌:{server_permission[sp]}\n"
                for sp in member_permission:
                    if sp in role_permission_list:
                        m_perm_text += f"✅:{member_permission[sp]}\n"
                    else:
                        m_perm_text += f"❌:{member_permission[sp]}\n"
                for sp in ch_permission:
                    if sp in role_permission_list:
                        c_perm_text += f"✅:{ch_permission[sp]}\n"
                    else:
                        c_perm_text += f"❌:{ch_permission[sp]}\n"
                for sp in voice_permission:
                    if sp in role_permission_list:
                        v_perm_text += f"✅:{voice_permission[sp]}\n"
                    else:
                        v_perm_text += f"❌:{voice_permission[sp]}\n"

                permission_embed = discord.Embed(title=f'権限リスト: {role_name}')
                permission_embed.add_field(name='サーバー全般の権限', value=f'```\n{s_perm_text}\n```')
                permission_embed.add_field(name='メンバーシップ権限', value=f'```\n{m_perm_text}\n```')
                permission_embed.add_field(name='テキストチャンネル権限', value=f'```\n{c_perm_text}\n```', inline=False)
                permission_embed.add_field(name='ボイスチャンネル権限', value=f'```\n{v_perm_text}\n```')
                await embed_msg.edit(embed=permission_embed)

    @commands.command(description='ユーザーの情報を表示します',
                      usage='<ID/メンション/名前>',
                      aliases=['ui', 'user_info'],
                      brief=['【実行例】\n'
                             '・ID: {cmd}userinfo 123456789012345678\n'
                             '・メンション: {cmd}userinfo <@123456789012345678>\n'
                             '・名前: {cmd}userinfo ユーザー'])
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            self.user_info = ctx.author
        else:
            self.user_info = member
        user_data = self.user_info
        user_id = user_data.id
        user_color = user_data.roles[len(user_data.roles)-1].color
        user_icon = user_data.avatar_url
        user_name = user_data.display_name
        user_created = user_data.created_at
        user_joined = user_data.joined_at
        status_l = {'online': '🟢 `オンライン`', 'dnd': '🔴 `取り込み中`', 'idle': '🟡 `退席中`', 'offline': '⚪ オフライン'}
        user_status = status_l[f'{user_data.status}']
        user_bot = 'Bot' if user_data.bot else 'User'

        user_role = ''
        if len(user_data.roles) == 15:
            user_role += 'なし'
        elif len(user_data.roles) < 15:
            for num in reversed(range(len(user_data.roles))):
                user_role += (user_data.roles[num].mention + ', ')
        else:
            for num in reversed(range(len(user_data.roles) - 15, len(user_data.roles))):
                user_role += (user_data.roles[num].mention + ', ')
            user_role += '...以下略'

        oauth_0_url = f'https://discord.com/oauth2/authorize?client_id={user_id}&permissions=0&scope=bot'
        oauth_all_url = f'https://discord.com/oauth2/authorize?client_id={user_id}&permissions=4294967287&scope=bot'

        embed = discord.Embed(title=f'{user_data}', description=f'**ID**: `{user_id}`', color=user_color)
        embed.set_thumbnail(url=user_icon)
        embed.add_field(name='名前', value=f'`{user_name}`')
        embed.add_field(name='アカウント作成日時',
                        value=f'`{user_created.astimezone(timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")}`')
        embed.add_field(name='サーバー入室日時',
                        value=f'`{user_joined.astimezone(timezone("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")}`')
        embed.add_field(name='ステータス', value=f'{user_status}')
        embed.add_field(name='BotかUser', value=f'`{user_bot}`')
        embed.add_field(name=f'役職 - {len(user_data.roles)}', value=user_role, inline=False)
        if user_data.bot:
            embed.add_field(name='招待リンク', value=f'[0権限]({oauth_0_url}) | [全権限]({oauth_all_url})', inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
