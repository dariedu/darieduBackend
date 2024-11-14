from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.html import format_html


User = get_user_model()


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
    description = models.TextField(blank=True, null=True, verbose_name='описание')

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

    def __str__(self):
        return str(self.name)

    @admin.display(description='адреса')
    def display_address(self):
        return format_html('<br>'.join([address.address for address in self.address.all()]))

    @admin.display(description='куратор локации')
    def display_curator(self):
        return self.location.curator

    class Meta:
        verbose_name = 'маршрутный лист'
        verbose_name_plural = 'маршрутные листы'


class RouteAssignment(models.Model):
    route_sheet = models.ForeignKey(RouteSheet, on_delete=models.CASCADE, related_name='assignments',
                                    verbose_name='маршрутный лист')
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='route_assignments',
                                  verbose_name='волонтёр')
    delivery = models.ForeignKey('task_app.Delivery', on_delete=models.CASCADE, related_name='route_assignments',
                                 verbose_name='доставка')

    def __str__(self):
        return f'{self.route_sheet.name} - {self.volunteer}'

    class Meta:
        verbose_name = 'маршрутный лист волонтёра'
        verbose_name_plural = 'маршрутные листы волонтёров'


class Address(models.Model):
    address = models.CharField(max_length=255, verbose_name='адрес')
    link = models.URLField(max_length=500, verbose_name='ссылка', blank=True, null=True)

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='address_location',
                                 verbose_name='локация', blank=True, null=True)
    route_sheet = models.ForeignKey(RouteSheet, on_delete=models.CASCADE, related_name='address',
                                    verbose_name='маршрутный лист', blank=True, null=True)

    def __str__(self):
        return f'{self.address}'

    @admin.display(description='маршрутный лист')
    def display_route_sheet(self):
        return self.route_sheet.name

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'адреса'

    @admin.display(description='благополучатели')
    def display_beneficiar(self):
        return format_html('<br>'.join([beneficiar.full_name for beneficiar in self.beneficiar.all()]))

    @admin.display(description='комментарии')
    def display_comment(self):
        return format_html('<br>'.join([beneficiar.comment for beneficiar in self.beneficiar.all()]))


class Beneficiar(models.Model):

    CHOICES = (
        ('да', 'да'),
        ('в отъезде', 'в отъезде'),
        ('архив', 'архив')
    )
    CATEGORY = (
        ('Пенсионер', 'Пенсионер'),
        ('Ветеран ВОВ', 'Ветеран ВОВ'),
        ('Ветеран труда', 'Ветеран труда'),
        ('Инвалид I группы', 'Инвалид I группы'),
        ('Инвалид II группы', 'Инвалид II группы'),
        ('Инвалид III группы', 'Инвалид III группы'),
    )

    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='телефон')
    second_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='дополнительный телефон')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    comment = models.TextField(blank=True, null=True, verbose_name='комментарий')
    category = models.CharField(choices=CATEGORY, max_length=255, blank=True, null=True, default=None,
                                verbose_name='категория')
    presence = models.CharField(choices=CHOICES, max_length=15, default='да', verbose_name='присутствие')
    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                related_name='beneficiar', verbose_name='адрес')
    photo_link = models.URLField(max_length=500, verbose_name='просмотр фото', blank=True, null=True)

    def __str__(self):
        return f'{self.full_name}, {self.phone}\n{self.comment}'

    class Meta:
        verbose_name = 'благополучатель'
        verbose_name_plural = 'благополучатели'
