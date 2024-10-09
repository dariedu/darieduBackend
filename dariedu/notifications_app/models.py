from django.db import models


class Notification(models.Model):
    title = models.CharField(max_length=255, verbose_name='тип уведомления')
    text = models.TextField(verbose_name='описание', blank=True, null=True)
    form = models.URLField(max_length=500, blank=True, null=True, verbose_name='форма')
    created = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'уведомление'
        verbose_name_plural = 'уведомления'
