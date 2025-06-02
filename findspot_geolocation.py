import os
import json
import requests

CACHE_FILE = "location_cache_geojson.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
else:
    cache = {}


def get_findspot_geojson(findspot):
    if findspot in cache:
        return cache[findspot]

    search_fs = findspot.replace("District", "")

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": search_fs,
        "format": "geojson"
    }
    headers = {
        "User-Agent": "coin-die-sna/0.1"
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        res_data = response.json()
        cache[findspot] = res_data

        with open(CACHE_FILE, "w") as file:
            json.dump(cache, file)

        print(f"Fetched: Findspot {findspot}")
        return res_data
    else:
        print(f"Error: Findspot {findspot}: {response.status_code} {response.text}")
        return None


def get_findspot_coordinate(findspot):
    geojson = get_findspot_geojson(findspot)
    lat = geojson["features"][0]["geometry"]["coordinates"][0]
    lon = geojson["features"][0]["geometry"]["coordinates"][1]

    return (lat, lon)


if __name__ == "__main__":
    latlon = get_findspot_coordinate("Manching")
    print(latlon)
