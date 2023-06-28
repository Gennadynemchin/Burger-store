from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import renderers, serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import Product, Order, Item
import phonenumbers
from phonenumbers import NumberParseException


class PhoneNumberSerializer(serializers.Serializer):
    number = PhoneNumberField(region="RU")





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


@api_view(['POST'])
def register_order(request):
    frontend_data = request.data
    firstname = frontend_data.get('firstname')
    lastname = frontend_data.get('lastname')
    phonenumber = frontend_data.get('phonenumber')
    address = frontend_data.get('address')
    products = frontend_data.get('products')
    validate_data = {"firstname": firstname, "lastname": lastname, "address": address}
    error_attributes = []

    for attribute_name, attribute_value in validate_data.items():
        if not attribute_value or type(attribute_value) != str:
            error_attributes.append({"error": f"{attribute_name} has invalid data type or does not exist. Must be string"})
    try:
        if not phonenumbers.is_valid_number(phonenumbers.parse(phonenumber, 'RU')):
            error_attributes.append({"error": f"phonenumber is not valid"})
    except NumberParseException:
        error_attributes.append({"error": f"phonenumber is not recognized"})
    if len(products) < 1:
        error_attributes.append({"error": "products list cannot be empty"})
    if not isinstance(products, list):
        error_attributes.append({"error": "products must be stored in list"})
    for product in products:
        is_product_exists = Product.objects.filter(id=product['product'])
        if not is_product_exists:
            error_attributes.append({"error": f"product does not exist"})
    if error_attributes:
        response = {"status": error_attributes}
        return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

    else:
        order = Order.objects.create(firstname=firstname, lastname=lastname, phonenumber=phonenumber, address=address)
        for product in products:
            Item.objects.create(product=Product.objects.get(id=product['product']), order=order, qty=product['quantity'])
        response = {"status": [{"200": "ok"}]}
        return Response(response, status=status.HTTP_200_OK)
