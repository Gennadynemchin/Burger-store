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
    return lat, lon


def calculate_distance(point_from, point_to):
    try:
        result = distance.distance(point_from, point_to).km
    except TypeError:
        return 'Distance has not been calculated'
    return result


if __name__ == '__main__':
    load_dotenv()
    api_key = os.getenv('YANDEX_API_KEY')
    coordinates_from = fetch_coordinates(api_key, '11111111')
    coordinates_to = fetch_coordinates(api_key, 'Нальчик, Ленина 110')
    distance = calculate_distance(coordinates_from, coordinates_to)
