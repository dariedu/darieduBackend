from django.db import models

from user_app.models import User


class RequestMessage(models.Model):
    type = models.CharField(max_length=255, verbose_name='тип запроса')
    text = models.TextField(verbose_name='текст', blank=True, null=True)
    form = models.URLField(max_length=500, blank=True, null=True, verbose_name='форма')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')

    def __str__(self):
        return self.type


class Feedback(models.Model):
    type = models.CharField(max_length=255, verbose_name='тип отзыва')
    text = models.TextField(blank=True, null=True, verbose_name='текст')
    form = models.URLField(max_length=500, blank=True, null=True, verbose_name='форма')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')

    def __str__(self):
        return self.type
