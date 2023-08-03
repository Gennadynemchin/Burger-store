import os
import requests
from dotenv import load_dotenv
from geopy import distance
from foodcartapp.models import Restaurant, Order


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })

    try:
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    except requests.exceptions.HTTPError:
        return None

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


def compare_order_menu(api_key, orders, menu_items):
    # extract products from each order
    output_orders = []
    for order in orders:
        order_products = [item.product.name for item in order['items']]

        # compare order items and restaurant menu. Add distance to restaurants
        available_restaurants = []
        for item in menu_items:
            restaurant = list(item.keys())[0]
            restaurant_menu = list(item.values())[0]
            if set(order_products).issubset(restaurant_menu):
                coordinates_from = fetch_coordinates(api_key, item['restaurant_address'])
                coordinates_to = fetch_coordinates(api_key, order['address'])
                distance = calculate_distance(coordinates_from, coordinates_to)
                available_restaurants.append({restaurant: distance})
        order['available_restaurants'] = sorted(available_restaurants, key=lambda x: list(x.values())[0])
        output_orders.append(order)
    return output_orders


def get_restaurants_by_order_id(order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.items.all()
    order_products = [item.product.name for item in order_items]

    restaurants_menu = Restaurant.objects.get_restaurants_menu()
    available_restaurants = []
    for item in restaurants_menu:
        restaurant = list(item.keys())[0]
        restaurant_menu = list(item.values())[0]
        if set(order_products).issubset(restaurant_menu):
            available_restaurants.append(restaurant)
    return available_restaurants
