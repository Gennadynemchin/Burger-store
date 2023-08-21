from django.db import models
from django.utils import timezone


class PlaceGeoInfo(models.Model):
    lat = models.FloatField(verbose_name='широта', null=True, blank=True)
    lon = models.FloatField(verbose_name='долгота', null=True, blank=True)
    address = models.CharField(max_length=200, unique=True)
    request_date = models.DateTimeField(default=timezone.now)
