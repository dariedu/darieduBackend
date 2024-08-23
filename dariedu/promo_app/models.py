from django.db import models

from address_app.models import City
from user_app.models import User


class Promotion(models.Model):
    category = models.CharField(max_length=255, verbose_name='категория')
    name = models.CharField(max_length=255, verbose_name='название')
    price = models.PositiveIntegerField(verbose_name='стоимость')
    description = models.TextField(blank=True, null=True, verbose_name='описание')
    date = models.DateTimeField(verbose_name='дата')
    quantity = models.PositiveIntegerField(verbose_name='количество')
    for_curators_only = models.BooleanField(default=False, verbose_name='только для кураторов')
    is_active = models.BooleanField(default=True, verbose_name='активная')
    file = models.FileField(upload_to='promotion/', blank=True, null=True, verbose_name='файл')  # TODO: upload to where ?

    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, verbose_name='город')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='получатель')

    def __str__(self):
        return self.name
