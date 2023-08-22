from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ValidationError

from .models import Item
from .models import Order
from .models import Product


class PhoneNumberSerializer(serializers.Serializer):
    number = PhoneNumberField(region="RU")


class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'product', 'quantity']

    def check_product(self, product):
        if not Product.objects.filter(id=product.get('product')):
            raise ValidationError('ID ERROR')

    def create(self, validated__data):
        return Item.objects.create()


class OrderSerializer(ModelSerializer):
    products = ItemSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(firstname=validated_data['firstname'],
                                     lastname=validated_data['lastname'],
                                     phonenumber=validated_data['phonenumber'],
                                     address=validated_data['address'])
        order_products = []
        for product in products:
            order_products.append(Item(
                order=order,
                product=Product.objects.get(pk=product['product'].id),
                quantity=product['quantity'],
                price=product['product'].price
            ))

        Item.objects.bulk_create(order_products)

        return order



