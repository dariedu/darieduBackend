from django.db import models

from user_app.models import User


class City(models.Model):
    city = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.city


class Location(models.Model):
    address = models.CharField(max_length=255)
    link = models.URLField(max_length=255)

    city = models.ForeignKey(City, on_delete=models.CASCADE)
    curator = models.ForeignKey(User, on_delete=models.CASCADE)


class RouteSheet(models.Model):
    map = models.URLField(max_length=255)

    def __str__(self):
        return self.map


class Address(models.Model):
    address = models.CharField(max_length=255)
    link = models.URLField(max_length=255)

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='address_location')
    route_sheet = models.ForeignKey(RouteSheet, on_delete=models.CASCADE)

    def __str__(self):
        return self.address


class Beneficiar(models.Model):
    phone = models.CharField(max_length=50, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)

    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='beneficiar_address')

    def __str__(self):
        return self.full_name
