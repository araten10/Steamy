import subprocess
import sys
from pathlib import Path

print("""Which feature would you like to run?
0. Quit
1. Main Program (__main__.py)""")

src = Path(__file__).parent / "src"

processes = [
    [src / "__main__.py"]
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
        print(f"Input must be between 0 and {len(processes)}")

print("Goodbye!")
