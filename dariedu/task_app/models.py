from django.db import models

from user_app.models import User
from address_app.models import RouteSheet, City


class Delivery(models.Model):
    date = models.DateField()
    price = models.PositiveIntegerField()
    is_free = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)

    volunteer = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    route_sheet = models.ForeignKey(RouteSheet, on_delete=models.CASCADE)


class Task(models.Model):
    category = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    duration = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    is_active = models.BooleanField()  # TODO: default: true of false ?

    city = models.ForeignKey(City, on_delete=models.CASCADE)
    curator = models.ForeignKey(User, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
