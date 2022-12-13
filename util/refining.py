import os
import pandas as pd
import yaml


def calc_refining(probability):
    df_refining_data = pd.DataFrame()
    master_energy_fixed_value = 0.4651  #장인의 기운 고정값
    probability = probability/100       # 처음 강화 확률
    change_probability = 0              # 변동된 강화 확률
    fail_before = 1
    success_this_time = 0               # N트만에 성공할 확률
    cumulative = 0                      # N트안에 성공할 확률
    master_energy = 0                   # 장인의 기운
    try_num = 1                         # 트라이 횟수

    while True:
        if try_num <= 11:
            change_probability = round(probability + (probability * 0.1 * (try_num-1)), 5)
        if master_energy >= 1:
            change_probability, master_energy = 1, 1
        success_this_time = round(fail_before * change_probability, 5)
        cumulative = round(cumulative + success_this_time, 5)
        if cumulative >= 1:
            cumulative = 1
        # print(f'{num} | {change_probability} | {success_this_time} | {cumulative} | {master_energy}')     # 강화 버튼 누르는 시점
        data = {'try_num': try_num, 'change_probability': change_probability, 'success_this_time': success_this_time, 'cumulative': cumulative, 'master_energy': master_energy}
        df_refining_data = df_refining_data.append(data, ignore_index=True)
        if master_energy >= 1 or change_probability >= 1: break
        fail_before = round(fail_before * (1 - change_probability), 5)
        master_energy = round(master_energy + change_probability * master_energy_fixed_value, 5)
        try_num += 1

    df_refining_data = df_refining_data.astype({'try_num': int})
    return df_refining_data


def data_group(*args):
    probability_list = args
    for i in probability_list:
        df_refining_data = calc_refining(i)
        filename = './db/refining/refining_' + str(i).replace('.', '_') + '.csv'
        df_refining_data.to_csv(filename, index=False)
        print(f'probability {i}% done.')


def calc_avg_num():
    path = './db/refining/'
    df_avg = pd.DataFrame()
    file_list = os.listdir(path)
    for file_name in file_list:
        refining_data = pd.read_csv(path + file_name)
        probability = file_name.replace('refining_', '').replace('.csv', '').replace('_', '.')
        max_num = len(refining_data)
        avg_num = 0
        for try_num, stt in zip(refining_data['try_num'], refining_data['success_this_time']):
            avg_num += try_num * stt

        data = {'probability': probability, 'avg_num': round(avg_num, 2), 'max_num': max_num}
        df_avg = df_avg.append(data, ignore_index=True)
        df_avg = df_avg.sort_values(by='max_num', ascending=False)

    filename = './db/avg_try_num.csv'
    df_avg.to_csv(filename, index=False)


def calcStepPrice():
    df_stepPrice = pd.DataFrame()

    df_itemPrice = pd.read_csv('./db/material_price.csv')
    df_avg = pd.read_csv('./db/avg_try_num.csv')
    df_weapon_step = pd.read_csv('./db/material/weapon_step.csv')
    df_armor_step = pd.read_csv('./db/material/armor_step.csv')

    honor_shard_list = list(df_itemPrice[df_itemPrice['itemName'].str.contains('명예의 파편 주머니')]['itemPrice'])
    honor_shard_price = round((honor_shard_list[0] / 500 + honor_shard_list[1] / 1000 + honor_shard_list[2] / 1500) / 3, 2)

    for weapon_step, armor_step in zip(df_weapon_step.to_dict('records'), df_armor_step.to_dict('records')):
        destruction_stone_price, guardian_stone_price, leap_stone_price, fusion_price = 0, 0, 0, 0
        print(weapon_step)
        if weapon_step['level'] == 'level_1302':
            destruction_stone_price = df_itemPrice[df_itemPrice['itemName'] == '파괴석 결정']['itemPrice'].values[0] / 10
            guardian_stone_price = df_itemPrice[df_itemPrice['itemName'] == '수호석 결정']['itemPrice'].values[0] / 10
            leap_stone_price = df_itemPrice[df_itemPrice['itemName'] == '명예의 돌파석']['itemPrice'].values[0]
            fusion_price = df_itemPrice[df_itemPrice['itemName'] == '하급 오레하 융화 재료']['itemPrice'].values[0]
        elif weapon_step['level'] == 'level_1340':
            destruction_stone_price = df_itemPrice[df_itemPrice['itemName'] == '파괴석 결정']['itemPrice'].values[0] / 10
            guardian_stone_price = df_itemPrice[df_itemPrice['itemName'] == '수호석 결정']['itemPrice'].values[0] / 10
            leap_stone_price = df_itemPrice[df_itemPrice['itemName'] == '위대한 명예의 돌파석']['itemPrice'].values[0]
            fusion_price = df_itemPrice[df_itemPrice['itemName'] == '중급 오레하 융화 재료']['itemPrice'].values[0]
        elif weapon_step['level'] == 'level_1390':
            destruction_stone_price = df_itemPrice[df_itemPrice['itemName'] == '파괴강석']['itemPrice'].values[0] / 10
            guardian_stone_price = df_itemPrice[df_itemPrice['itemName'] == '수호강석']['itemPrice'].values[0] / 10
            leap_stone_price = df_itemPrice[df_itemPrice['itemName'] == '경이로운 명예의 돌파석']['itemPrice'].values[0]
            fusion_price = df_itemPrice[df_itemPrice['itemName'] == '상급 오레하 융화 재료']['itemPrice'].values[0]
        elif weapon_step['level'] == 'level_1525':
            destruction_stone_price = df_itemPrice[df_itemPrice['itemName'] == '정제된 파괴강석']['itemPrice'].values[0] / 10
            guardian_stone_price = df_itemPrice[df_itemPrice['itemName'] == '정제된 수호강석']['itemPrice'].values[0] / 10
            leap_stone_price = df_itemPrice[df_itemPrice['itemName'] == '찬란한 명예의 돌파석']['itemPrice'].values[0]
            fusion_price = df_itemPrice[df_itemPrice['itemName'] == '최상급 오레하 융화 재료']['itemPrice'].values[0]

        prabability_data = df_avg[df_avg['probability'] == weapon_step['probability']].to_dict('records')[0]

        weapon_refining_once = round(weapon_step['destruction_stone'] * destruction_stone_price + weapon_step['leap_stone'] * leap_stone_price + weapon_step['fusion'] * fusion_price + weapon_step['honor_shard'] * honor_shard_price + weapon_step['gold'])
        weapon_refining_avg = round(weapon_refining_once * prabability_data['avg_num'])
        weapon_refining_max = round(weapon_refining_once * prabability_data['max_num'])
        armor_refining_once = round(armor_step['guardian_stone'] * guardian_stone_price + armor_step['leap_stone'] * leap_stone_price + armor_step['fusion'] * fusion_price + armor_step['honor_shard'] * honor_shard_price + armor_step['gold'])
        armor_refining_avg = round(armor_refining_once * prabability_data['avg_num'])
        armor_refining_max = round(armor_refining_once * prabability_data['max_num'])

        data = {'level': weapon_step['level'],
                'step': weapon_step['step'],
                'weaponOnce': weapon_refining_once,
                'weaponAvg': weapon_refining_avg,
                'weaponMax': weapon_refining_max,
                'armorOnce': armor_refining_once,
                'armorAvg': armor_refining_avg,
                'armorMax': armor_refining_max,
                }

        df_stepPrice = df_stepPrice.append(data, ignore_index=True)

    filename = './db/step_price.csv'
    df_stepPrice.to_csv(filename, index=False)


if __name__ == '__main__':

    # data_group(100, 60, 45, 30, 15, 10, 5, 4, 3, 1.5, 1, 0.5)
    # calc_avg_num()

    calcStepPrice()



