import os
import pandas as pd


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
        filename = '../db/refining/refining_' + str(i).replace('.', '_') + '.csv'
        df_refining_data.to_csv(filename, index=False)
        print(f'probability {i}% done.')


def calc_avg_num():
    path = '../db/refining/'
    df_avg = pd.DataFrame()
    file_list = os.listdir(path)
    print(file_list)
    for file_name in file_list:
        refining_data = pd.read_csv(path + file_name)
        print(refining_data)
        probability = file_name.replace('refining_', '').replace('.csv', '').replace('_', '.')
        max_num = len(refining_data)
        avg_num = 0
        for try_num, stt in zip(refining_data['try_num'], refining_data['success_this_time']):
            avg_num += try_num * stt

        data = {'probability': probability, 'avg_num': avg_num, 'max_num': max_num}
        df_avg = df_avg.append(data, ignore_index=True)
        df_avg = df_avg.sort_values(by='max_num', ascending=False)

    print(df_avg)
    filename = '../db/avg_try_num.csv'
    df_avg.to_csv(filename, index=False)


if __name__ == '__main__':
    try:
        os.makedirs('../db/refining')
    except FileExistsError as e:
        pass

    data_group(100, 60, 45, 30, 15, 10, 5, 4, 3, 1.5, 1, 0.5)
    calc_avg_num()



