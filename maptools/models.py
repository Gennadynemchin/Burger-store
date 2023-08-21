from django.db import models
from django.utils import timezone


class PlaceGeoInfo(models.Model):
    lat = models.FloatField(verbose_name='широта')
    lon = models.FloatField(verbose_name='долгота')
    address = models.CharField(max_length=200, unique=True)
    request_date = models.DateTimeField(default=timezone.now)
