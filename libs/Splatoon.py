import requests
from discord import Embed


class Splatoon:

    def __init__(self):
        self.endpoint = 'https://stat.ink/api/v2'

    def get_weapons(self, from_type, name):
        response = requests.get(f'{self.endpoint}/weapon')
        status = response.status_code
        res_data = response.json()
        if from_type == 'special':
            sp_list = {'アメフラシ': 'amefurashi', 'インクアーマー': 'armor', 'バブルランチャー': 'bubble', 'スーパーチャクチ': 'chakuchi',
                       'カーリングボムピッチャー': 'curlingbomb_pitcher', 'ジェットパック': 'jetpack',
                       'キューバンボムピッチャー': 'kyubanbomb_pitcher', 'マルチミサイル': 'missile', 'ナイスダマ': 'nicedama',
                       'ボムピッチャー': 'pitcher', 'ハイパープレッサー': 'presser', 'クイックボムピッチャー': 'quickbomb_pitcher',
                       'ロボボムピッチャー': 'robotbomb_pitcher', 'イカスフィア': 'sphere',
                       'スプラッシュボムピッチャー': 'splashbomb_pitcher', 'ウルトラハンコ': 'ultrahanko'
                       }
            if name in sp_list:
                if status != 200:
                    print(res_data)
                else:
                    weapon_list = []
                    for data in res_data:
                        if data['special']['key'] == sp_list[name]:
                            w_name = data['name']['ja_JP']
                            w_tye = data['type']['key']
                            weapon_list.append([f'・{w_name}', w_tye])
                    if not weapon_list:
                        return None
                    else:
                        return weapon_list
            else:
                return None

        elif from_type == 'sub':
            sub_list = {'カーリングボム': 'curlingbomb', 'ジャンプビーコン': 'jumpbeacon', 'キューバンボム': 'kyubanbomb',
                        'ポイントセンサー': 'pointsensor', 'ポイズンミスト': 'poisonmist', 'クイックボム': 'quickbomb',
                        'ロボットボム': 'robotbomb', 'スプラッシュボム': 'splashbomb', 'スプラッシュシールド': 'splashshield',
                        'スプリンクラー': 'sprinkler', 'タンサンボム': 'tansanbomb', 'トーピード': 'torpedo', 'トラップ': 'trap'
                        }
            if name in sub_list:
                if status != 200:
                    print(res_data)
                else:
                    weapon_list_sub = []
                    for data in res_data:
                        if data['sub']['key'] == sub_list[name]:
                            w_name = data['name']['ja_JP']
                            w_tye = data['type']['key']
                            weapon_list_sub.append([f'・{w_name}', w_tye])
                    if not weapon_list_sub:
                        return None
                    else:
                        return weapon_list_sub
            else:
                return None

    def sort_weapons(self, sp_name, res) -> Embed:

        we_msg = Embed(title=f'スペシャルが {sp_name} の一覧')
        weapon_list = {'shooter': 'シューター', 'blaster': 'ブラスター', 'reelgun': 'リールガン', 'maneuver': 'マニューバー',
                       'roller': 'ローラー', 'brush': 'フデ', 'charger': 'チャージャー', 'slosher': 'スロッシャー',
                       'splatling': 'スピナー', 'brella': 'シェルター'}
        we_count = 0
        for id_name, we_name in weapon_list.items():
            sorted_list = []
            for w_name, i in dict(res).items():
                if i == id_name:
                    sorted_list.append(w_name)
                    we_count += 1
            if not sorted_list:
                we_msg.add_field(name=f'{weapon_list[id_name]}',
                                 value='```\nなし\n```',
                                 inline=False
                                 )
            else:
                we_msg.add_field(name=f'{weapon_list[id_name]}',
                                 value='```\n{}\n```'.format('\n'.join(sorted_list)),
                                 inline=False
                                 )
        we_msg.set_footer(text=f'ブキの数: {we_count} 個')

        return we_msg
