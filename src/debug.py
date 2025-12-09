import subprocess
import sys
from pathlib import Path

# TODO: Running individual features
print("""Which feature would you like to run?
0. Quit
1. Main Program (__main__.py)
2. Game Scraper (game_list_scraper.py)""")

MAIN_PATH = str(Path(__file__) / "__main__.py")
SCRAPER_PATH = str(Path(__file__) / "game_list_scraper.py")

processes = [
    MAIN_PATH,
    SCRAPER_PATH
]  # fmt: off

while True:
    num = input("Select number: ")
    try:
        num = int(num)
    except Exception:
        print("Input must be an integer")
        continue

    if num == 0:
        break
    elif num > 0 and num <= len(processes):
        subprocess.run([sys.executable] + processes[num - 1])
        print("Done")
    else:
        print("Input must be between 0 and 2")

print("Goodbye!")
