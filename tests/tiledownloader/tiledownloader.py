import os
import requests
from time import sleep

def download_tile(z, x, y, base_path="tiles"):
    url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    tile_dir = os.path.join(base_path, str(z), str(x))
    os.makedirs(tile_dir, exist_ok=True)
    file_path = os.path.join(tile_dir, f"{y}.png")

    if os.path.exists(file_path):
        print(f"✓ Already exists: {z}/{x}/{y}")
        return

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"✓ Downloaded: {z}/{x}/{y}")
        else:
            print(f"✗ Failed: {z}/{x}/{y} ({response.status_code})")
    except Exception as e:
        print(f"✗ Error: {z}/{x}/{y} ({e})")

# Download tiles from zoom 0 to 5
for z in range(0, 6):
    max_tile = 2 ** z
    for x in range(max_tile):
        for y in range(max_tile):
            download_tile(z, x, y)
            sleep(0.1)  # Be kind to the server
