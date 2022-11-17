import os
import pandas as pd


def calc(probability):
    try_df = pd.DataFrame()
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
        try_df = try_df.append(data, ignore_index=True)
        if master_energy >= 1: break
        fail_before = round(fail_before * (1 - change_probability), 5)
        master_energy = round(master_energy + change_probability * master_energy_fixed_value, 5)
        try_num += 1

    # 평균 = 1*0.1500 + 2*0.1402 + 3*0.1278 ... num * success_this_time
    # avg = 0
    # for i, prob in zip(try_df['num'], try_df['success_this_time']):
    #     avg += i*prob
    # print(avg)

    try_df = try_df.astype({'try_num': int})
    return try_df


def data_group(*args):
    probability_list = args
    result_dict = {}
    for i in probability_list:
        result_dict[i] = calc(i)
        print(f'probability {i}% done.')
    return result_dict


def to_csv(data_dict):
    try:
        os.mkdir('./db')
    except FileExistsError as e:
        pass
    for key, value in data_dict.items():
        path = './db/'
        filename = 'refining_' + str(key).replace('.', '_') + '.csv'
        value.to_csv(path + filename, index=False)