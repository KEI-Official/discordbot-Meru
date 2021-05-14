import discord
from discord.ext import commands


class Info(commands.Cog):
    """Info関連コマンド"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='サーバーの情報を表示します', aliases=['si'])
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


def setup(bot):
    bot.add_cog(Info(bot))
