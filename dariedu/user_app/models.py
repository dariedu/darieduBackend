from django.contrib import admin
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from dariedu.settings import CURRENT_HOST
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    METIERS = (
        ('schoolchild', 'Школьник'),
        ('student', 'Студент'),
        ('work_on_himself', 'Работаю на себя'),
        ('work_for_hire', 'Работаю по найму'),
        ('pensioner', 'Пенсионер'),
        ('other', 'Другое'),
    )
    tg_id = models.PositiveBigIntegerField(unique=True, db_index=True, verbose_name='телеграм ID')
    tg_username = models.CharField(max_length=255, blank=True, null=True, verbose_name='никнэйм')
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='email')
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='фамилия')
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='имя')
    surname = models.CharField(max_length=255, blank=True, null=True, verbose_name='отчество')
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='телефон')
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='фото')
    photo_view = models.URLField(max_length=500, verbose_name='фотография пользователя', blank=True, null=True)
    # avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='аватарка')
    volunteer_hour = models.PositiveIntegerField(default=0, verbose_name='волонтерские часы')
    point = models.PositiveIntegerField(default=0, verbose_name='баллы')
    is_superuser = models.BooleanField(default=False, verbose_name='Сотрудник')
    is_staff = models.BooleanField(default=False, verbose_name='Куратор')
    consent_to_personal_data = models.BooleanField(default=False, verbose_name='Согласие',
                                                   help_text='Принятие условий договора-оферты')
    birthday = models.DateField(blank=True, null=True, verbose_name='дата рождения')
    is_adult = models.BooleanField(default=True, verbose_name='18+')
    rating = models.ForeignKey('Rating', on_delete=models.CASCADE, blank=True, null=True, verbose_name='рейтинг')

    city = models.ForeignKey('address_app.City', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='users', verbose_name='город')
    interests = models.TextField(blank=True, null=True, verbose_name='интересы')
    metier = models.CharField(choices=METIERS, max_length=50, blank=True, null=True, verbose_name='род деятельности',
                              default=None)

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @admin.display(description="Город")
    def city_id(self, obj):
        return obj.city if obj.city else None

    @admin.display(description="Рейтинг")
    def rating_id(self, obj):
        return obj.rating.level if obj.rating else None

    def __str__(self):
        return f'{self.name} {self.last_name}, ' + (f' {self.tg_username}' if self.tg_username else f'{self.tg_id}')

    def get_absolute_url(self):
        return f'{CURRENT_HOST}/admin/user_app/user/{self.pk}/change/'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


###### PROXIES FOR ADMIN PANEL ######
class Volunteer(User):
    class Meta:
        proxy = True


class Curator(User):
    class Meta:
        proxy = True


class Employee(User):
    class Meta:
        proxy = True


class Rating(models.Model):
    """
    Maybe we don't need separate model for rating
    """
    level = models.CharField(max_length=255, verbose_name='рейтинг')
    hours_needed = models.PositiveIntegerField(verbose_name='часы')

    def __str__(self):
        return self.level

    class Meta:
        verbose_name = 'рейтинг'
        verbose_name_plural = 'рейтинги'
