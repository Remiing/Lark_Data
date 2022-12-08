import requests
import json
import pandas as pd
import config

api_key = config.api_key

def get_characterInfo(characterName):
    url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + characterName
    response = requests.get(url, headers={"X-Riot-Token": api_key})
    if response.status_code == 200:
        summoners = json.loads(response.text)
        return summoners
    else:
        print("error")









if __name__ == '__main__':





