import requests
import random
import json
from time import sleep

from steam import Steam

steam = Steam()

converted_dict = {}

for game_id in steam.game_ids:
    try:
        store_url = "https://store.steampowered.com/api/appdetails?appids=" + game_id
        name = requests.get(store_url).json()[game_id]['data']['name']
        converted_dict[game_id] = name
        print(f"{converted_dict[game_id]} added to dict. Total games: {len(converted_dict)}")
    except:
        print(f"Error in getting name for ID {game_id}. Most likely a program and not a game. Skipping...")
    sleep(random.uniform(1.6, 2))

with open("dumped_game_list.json", "w") as f:
    json.dump(converted_dict, f)
