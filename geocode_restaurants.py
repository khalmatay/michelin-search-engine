import os

import requests

api_key = os.getenv("API_KEY")
from dotenv import load_dotenv

load_dotenv()


def get_region_and_coordinates(city):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city},Italy&key={api_key}"
    response = requests.get(url)
    data = response.json()

    region = None
    latitude = None
    longitude = None

    if data['status'] == "OK":
        location = data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']

        for component in data['results'][0]['address_components']:
            if "administrative_area_level_1" in component['types']:
                region = component['long_name']
                break

    return region, latitude, longitude
