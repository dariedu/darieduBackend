from django.contrib import admin
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.urls import reverse

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
    tg_id = models.PositiveBigIntegerField(unique=True, db_index=True, verbose_name='ID')
    tg_username = models.CharField(max_length=255, blank=True, null=True, verbose_name='ник')
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='email')
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='фамилия')
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='имя')
    surname = models.CharField(max_length=255, blank=True, null=True, verbose_name='отчество')
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='телефон')
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='фото')
    photo_view = models.URLField(max_length=500, verbose_name='фотография пользователя', blank=True, null=True)
    volunteer_hour = models.PositiveIntegerField(default=0, verbose_name='часы')
    point = models.PositiveIntegerField(default=0, verbose_name='баллы')
    is_superuser = models.BooleanField(default=False, verbose_name='Сотрудник')
    is_staff = models.BooleanField(default=False, verbose_name='Куратор')
    is_admin = models.BooleanField(default=False, verbose_name='Администратор')
    is_confirmed = models.BooleanField(default=False, verbose_name='\u2714')  # confirmed тут ✔️
    consent_to_personal_data = models.BooleanField(default=False, verbose_name='Согласие',
                                                   help_text='Принятие условий договора-оферты')
    birthday = models.DateField(blank=True, null=True, verbose_name='дата рождения')
    is_adult = models.BooleanField(default=True, verbose_name='18+')
    rating = models.ForeignKey('Rating', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='уровень')

    city = models.ForeignKey('address_app.City', on_delete=models.PROTECT, blank=True, null=True,
                             related_name='users', verbose_name='город')
    interests = models.TextField(blank=True, null=True, verbose_name='интересы')
    metier = models.CharField(choices=METIERS, max_length=50, blank=True, null=True, verbose_name='род деятельности',
                              default=None)
    university = models.ForeignKey('user_app.University', on_delete=models.PROTECT, blank=True, null=True,
                                   related_name='users', verbose_name='университет')

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @admin.display(description="Город")
    def city_id(self, obj):
        return obj.city if obj.city else None

    @admin.display(description="Уровень")
    def rating_id(self, obj):
        return obj.rating.level if obj.rating else None

    def __str__(self):
        return f'{self.name} {self.last_name}, ' + (f' {self.tg_username}' if self.tg_username else f'{self.tg_id}')

    def get_absolute_url(self):
        return reverse('admin:user_app_user_change', args=[self.pk])

    def update_volunteer_hours(self, hours, point):
        self.volunteer_hour = hours
        self.point = point
        self.save(update_fields=['volunteer_hour', 'point'])

    def update_rating(self):
        new_rating = Rating.objects.filter(hours_needed__lt=self.volunteer_hour).order_by('-hours_needed').first()
        if new_rating and new_rating != self.rating:
            self.rating = new_rating
            self.save(update_fields=['rating'])

    def save(self, *args, **kwargs):
        if self.pk:  # Если объект уже существует
            old_instance = User.objects.get(pk=self.pk)
            self.old_point = old_instance.point
            self.old_volunteer_hour = old_instance.volunteer_hour
        else:
            self.old_point = self.point
            self.old_volunteer_hour = self.volunteer_hour
        super().save(*args, **kwargs)

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


class University(models.Model):
    """
    University model
    """
    name = models.CharField(max_length=255, verbose_name='название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'университет'
        verbose_name_plural = 'университеты'
