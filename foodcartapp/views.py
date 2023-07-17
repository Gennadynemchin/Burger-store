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
from rest_framework.serializers import ModelSerializer, ListField, ValidationError
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import io


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


class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'product', 'quantity']

    def check_product(self, product):
        if not Product.objects.filter(id=product.get('product')):
            raise ValidationError('ID ERROR')


class OrderSerializer(ModelSerializer):
    products = ItemSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    validated_products = []
    for product in request.data['products']:
        product_serializer = ItemSerializer(data=product)
        product_serializer.is_valid(raise_exception=True)
        product_serializer.check_product(product)
        validated_products.append(product_serializer.validated_data)

    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address']
    )

    positions = []
    for product in validated_products:
        positions.append(Item(
            order=order,
            product=Product.objects.get(pk=product['product'].id),
            quantity=product['quantity']
        ))
    Item.objects.bulk_create(positions)
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
