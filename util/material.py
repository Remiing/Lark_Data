import requests
from bs4 import BeautifulSoup
import yaml
import os


def crawling(code):
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

        material['step_' + str(i)] = {
            'basic_stone': basic_stone,
            'leap_stone': leap_stone,
            'fusion': fusion,
            'honor_shard': honor_shard,
            'gold': gold,
            'probability': probability
        }

    return material


def data_group(*args):
    result_dict = {}
    for i in args:
        code = None
        if i == 1525:
            code = '113487410'
        elif i == 1390:
            code = '113457410'
        elif i == 1340:
            code = '113337410'
        elif i == 1302:
            code = '113011410'
        result_dict['level_' + str(i)] = crawling(code)
        print(f'level_{i}% done.')
    return result_dict


def to_yml(data_dict):
    try:
        os.makedirs('../db/material')
    except FileExistsError as e:
        pass
    path = '../db/material/'
    filename = 'material' + '.yml'
    with open(path + filename, 'w') as file:
        yaml.dump(data_dict, file, default_flow_style=False)


if __name__ == '__main__':
    material = data_group(1302, 1340, 1390, 1525)
    to_yml(material)