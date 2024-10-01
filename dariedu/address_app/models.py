from django.contrib import admin
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
    link = models.URLField(max_length=500, verbose_name='ссылка', blank=True, null=True)
    subway = models.CharField(max_length=255, blank=True, null=True, verbose_name='метро')

    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='город')
    curator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='куратор',
                                blank=True, null=True)
    media_files = models.FileField(blank=True, null=True, verbose_name='файлы', upload_to='location_files')

    class Meta:
        verbose_name = 'локация'
        verbose_name_plural = 'локации'

    def __str__(self):
        return f'{self.subway}, {self.address}'


class RouteSheet(models.Model):
    name = models.CharField(verbose_name='название', unique=True, max_length=500)
    map = models.URLField(max_length=500, blank=True, null=True, verbose_name='карта')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='route_sheets', verbose_name='локация')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='route_sheets', verbose_name='волонтер',
                             blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def display_address(self):
        return ' | '.join([address.address for address in self.address.all()])

    class Meta:
        verbose_name = 'маршрутный лист'
        verbose_name_plural = 'маршрутные листы'


class Address(models.Model):
    address = models.CharField(max_length=255, verbose_name='адрес')
    link = models.URLField(max_length=500, verbose_name='ссылка', blank=True, null=True)

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='address_location',
                                 verbose_name='локация', blank=True, null=True)
    route_sheet = models.ForeignKey(RouteSheet, on_delete=models.CASCADE, related_name='address',
                                    verbose_name='маршрутный лист', blank=True, null=True)

    def __str__(self):
        return f'{self.address}\n{self.link}'

    @admin.display(description='маршрутный лист')
    def display_route_sheet(self):
        return self.route_sheet.name

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'адреса'

    def display_beneficiar(self):
        return '|'.join([beneficiar.full_name for beneficiar in self.beneficiar.all()])


class Beneficiar(models.Model):
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='телефон')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    comment = models.TextField(blank=True, null=True, verbose_name='комментарий')

    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                related_name='beneficiar', verbose_name='адрес')

    def __str__(self):
        return f'{self.full_name}, {self.phone}\n{self.comment}'

    class Meta:
        verbose_name = 'благополучатель'
        verbose_name_plural = 'благополучатели'
