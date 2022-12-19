import requests
from bs4 import BeautifulSoup
import yaml
import os
import pandas as pd


def crawling(type, code):
    url = 'https://lostark.inven.co.kr/dataninfo/item/?code=' + code
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    steps = soup.select('.enchant_info > .craft_wrap')
    material = {}
    for i, step in enumerate(steps, start=1):

        basic_stone = int(step.select_one('.material > ul > li:nth-child(1) > div > a > span > em').text.replace('x', ''))   # 파괴석 or 수호석
        leap_stone = int(step.select_one('.material > ul > li:nth-child(2) > div > a > span > em').text.replace('x', ''))    # 돌파석
        fusion = step.select_one('.material > ul > li:nth-child(3) > div > a > span > em')
        fusion = int(fusion.text.replace('x', '')) if fusion else 0                                                          # 오레하 융화 재료
        price = step.select_one('.craft_txt > p:nth-child(2)').text.replace('[재련 비용] ', '').split(', ')
        honor_shard = int(price[0].replace(',', '').replace('명예의 파편', ''))                                                # 명예의 파편
        gold = int(price[2].replace(',', '').replace('골드', '')) if len(price) > 2 else 0                                    # 재련 골드
        probability = step.select_one('.craft_txt > p:nth-child(3)').text.replace('[기본 성공률] ', '').replace('%', '')       # 강화 확률

        step_dict = {
            'leap_stone': leap_stone,
            'fusion': fusion,
            'honor_shard': honor_shard,
            'gold': gold,
            'probability': probability
        }
        if type == 'weapon':
            step_dict['destruction_stone'] = basic_stone
        elif type == 'armor':
            step_dict['guardian_stone'] = basic_stone

        material['step_' + str(i)] = step_dict

    return material


def data_group(type, *args):
    result_dict = {}
    for i in args:
        code = None
        if type == 'weapon':
            if i == 1525:
                code = '113487410'
            elif i == 1390:
                code = '113457410'
            elif i == 1340:
                code = '113337410'
            elif i == 1302:
                code = '113011410'
        elif type == 'armor':
            if i == 1525:
                code = '113487414'
            elif i == 1390:
                code = '113457414'
            elif i == 1340:
                code = '113337414'
            elif i == 1302:
                code = '113111414'
        result_dict['level_' + str(i)] = crawling(type, code)
        print(f'{type} level_{i} done.')

    return type, result_dict


def to_yml(data_dict):
    path = './db/material/'
    filename = data_dict[0] + '_material' + '.yml'
    with open(path + filename, 'w') as file:
        yaml.dump(data_dict[1], file, default_flow_style=False)


def to_csv(data_dict):
    df_material = pd.DataFrame()
    for level, level_dict in data_dict[1].items():
        for step, step_dict in level_dict.items():
            data = step_dict
            data['step'] = step
            data['level'] = level
            df_material = df_material.append(data, ignore_index=True)

    if data_dict[0] == 'weapon':
        df_material = df_material.astype({'destruction_stone': int, 'leap_stone': int, 'fusion': int, 'honor_shard': int, 'gold': int})
        df_material = df_material[['level', 'step', 'destruction_stone', 'leap_stone', 'fusion', 'honor_shard', 'gold', 'probability']]
    elif data_dict[0] == 'armor':
        df_material = df_material.astype({'guardian_stone': int, 'leap_stone': int, 'fusion': int, 'honor_shard': int, 'gold': int})
        df_material = df_material[['level', 'step', 'guardian_stone', 'leap_stone', 'fusion', 'honor_shard', 'gold', 'probability']]

    df_material.to_csv('./db/material/' + data_dict[0] + '_step.csv', index=False)


if __name__ == '__main__':
    material = data_group('weapon', 1302, 1340, 1390, 1525)
    to_csv(material)
    material = data_group('armor', 1302, 1340, 1390, 1525)
    to_csv(material)

