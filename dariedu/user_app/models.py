from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    tg_id = models.PositiveBigIntegerField(unique=True, verbose_name='телеграм ID')
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='email')
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='фамилия')
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='имя')
    surname = models.CharField(max_length=255, blank=True, null=True, verbose_name='отчество')
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='телефон')
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='фото')
    volunteer_hour = models.PositiveIntegerField(default=0, verbose_name='волонтерские часы')
    is_superuser = models.BooleanField(default=False, verbose_name='Сотрудник')
    is_staff = models.BooleanField(default=False, verbose_name='Куратор')

    rating = models.ForeignKey('Rating', on_delete=models.CASCADE, blank=True, null=True, verbose_name='рейтинг')

    city = models.ForeignKey('address_app.City', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='users', verbose_name='город')

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.name} {self.last_name}, {self.tg_id}'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class Rating(models.Model):
    level = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.level

    class Meta:
        verbose_name = 'рейтинг'
        verbose_name_plural = 'рейтинги'
