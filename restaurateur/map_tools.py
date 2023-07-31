import os
import requests
from dotenv import load_dotenv
from geopy import distance


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def calculate_distance(lon_from, lat_from, lon_to, lat_to):
    from_point = (lat_from, lon_from)
    to_point = (lat_to, lon_to)
    result = distance.distance(from_point, to_point).km
    return result


if __name__ == '__main__':
    load_dotenv()
    api_key = os.getenv('YANDEX_API_KEY')
    coordinates_from = fetch_coordinates(api_key, 'Москва, Калужское шоссе, 104')
    coordinates_to = fetch_coordinates(api_key, 'Нальчик, Ленина 110')
    distance = calculate_distance(coordinates_from[0], coordinates_from[1], coordinates_to[0], coordinates_to[1])
