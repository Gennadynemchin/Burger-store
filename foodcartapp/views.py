from django.http import JsonResponse
from django.templatetags.static import static
import json


from .models import Product, Order, Item


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    frontend_data = json.loads(request.body.decode())
    firstname = frontend_data['firstname']
    lastname = frontend_data['lastname']
    phonenumber = frontend_data['phonenumber']
    address = frontend_data['address']
    products = frontend_data['products']

    order = Order.objects.create(firstname=firstname, lastname=lastname, phonenumber=phonenumber, address=address)
    for product in products:
        Item.objects.create(product=Product.objects.get(id=product['product']), order=order, qty=product['quantity'])

    print(f'Заказ успешно добавлен: {order}, {order.items.all()}')
    return JsonResponse({})
