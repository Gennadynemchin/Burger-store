from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
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


class OrderSerializer(ModelSerializer):
    products = ItemSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']
