import requests
import random
from bs4 import BeautifulSoup
from time import sleep

from steam import Steam

steam = Steam()

converted_dict = {}

for game_id in steam.game_ids:
    store_url = "https://store.steampowered.com/app/" + game_id
    response = requests.get(store_url)
    steam_soup = BeautifulSoup(response.text, features="html.parser")
    converted_dict[steam_soup.find("div", {"class": "apphub_AppName"}).text] = game_id
    print(converted_dict)
    sleep(random.uniform(1, 2))
