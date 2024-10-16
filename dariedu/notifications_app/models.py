from django.db import models


class Notification(models.Model):
    title = models.CharField(max_length=255, verbose_name='тип уведомления')
    text = models.TextField(verbose_name='описание', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    obj_link = models.URLField(max_length=255, verbose_name='ссылка на объект', blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'уведомление'
        verbose_name_plural = 'уведомления'
