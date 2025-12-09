import json
import os
import random
from time import sleep

import requests

from steam import Steam

steam = Steam()

converted_dict = {}

sorted_ids = [int(i) for i in steam.game_ids]
sorted_ids.sort()

if os.path.isfile("game_list.json"):
    with open("game_list.json", "r") as f:
        game_list = json.load(f)

print(f"{len(sorted_ids)} steam IDs found. Scraping names for these now...")

if "game_list" in globals():
    print(f"There are {len(game_list.keys())} games already in the database. These will be skipped if detected.")

for game_id in sorted_ids:
    try:
        if "game_list" in globals():
            if str(game_id) in game_list.keys():
                print(f'Game ID {game_id} already found in database as "{game_list[str(game_id)]}". Skipping...')
                continue
        # Don't take this out! this is a rate limiter so steam doesn't block requests.
        sleep(random.uniform(1.6, 2))
        store_url = "https://store.steampowered.com/api/appdetails?appids=" + str(game_id)
        name = requests.get(store_url).json()[str(game_id)]["data"]["name"]
        converted_dict[str(game_id)] = name
        print(f"{converted_dict[str(game_id)]} added to dict. Total games: {len(converted_dict)}")
    except KeyError:
        print(f"Error in getting name for ID {game_id}. Most likely a program and not a game, or removed from the steam store. Skipping...")

with open("dumped_game_list.json", "w") as f:
    json.dump(converted_dict, f, indent=2)
