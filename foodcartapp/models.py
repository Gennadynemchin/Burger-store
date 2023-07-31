import datetime

from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F
from django.utils import timezone


class OrdersQuerySet(models.QuerySet):
    def get_active_orders(self):
        orders = []
        for order in self.exclude(status='FN').prefetch_related('items__product'):
            order_items = order.items.all()
            order_sum = sum(item.price for item in order_items)
            orders.append({'id': order.id,
                           'status': order.get_status_display(),
                           'items': order_items,
                           'sum': order_sum,
                           'firstname': order.firstname,
                           'lastname': order.lastname,
                           'phonenumber': order.phonenumber,
                           'address': order.address,
                           'comment': order.comment,
                           'payment_method': order.get_payment_method_display(),
                           'prepared_by': order.prepared_by})
        return orders


class RestaurantQuerySet(models.QuerySet):
    def get_restaurants_menu(self):
        context = []
        for restaurant in self.all():
            products_in_menu = []
            for restaurant_menu in restaurant.menu_items.all():
                products_in_menu.append(restaurant_menu.product.name)
            context.append({restaurant.name: products_in_menu})
        return context


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    objects = RestaurantQuerySet.as_manager()

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=300,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):

    ORDER_STATUS = (
        ('1', 'RECEIVED'),
        ('2', 'PREPARING'),
        ('3', 'DELIVERING'),
        ('4', 'FINISHED'),
    )

    PAYMENT_METHODS = (
        ('1', 'CARD'),
        ('2', 'CASH'),
    )

    firstname = models.CharField(max_length=100, db_index=True, null=False)
    lastname = models.CharField(max_length=100, db_index=True, null=False)
    phonenumber = PhoneNumberField(max_length=14, blank=False, null=False)
    address = models.CharField(max_length=200, null=False)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='1', db_index=True)
    comment = models.TextField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='1', db_index=True)
    prepared_by = models.ForeignKey(Restaurant,
                                    verbose_name='ресторан, принявший заказ',
                                    related_name='orders',
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL)
    objects = OrdersQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname}, {self.phonenumber}, {self.address}"


class Item(models.Model):
    product = models.ForeignKey(Product, verbose_name='продукт', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='items', verbose_name='заказ', on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(verbose_name='количество')
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                default=0,
                                verbose_name='цена',
                                validators=[MinValueValidator(limit_value=0)]
                                )

    class Meta:
        verbose_name = 'позиция'
        verbose_name_plural = 'позиции'

    def __str__(self):
        return f"{self.product.name}, {self.quantity}"
