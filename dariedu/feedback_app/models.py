from django.db import models

from user_app.models import User


class RequestMessage(models.Model):
    type = models.CharField(max_length=255, verbose_name='тип заявки')
    text = models.TextField(verbose_name='текст', blank=True, null=True)
    form = models.URLField(max_length=500, blank=True, null=True, verbose_name='форма')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'


class Feedback(models.Model):
    type = models.CharField(max_length=255, verbose_name='тип отзыва')
    text = models.TextField(blank=True, null=True, verbose_name='текст')
    form = models.URLField(max_length=500, blank=True, null=True, verbose_name='форма')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'


class PhotoReport(models.Model):
    address = models.ForeignKey('address_app.Address', on_delete=models.CASCADE, verbose_name='адрес')
    photo = models.URLField(max_length=500, verbose_name='фото', blank=True, null=True)
    date = models.DateField(verbose_name='дата', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    comment = models.TextField(verbose_name='комментарий', blank=True, null=True)
