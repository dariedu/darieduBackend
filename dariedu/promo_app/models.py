from django.db import models

from address_app.models import City
from user_app.models import User


class Promotion(models.Model):
    category = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    quantity = models.PositiveIntegerField()
    is_active = models.BooleanField()  # TODO: default: true of false ?
    file = models.FileField(upload_to='promotion/')  # TODO: upload to where ?

    city = models.ForeignKey(City, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
