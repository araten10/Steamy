import json
import random
from time import sleep

import requests

from steam import Steam

steam = Steam()

converted_dict = {}

sorted_ids = [int(i) for i in steam.game_ids]
sorted_ids.sort()

for game_id in sorted_ids:
    try:
        store_url = "https://store.steampowered.com/api/appdetails?appids=" + str(game_id)
        name = requests.get(store_url).json()[str(game_id)]["data"]["name"]
        converted_dict[str(game_id)] = name
        print(f"{converted_dict[str(game_id)]} added to dict. Total games: {len(converted_dict)}")
    except:
        print(f"Error in getting name for ID {game_id}. Most likely a program and not a game. Skipping...")
    sleep(random.uniform(1.6, 2))

with open("dumped_game_list.json", "w") as f:
    json.dump(converted_dict, f)
