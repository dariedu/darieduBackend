from django.db import models

from user_app.models import User


class City(models.Model):
    city = models.CharField(max_length=255, unique=True, verbose_name='город')

    def __str__(self):
        return self.city


class Location(models.Model):
    address = models.CharField(max_length=500, verbose_name='адрес')
    link = models.URLField(max_length=500, verbose_name='ссылка')

    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='город')
    curator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='куратор')


class RouteSheet(models.Model):
    map = models.URLField(max_length=500, verbose_name='карта')

    def __str__(self):
        return self.map


class Address(models.Model):
    address = models.CharField(max_length=255, verbose_name='адрес')
    link = models.URLField(max_length=500, verbose_name='ссылка')

    location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                 related_name='address_location', verbose_name='локация')
    route_sheet = models.ForeignKey(RouteSheet, on_delete=models.CASCADE,
                                    related_name='address_route_sheet', verbose_name='маршрутный лист')

    def __str__(self):
        return self.address


class Beneficiar(models.Model):
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='телефон')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    comment = models.TextField(blank=True, null=True, verbose_name='комментарий')

    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                related_name='beneficiar_address', verbose_name='адрес')

    def __str__(self):
        return self.full_name
