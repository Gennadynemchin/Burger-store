from .map_tools import fetch_coordinates, calculate_distance


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
