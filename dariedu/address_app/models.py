from django.db import models

from user_app.models import User


class City(models.Model):
    city = models.CharField(max_length=255, unique=True, verbose_name='город')

    def __str__(self):
        return self.city

    class Meta:
        verbose_name = 'город'
        verbose_name_plural = 'города'


class Location(models.Model):
    address = models.CharField(max_length=500, verbose_name='адрес')
    link = models.URLField(max_length=500, verbose_name='ссылка')
    subway = models.CharField(max_length=255, blank=True, null=True, verbose_name='метро')

    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='город')
    curator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='куратор')

    class Meta:
        verbose_name = 'локация'
        verbose_name_plural = 'локации'


class RouteSheet(models.Model):
    map = models.URLField(max_length=500, verbose_name='карта')
    address = models.ManyToManyField('Address', on_delete=models.CASCADE, through='RoureAddress',
                                     related_name='route_address', verbose_name='адреса')

    def __str__(self):
        return self.map

    def display_address(self):
        return ', '.join([(address.address, address.location) for address in self.route_address.all()])

    class Meta:
        verbose_name = 'маршрутный лист'
        verbose_name_plural = 'маршрутные листы'


class Address(models.Model):
    address = models.CharField(max_length=255, verbose_name='адрес')
    link = models.URLField(max_length=500, verbose_name='ссылка')

    location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                 related_name='address_location', verbose_name='локация')

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'адреса'


class RoureAddress(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name='адрес')
    route_sheet = models.ForeignKey(RouteSheet, on_delete=models.CASCADE, verbose_name='маршрутный лист')


class Beneficiar(models.Model):
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='телефон')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    comment = models.TextField(blank=True, null=True, verbose_name='комментарий')

    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                related_name='beneficiar_address', verbose_name='адрес')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'благополучатель'
        verbose_name_plural = 'благополучатели'
