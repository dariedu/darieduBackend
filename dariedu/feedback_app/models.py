from django.db import models

from user_app.models import User


class Request(models.Model):
    type = models.CharField(max_length=255)
    text = models.TextField()
    form = models.URLField(max_length=255)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.type


class Feedback(models.Model):
    type = models.CharField(max_length=255)
    text = models.TextField()
    form = models.URLField(max_length=255)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.type
