import asyncio
import re
from typing import Optional
from discord import Embed, AllowedMentions, ChannelType, utils
from discord.ext import commands


class Admin(commands.Cog):
    """特定の権限が必要なコマンドがあるカテゴリーです"""
    def __init__(self, bot):
        self.bot = bot
        self.get_user = None
        self.get_channel = None

    # FIXME: 要確認
    @commands.command(description='指定されたユーザーのBANを行います',
                      usage='[ID/メンション] <理由>',
                      brief=['【実行例】\n'
                             '・{cmd}ban 123456789012345678 荒らし',
                             'ban_members']
                      )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user=None, reason=None):
        if user is None:
            no_user = Embed(description='BANを行うユーザーをIDで指定してください')
            return await ctx.reply(embed=no_user, allowed_mentions=AllowedMentions.none())
        elif ctx.message.mentions:
            self.get_user = ctx.message.mentions[0]
        elif re.search(r'[0-9]{18}', user) is not None:
            pre_user = ctx.guild.get_member(int(user))
            if pre_user:
                self.get_user = pre_user
            else:
                no_user_msg = Embed(description='ユーザーが見つかりませんでした\n**考えられる原因**```'
                                                '\n・IDは間違っていませんか？\n・ユーザーはサーバーにいますか？\n```')
                return await ctx.reply(embed=no_user_msg, allowed_mentions=AllowedMentions.none())
        if self.get_user is not None:
            veri_msg = Embed(title='BAN確認画面',
                             description='以下のユーザーにBANを行います。\n行う場合は`y`、キャンセルする場合は`n`を送信してください。')
            veri_msg.add_field(name='名前', value=f'{self.get_user}')
            veri_msg.add_field(name='ID', value=f'{self.get_user.id}')
            if reason is not None:
                veri_msg.add_field(name='理由', value=f'{reason}', inline=False)
            else:
                veri_msg.add_field(name='理由', value='なし', inline=False)

            veri_embed = await ctx.send(embed=veri_msg)

            def check(c_msg):
                return c_msg.author == ctx.author and c_msg.channel == ctx.channel

            try:
                msg = await self.bot.wait_for('message', timeout=20, check=check)
            except asyncio.TimeoutError:
                return await veri_embed.edit(embed=Embed(description='時間切れです...'))
            else:
                if msg.content == 'y':
                    await msg.delete()
                    if reason is not None:
                        await ctx.guild.ban(user=self.get_user, reason=f'{reason}')
                    else:
                        await ctx.guild.ban(user=self.get_user, reason='なし')
                    s_embed = Embed(description='指定ユーザーのBANが完了しました')
                    s_embed.add_field(name='名前', value=f'{self.get_user}')
                    s_embed.add_field(name='ID', value=f'{self.get_user.id}')
                    s_embed.set_footer(text=f'実行者: {ctx.author}')
                    return await veri_embed.edit(embed=s_embed)
                if msg.content == 'n':
                    await msg.delete()

    @commands.command(description='指定されたカテゴリー内にあるチャンネルを全て削除します',
                      usage='[カテゴリーID]',
                      aliases=['delc'],
                      brief=['【実行例】\n'
                             '・{cmd}delcategory 123456789012345678',
                             'manage_channels']
                      )
    @commands.has_permissions(manage_channels=True)
    async def delcategory(self, ctx, category_id: Optional[int]) -> None:
        if category_id is None:
            no_id = Embed(description='削除を行うカテゴリーIDを指定してください')
            return await ctx.reply(embed=no_id, allowed_mentions=AllowedMentions.none())
        else:
            got_category = ctx.guild.get_channel(category_id)
            if got_category is None:
                no_cate = Embed(description='カテゴリーが見つかりませんでした')
                return await ctx.reply(embed=no_cate, allowed_mentions=AllowedMentions.none())
            elif got_category.type != ChannelType.category:
                no_type = Embed(description='指定したIDはカテゴリーIDではありません\nIDを確認してみてください')
                return await ctx.reply(embed=no_type, allowed_mentions=AllowedMentions.none())
            else:
                got_ch = Embed(description='指定されたカテゴリー内にあるチャンネルを全て削除しますか？')
                re_msg = await ctx.reply(embed=got_ch, allowed_mentions=AllowedMentions.none())
                await re_msg.add_reaction('✅')
                await re_msg.add_reaction('❎')

                def check(p_reaction, p_user):
                    return p_user == ctx.author and p_reaction.message == re_msg

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                except asyncio.TimeoutError:
                    return await re_msg.edit(embed=Embed(description='時間切れです...'))
                else:
                    if str(reaction) == '✅':
                        load_emoji = self.bot.get_emoji(852849151628935198)
                        await re_msg.edit(embed=Embed(description=f'{load_emoji} 削除しています...'))
                        ch_list = []
                        for ch in ctx.guild.channels:
                            if ch.type != ChannelType.category and got_category == ch.category:
                                ch_list.append(f'・{ch.name}')
                                await ch.delete()
                        ch_list_text = ''
                        if not ch_list:
                            ch_list_text += 'チャンネルなし'
                        elif len(str('\n'.join(ch_list))) > 2000:
                            ch_list_text += '2048文字以上のため非表示'
                        else:
                            ch_list_text += '\n'.join(ch_list)
                        await re_msg.clear_reactions()
                        return await re_msg.edit(embed=Embed(description='✅ 指定されたカテゴリー内のチャンネルをすべて削除しました\n'
                                                                         f'```\n{ch_list_text}\n```'))
                    elif str(reaction) == '❎':
                        await re_msg.clear_reactions()
                        return await re_msg.edit(embed=Embed(description='❎ 操作をキャンセルしました'))

    @commands.command(description='指定されたチャンネルを複製します',
                      usage='[Channel ID/名前/メンション] <c=回数 | n=複製先の名前>',
                      brief=['【実行例】\n'
                             '・そのまま複製\n{cmd}clone 740381404952000000\n'
                             '・5回複製\n{cmd}clone 740381404952000000 c=5\n'
                             '・testで複製\n{cmd}clone 740381404952000000 n=test',
                             'manage_channels']
                      )
    @commands.has_permissions(manage_channels=True)
    async def clone(self, ctx, ch=None, name_int=None):
        if ch is None:
            no_ch_msg = Embed(description='チャンネルを以下の形で指定してください\n```\n・ID\n・名前\n・メンション\n```')
            return await ctx.reply(embed=no_ch_msg, allowed_mentions=AllowedMentions.none())

        elif ctx.message.channel_mentions:
            self.get_channel = ctx.message.channel_mentions[0]

        elif re.search(r'[0-9]{18}', str(ch)) is not None:
            pre_ch = ctx.guild.get_channel(int(ch))
            if pre_ch:
                self.get_channel = pre_ch
            else:
                no_ch_msg = Embed(description='チャンネルが見つかりませんでした\nチャンネルIDは間違っていませんか？')
                return await ctx.reply(embed=no_ch_msg, allowed_mentions=AllowedMentions.none())
        else:
            pre_ch = utils.get(ctx.guild.channels, name=ch)
            if pre_ch:
                self.get_channel = pre_ch
            else:
                no_ch_msg = Embed(description='チャンネルが見つかりませんでした\nチャンネルの名前は間違っていませんか？')
                return await ctx.reply(embed=no_ch_msg, allowed_mentions=AllowedMentions.none())

        if self.get_channel is not None:
            get_channel = self.get_channel
            if name_int is None:
                cloned_ch = await get_channel.clone()
                return await ctx.reply(embed=Embed(description=f'✅ 指定されたチャンネルを複製しました\nチャンネル: {cloned_ch.mention}'),
                                       allowed_mentions=AllowedMentions.none())
            elif str(name_int).startswith('n='):
                change_name = name_int.replace('n=', '')
                if not change_name:
                    return await ctx.reply(embed=Embed(description='名前を指定してください'),
                                           allowed_mentions=AllowedMentions.none())
                else:
                    cloned_ch = await get_channel.clone(name=change_name)
                    return await ctx.reply(embed=Embed(description=f'✅ 指定されたチャンネルを複製しました\nチャンネル: {cloned_ch.mention}'),
                                           allowed_mentions=AllowedMentions.none())
            elif str(name_int).startswith('c='):
                repeat_count = name_int.replace('c=', '')
                if not repeat_count:
                    return await ctx.reply(embed=Embed(description='回数を指定してください'),
                                           allowed_mentions=AllowedMentions.none())
                elif int(repeat_count) > 10:
                    high_int_msg = Embed(description='一度に複製できる回数は10回までです')
                    return await ctx.reply(embed=high_int_msg, allowed_mentions=AllowedMentions.none())
                else:
                    pre_embed = Embed(description=f'{get_channel.name} の複製を {repeat_count} 回行いますか？')
                    pre_ch_msg = await ctx.reply(embed=pre_embed, allowed_mentions=AllowedMentions.none())
                    await pre_ch_msg.add_reaction('✅')
                    await pre_ch_msg.add_reaction('❎')

                    def check(p_reaction, p_user):
                        return p_user == ctx.author and p_reaction.message == pre_ch_msg

                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                    except asyncio.TimeoutError:
                        await pre_ch_msg.clear_reactions()
                        return await pre_ch_msg.edit(embed=Embed(description='時間切れです...'))
                    else:
                        if str(reaction) == '✅':
                            await pre_ch_msg.clear_reactions()

                            load_emoji = self.bot.get_emoji(852849151628935198)
                            await pre_ch_msg.edit(embed=Embed(description=f'{load_emoji} チャンネルを{repeat_count}回複製中...'))

                            for num in range(int(repeat_count)):
                                await get_channel.clone()
                                embed = Embed(description=f'{load_emoji} チャンネルを{repeat_count}回複製中...\n'
                                                          f'{num+1}/{repeat_count} 回完了')
                                await pre_ch_msg.edit(embed=embed)
                            return await pre_ch_msg.edit(embed=Embed(description=f'✅ チャンネル: {get_channel.mention}'
                                                                                 ' の複製が完了しました'))
                        elif str(reaction) == '❎':
                            await pre_ch_msg.clear_reactions()
                            return await pre_ch_msg.edit(embed=Embed(description='❎ 操作をキャンセルしました'))
            else:
                no_embed = Embed(description='名前または回数を以下のように指定してください\n'
                                             '```\n・名前: n=名前\n・回数: c=回数(数値)\n```')
                return await ctx.reply(embed=no_embed, allowed_mentions=AllowedMentions.none())


def setup(bot):
    bot.add_cog(Admin(bot))
