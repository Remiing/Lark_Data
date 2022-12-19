import requests
import json
import pandas as pd
import config
import os
import re
import yaml
import time


api_key = 'bearer ' + config.api_key


def get_characterInfo(characterName):
    url = 'https://developer-lostark.game.onstove.com/armories/characters/'

    # profiles: characterClass, battleLV, expeditionLV, itemLV, stat, power, vitality
    response = requests.get(url + characterName + '/profiles', headers={"authorization": api_key})
    if response.status_code == 200:
        characterProfile = json.loads(response.text)
        characterClass = characterProfile['CharacterClassName']
        battleLV = characterProfile['CharacterLevel']
        expeditionLV = characterProfile['ExpeditionLevel']
        stat = ','.join([f'{characterProfile["Stats"][i]["Type"]} {characterProfile["Stats"][i]["Value"]}' for i in [0, 1, 3]])
        itemLV = characterProfile['ItemMaxLevel'].replace(',', '')
        power = characterProfile["Stats"][6]['Value']
        vitality = characterProfile["Stats"][7]['Value']
        del characterProfile
    else:
        characterClass, battleLV, expeditionLV, itemLV, stat, power, vitality = '', 0, 0, 0, '', 0, 0

    # engravings: engraving_detail, engraving_simple
    response = requests.get(url + characterName + '/engravings', headers={"authorization": api_key})
    if response.status_code == 200:
        characterEngraving = json.loads(response.text)
        engraving_detail = ','.join(engraving['Name'] for engraving in characterEngraving['Effects'])
        engraving_simple = re.sub(r'[^0-9]', '', engraving_detail)
        del characterEngraving
    else:
        engraving_detail, engraving_simple = '', ''

    # equipment: equipmentLV, equipment_detail, accessory, accessory_engraving
    response = requests.get(url + characterName + '/equipment', headers={"authorization": api_key})
    if response.status_code == 200:
        characterEquipment = json.loads(response.text)
        equipmentLV, equipment_detail = [], []
        for equip in characterEquipment[:6]:
            equipmentLV.append(equip['Name'].replace('+', ''))
            equipType = equip['Type']
            equipTooltip = json.loads(equip['Tooltip'])
            equipQuality = equipTooltip['Element_001']['value']['qualityValue']
            equipment_detail.append(f'{equipType} {equipQuality}')
        equipmentLV = ','.join(equipmentLV)
        equipment_detail = ','.join(equipment_detail)
        accessory, accessory_engraving = [], []
        for acc in characterEquipment[6:11]:
            accType = acc['Type']
            accTooltip = json.loads(acc['Tooltip'])
            accQuality = accTooltip['Element_001']['value']['qualityValue']
            accNature = re.sub('[^가-힣\s]', '', accTooltip['Element_005']['value']['Element_001']).rstrip()
            accEngraving = []
            for i in range(2):
                engraving = accTooltip['Element_006']['value']['Element_000']['contentStr']['Element_00' + str(i)]['contentStr']
                engraving = ''.join(re.findall('(?<=>)[가-힣\s]+(?=<)|\+\d{1}', engraving))
                accEngraving.append(engraving)
            accessory.append(f'{accType} {accQuality} {accNature}')
            accessory_engraving.append('_'.join(accEngraving))
        accessory = ','.join(accessory)
        accessory_engraving = ','.join(accessory_engraving)
        del characterEquipment
    else:
        equipmentLV, equipment_detail, accessory, accessory_engraving = '', '', '', ''

    # cards: card
    response = requests.get(url + characterName + '/cards', headers={"authorization": api_key})
    if response.status_code == 200:
        characterCard = json.loads(response.text)
        card = ','.join(characterCard['Effects'][0]['Items'][-1]['Name'].rstrip(')').split(' ('))
        del characterCard
    else:
        card = ''

    # gems: gem_simple
    response = requests.get(url + characterName + '/gems', headers={"authorization": api_key})
    if response.status_code == 200:
        characterGem = json.loads(response.text)
        gems = characterGem['Gems'] if characterGem else []
        for gem in gems[:]:
            gemName = re.search(r'\d{,2}레벨 .(?=.의 보석)', gem['Name']).group().replace('레벨 ', '')
            gems[gems.index(gem)] = gemName
        gems = sorted(gems, key=lambda x: (-int(re.search(r'\d+', x).group()), x[-1]))
        counter = {}
        for gem in gems:
            if gem in counter:
                counter[gem] += 1
            else:
                counter[gem] = 1
        gem_simple = ','.join(f'{key} x{value}' for key, value in counter.items())
        del characterGem, gems
    else:
        gem_simple = ''

    character_data = {
        'name': characterName,
        'class': characterClass,
        'itemLV': itemLV,
        'battleLV': battleLV,
        'expeditionLV': expeditionLV,
        'engraving_simple': engraving_simple,
        'engraving_detail': engraving_detail,
        'stat': stat,
        'card': card,
        'gem_simple': gem_simple,
        'equipmentLV': equipmentLV,
        'equipment_detail': equipment_detail,
        'accessory': accessory,
        'accessory_engraving': accessory_engraving,
        'power': power,
        'vitality': vitality
    }

    return character_data


def members_to_dataframe():
    with open('./guild_members.yml', encoding='utf-8') as file:
        guild_members = yaml.load(file, Loader=yaml.FullLoader)
        guild_members = guild_members['main_character'] + guild_members['sub_character']

    df_members = pd.DataFrame()
    start = time.time()
    for member in guild_members:
        member_data = get_characterInfo(member)
        if member_data:
            df_members = df_members.append(member_data, ignore_index=True)
            print(member, 'complete')
        else:
            print(member, 'fail')
        time.sleep(3)
    print(time.time()-start)

    df_members = df_members.astype({'itemLV': float, 'battleLV': int, 'expeditionLV': int, 'power': int, 'vitality': int})
    df_members = df_members.sort_values(by='itemLV', ascending=False)
    filename = './db/members.csv'
    df_members.to_csv(filename, index=False)


def get_material_price():
    df_itemPrice = pd.DataFrame()
    itemCodeList = [
        66102003,       # 파괴석 결정
        66102004,       # 파괴강석
        66102005,       # 정제된 파괴강석
        66102103,       # 수호석 결정
        66102104,       # 수호강석
        66102105,       # 정제된 수호강석
        66110221,       # 명예의 돌파석
        66110222,       # 위대한 명예의 돌파석
        66110223,       # 경이로운 명예의 돌파석
        66110224,       # 찬란한 명예의 돌파석
        6861007,        # 하급 오레하 융화 재료
        6861008,        # 중급 오레하 융화 재료
        6861009,        # 상급 오레하 융화 재료
        6861011,        # 최상급 오레하 융화 재료
        66130131,       # 명예의 파편 주머니(소)
        66130132,       # 명예의 파편 주머니(중)
        66130133,       # 명예의 파편 주머니(대)
    ]
    for itemCode in itemCodeList:
        url = "https://developer-lostark.game.onstove.com/markets/items/" + str(itemCode)
        response = requests.get(url, headers={"authorization": api_key})
        if response.status_code == 200:
            itemData = json.loads(response.text)[0]
            itemName = itemData['Name']
            itemPrice = itemData['Stats'][0]['AvgPrice']
            print(f'{itemName}: {itemPrice}')
            data = {'itemName': itemName, 'itemPrice': itemPrice}
            df_itemPrice = df_itemPrice.append(data, ignore_index=True)
        else:
            print("error")
        time.sleep(1)

    filename = './db/material_price.csv'
    df_itemPrice.to_csv(filename, index=False)


if __name__ == '__main__':
    # get_material_price()
    members_to_dataframe()





