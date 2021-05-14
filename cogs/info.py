import re
import discord
from discord.ext import commands


class Info(commands.Cog):
    """Info関連コマンド"""
    def __init__(self, bot):
        self.bot = bot
        self.role_info = None

    @commands.command(description='サーバーの情報を表示します', aliases=['si', 'server_info'])
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
        embed.add_field(name='作成日時', value=f'{server_created.strftime("%Y/%m/%d %H:%M:%S")}')
        embed.add_field(name='地域', value=server_region)
        embed.add_field(name=f'チャンネル - {server_all_ch_count}/500',
                        value=f'```diff\n+ カテゴリーチャンネル: {server_c_ch_count}\n+ テキストチャンネル: {server_t_ch_count}'
                              f'\n+ ボイスチャンネル: {server_v_ch_count}\n+ システムチャンネル: {server_system_ch}\n```',
                        inline=False)
        embed.add_field(name=f'メンバー - {server_all_member_count}',
                        value=f'```diff\n+ メンバー: {server_m_count}\n+ BOT: {server_b_count}'
                              f'\n+ Banされた人数: {server_ban_m_count}\n```',
                        inline=False)
        embed.add_field(name=f'絵文字',
                        value=f'```diff\n+ 通常: {server_e_count}/{server_e_limit}'
                              f'\n+ アニメーション: {server_ani_e_count}/{server_e_limit}\n```',
                        inline=False)
        embed.add_field(name=f'役職 - {server_role_count}',
                        value=server_role + '..以下略',
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(description='指定された役職の情報を表示します', aliases=['ri', 'role_info'])
    async def roleinfo(self, ctx, role=None):
        if role is None:
            no_role_msg = discord.Embed(description='役職を以下の形で指定してください\n```\n・ID\n・名前\n・メンション\n```')
            return await ctx.reply(embed=no_role_msg, allowed_mentions=discord.AllowedMentions.none())

        elif ctx.message.role_mentions:
            self.role_info = ctx.message.role_mentions[0]
        elif re.search(r'[0-9]{18}', str(role)) is not None:
            pre_role = ctx.guild.get_role(int(role))
            if pre_role:
                self.role_info = pre_role
            else:
                no_role_msg = discord.Embed(description='役職が見つかりませんでした\n**考えられる原因**```\nIDは間違っていませんか？```')
                return await ctx.reply(embed=no_role_msg, allowed_mentions=discord.AllowedMentions.none())
        else:
            pre_role = discord.utils.get(ctx.guild.roles, name=role)
            if pre_role:
                self.role_info = pre_role
            else:
                no_role_msg = discord.Embed(description='役職が見つかりませんでした\n**考えられる原因**```\n名前は間違っていませんか？```')
                return await ctx.reply(embed=no_role_msg, allowed_mentions=discord.AllowedMentions.none())

        if self.role_info is not None:
            role_info = self.role_info
            role_id = role_info.id
            role_name = role_info.name
            role_created = role_info.created_at
            role_mentionable = role_info.mentionable
            role_managed = role_info.managed
            role_color = role_info.color
            role_permission = role_info.permissions.value
            role_members = role_info.members
            role_member = ''
            if len(role_members) == 0:
                role_member += 'なし'
            elif len(role_members) < 10:
                for m in range(len(role_members)):
                    role_member += role_members[m].mention + ', '
            else:
                role_member += '`上位10人を表示`\n'
                for m in range(10):
                    role_member += role_members[m].mention + ', '
                role_member += ' ...以下略'

            embed = discord.Embed(title=f'Role - {role_name}', color=role_color, description=f'**ID**: `{role_id}`')
            embed.add_field(name='作成日時', value=f'{role_created.strftime("%Y/%m/%d %H:%M:%S")}')
            embed.add_field(name='メンション可/不可', value=f'{role_mentionable}')
            embed.add_field(name='外部サービスとの連携', value=f'{role_managed}')
            embed.add_field(name='役職の色', value=f'{role_color}')
            embed.add_field(name='権限', value=f'{role_permission}')
            embed.add_field(name=f'持っている人 - {len(role_members)}人',
                            value=f'{role_member}', inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
