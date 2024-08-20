from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    tg_id = models.PositiveBigIntegerField(unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True)
    volunteer_hour = models.PositiveIntegerField(default=0)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    rating = models.ForeignKey('Rating', on_delete=models.CASCADE)

    city = models.ForeignKey('address_app.City', on_delete=models.CASCADE)

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.tg_id


class Rating(models.Model):
    level = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.level
