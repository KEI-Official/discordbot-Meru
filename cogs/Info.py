import asyncio
import datetime
from typing import Union

import discord
from discord.ext import commands
from pytz import timezone

from libs import check_permission


class Info(commands.Cog):
    """チャンネルなどの情報を見るためなどのコマンドがあるカテゴリーです"""
    def __init__(self, bot):
        self.bot = bot
        self.user_info = None
        self.channel_info = None

    @check_permission([])
    @commands.command(description='サーバーの情報を表示します',
                      aliases=['si', 'server_info'])
    async def serverinfo(self, ctx):
        guild = ctx.guild
        bot_id = self.bot.user.id
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
        server_ban_m_count = '権限不足' if not dict(guild.get_member(bot_id).guild_permissions).get('ban_members') else len(await guild.bans())
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
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @check_permission([])
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
            embed_msg = await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            await embed_msg.add_reaction('▶')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == '▶'

            try:
                await self.bot.wait_for('reaction_add', timeout=20, check=check)
            except asyncio.TimeoutError:
                await embed_msg.clear_reactions()
            else:
                await embed_msg.clear_reactions()
                role_per_list = []
                for rp in list(role_permission):
                    if rp[1]:
                        role_per_list.append(rp[0])

                s_perm_text, m_perm_text, c_perm_text, v_perm_text = self.bot.almighty.sort_permissions(role_per_list)

                permission_embed = discord.Embed(title=f'権限リスト: {role_name}')
                permission_embed.add_field(name='サーバー全般の権限', value=f'```\n{s_perm_text}\n```')
                permission_embed.add_field(name='メンバーシップ権限', value=f'```\n{m_perm_text}\n```')
                permission_embed.add_field(name='テキストチャンネル権限', value=f'```\n{c_perm_text}\n```', inline=False)
                permission_embed.add_field(name='ボイスチャンネル権限', value=f'```\n{v_perm_text}\n```')
                await embed_msg.edit(embed=permission_embed, allowed_mentions=discord.AllowedMentions.none())

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
        online = self.bot.get_emoji(871520342672285748)
        dnd = self.bot.get_emoji(871520343100108830)
        offline = self.bot.get_emoji(871520342919753749)
        idle = self.bot.get_emoji(871520343095926804)
        user_data = self.user_info
        user_id = user_data.id
        user_color = user_data.roles[len(user_data.roles)-1].color
        user_icon = user_data.avatar_url
        user_name = user_data.display_name
        user_created = user_data.created_at
        user_joined = user_data.joined_at
        status_l = {'online': f'{online} オンライン', 'dnd': f'{dnd} 取り込み中', 'idle': f'{idle} 退席中', 'offline': f'{offline} オフライン'}
        user_status = status_l[f'{user_data.status}']
        user_bot = 'Bot' if user_data.bot else 'User'

        user_evaluation = self.bot.db.user_evaluation_get(user_id)

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
        embed.add_field(name='名前',
                        value=f'> {user_name}'
                        )
        embed.add_field(name='ステータス',
                        value=f'> {user_status}'
                        )
        embed.add_field(name='Bot/User',
                        value=f'> {user_bot}'
                        )

        embed.add_field(name='アカウント作成日時',
                        value=f'> <t:{int(user_created.astimezone().timestamp())}:f>')
        embed.add_field(name='サーバー入室日時',
                        value=f'> <t:{int(user_joined.astimezone().timestamp())}:f>')

        embed.add_field(name='グローバルスコア',
                        value=f'> {"10.0" if not user_evaluation else user_evaluation[0][1]}',
                        inline=False
                        )

        embed.add_field(name=f'役職 - {len(user_data.roles)}',
                        value=user_role,
                        inline=False)

        if user_data.bot:
            embed.add_field(name='招待リンク', value=f'[0権限]({oauth_0_url}) | [全権限]({oauth_all_url})', inline=False)

        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @check_permission([])
    @commands.command(description='チャンネルの情報を表示します',
                      usage='<ID/メンション/名前>',
                      aliases=['ci', 'channel_info', 'chinfo'],
                      brief=['【実行例】\n'
                             '・ID: {cmd}channelinfo 123456789012345678\n'
                             '・メンション: {cmd}channelinfo <#123456789012345678>\n'
                             '・名前: {cmd}channelinfo チャンネル名'])
    async def channelinfo(self, ctx, *, channel: Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel] = None):
        if channel is None:
            self.channel_info = ctx.channel
        else:
            self.channel_info = channel
        ch_data = self.channel_info
        ch_id = ch_data.id
        ch_created = ch_data.created_at + datetime.timedelta(hours=2)
        ch_type = str(ch_data.type).title()
        ch_category = ch_data.category
        ch_perm = ch_data.permissions_for(ctx.author)

        embed = discord.Embed(title=f'{ch_data}', description=f'**ID**: `{ch_id}`')
        embed.add_field(name='種類', value=f'> {ch_type}Channel')
        embed.add_field(name='チャンネル作成日時',
                        value=f'> <t:{int(ch_created.timestamp())}:F>')
        embed.add_field(name='親カテゴリ',
                        value=f'> {ch_category.name if ch_category is not None else "なし"}',
                        inline=False)
        if isinstance(ch_data, discord.TextChannel):
            ch_topic = ch_data.topic
            ch_slow_delay = ch_data.slowmode_delay
            ch_nsfw = ch_data.nsfw
            embed.add_field(name='トピック',
                            value=f'> {ch_topic if ch_topic else "なし" }',
                            inline=False)
            embed.add_field(name='低速モード',
                            value=f'> {ch_slow_delay+"秒" if ch_slow_delay != 0 else "オフ"}'
                            )
            embed.add_field(name='NSFW',
                            value=f'> {"オン" if ch_nsfw else "オフ"}'
                            )

        if isinstance(ch_data, discord.VoiceChannel):
            ch_bitrate = ch_data.bitrate
            ch_limit = ch_data.user_limit
            embed.add_field(name='ビットレート', value=f'> {ch_bitrate / 1000} Kbps')
            embed.add_field(name='制限人数', value=f'> {"なし" if ch_limit == 0 else ch_limit+"人"}')

        if isinstance(ch_data, discord.CategoryChannel):
            c_ch = [ches for ches in ctx.guild.channels if ches.category is not None and ches.category == ch_data]
            embed.add_field(name='カテゴリー内のチャンネル数',
                            value=f'> {len(c_ch)} チャンネル'
                            )

        embed.add_field(name='権限の値', value=f'> {ch_perm.value}')

        embed_msg = await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        await embed_msg.add_reaction('▶')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '▶'

        try:
            await self.bot.wait_for('reaction_add', timeout=20, check=check)
        except asyncio.TimeoutError:
            await embed_msg.clear_reactions()
        else:
            await embed_msg.clear_reactions()
            per_allow_list = []
            for per, i in dict(ch_perm).items():
                if i:
                    per_allow_list.append(per)

            s_perm, m_perm, c_perm, v_perm = self.bot.almighty.sort_permissions(per_allow_list)

            perm_embed = discord.Embed(title=f'権限リスト: {ch_data}')
            perm_embed.add_field(name='サーバー全般の権限', value=f'```\n{s_perm}\n```')
            perm_embed.add_field(name='メンバーシップ権限', value=f'```\n{m_perm}\n```')
            perm_embed.add_field(name='テキストチャンネル権限', value=f'```\n{c_perm}\n```', inline=False)
            perm_embed.add_field(name='ボイスチャンネル権限', value=f'```\n{v_perm}\n```')
            await embed_msg.edit(embed=perm_embed, allowed_mentions=discord.AllowedMentions.none())

    @check_permission([])
    @commands.command(description='指定された絵文字の情報を表示します',
                      usage='[ID/名前]',
                      aliases=['ei', 'emoji_info'],
                      brief=['【実行例】\n'
                             '・ID: {cmd}emojiinfo 123456789012345678\n'
                             '・名前: {cmd}emojiinfo :emoji:(emoji)'])
    async def emojiinfo(self, ctx, emoji: discord.Emoji = None):
        if emoji is None:
            no_emoji_msg = discord.Embed(description='絵文字を指定してください')
            return await ctx.reply(embed=no_emoji_msg, allowed_mentions=discord.AllowedMentions.none())
        else:
            emoji_id = emoji.id
            emoji_name = emoji.name
            emoji_created = emoji.created_at.astimezone()
            emoji_animated = emoji.animated
            emoji_url = emoji.url
            emoji_guild = emoji.guild

            embed = discord.Embed(title=f'Emoji - {emoji}')
            embed.add_field(name='絵文字の名前', value=f'> `{emoji_name}`')
            embed.add_field(name='ID', value=f'> `{emoji_id}`')
            embed.add_field(name='URL', value=f'[Here]({emoji_url})', inline=False)
            embed.add_field(name='作成日時',
                            value=f'<t:{int(emoji_created.timestamp())}:f>')
            embed.add_field(name='アニメ絵文字', value=f'> {"はい" if emoji_animated else "いいえ"}')
            embed.add_field(name='追加されたサーバー', value=f'> {emoji_guild if emoji_guild is not None else "なし"}')
            embed.set_thumbnail(url=emoji_url)
            return await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @check_permission([])
    @commands.command(description='指定された招待リンクの情報を表示します',
                      usage='[リンク/コード]',
                      aliases=['ii', 'invite_info'],
                      brief=['【実行例】\n'
                             '・コード: {cmd}inviteinfo pvyMQhf\n'
                             '・リンク: {cmd}inviteinfo https://discord.gg/pvyMQhf'])
    async def inviteinfo(self, ctx, invite_data: discord.Invite = None):
        if not invite_data:
            no_invite_msg = discord.Embed(description='招待リンクを指定してください')
            return await ctx.reply(embed=no_invite_msg, allowed_mentions=discord.AllowedMentions.none())

        def get_d_h_m_s_us(sec):
            td = datetime.timedelta(seconds=sec)
            m, s = divmod(td.seconds, 60)
            h, m = divmod(m, 60)
            return td.days, h, m, s, td.microseconds

        guild_invite = await ctx.guild.invites()
        invite = None

        for g_i in guild_invite:
            if g_i == invite_data:
                invite = g_i

        in_age = get_d_h_m_s_us(invite.max_age)
        time_list = ['日', '時間', '分', '秒', 'ミリ秒']
        time_text = []
        for num in range(5):
            if in_age[num] != 0:
                time_text.append(f'{in_age[num]}{time_list[num]}')

        in_max = invite.max_uses
        in_temp = invite.temporary
        in_created = invite.created_at.astimezone()

        embed = discord.Embed(title=f'Invite - {invite.code}')
        embed.add_field(name='招待コード', value=f'> `{invite.code}`')
        embed.add_field(name='作成者', value=f'> {invite.inviter}')
        embed.add_field(name='作成日時',
                        value=f'{"取得不可" if in_created is None else f"<t:{int(in_created.timestamp())}:f>"}')
        embed.add_field(name='有効期限', value=f'> {"なし" if not time_text else " ".join(time_text)}')
        embed.add_field(name='利用回数', value=f'> {invite.uses} / {in_max if in_max != 0 else "∞"}')
        embed.add_field(name='一時的な招待', value=f'> {"はい" if in_temp else "いいえ"}')
        embed.add_field(name='招待リンク', value=f'[{invite.url}]({invite.url})')

        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())


def setup(bot):
    bot.add_cog(Info(bot))
