from django.db import models
from django.conf import settings


class Stories(models.Model):
    cover = models.ImageField(verbose_name='обложка', upload_to='stories_cover',
            help_text='Обложка для сториса в приложении. Ширина 116, высота 160 пикселей, формат SVG, PNG')
    title = models.CharField(max_length=255, verbose_name='заголовок')
    subtitle = models.CharField(max_length=255, verbose_name='подзаголовок', blank=True, null=True)
    text = models.TextField(verbose_name='текст')
    date = models.DateField(verbose_name='дата', null=True, blank=True)
    background = models.ImageField(blank=True, null=True, verbose_name='фон', upload_to='stories_background',
            help_text='Фон для сториса в приложении. Ширина 360, высота 634 пикселей, формат SVG, PNG, JPG')
    hidden = models.BooleanField(default=False, verbose_name='скрыт')

    class Meta:
        verbose_name = 'сторис'
        verbose_name_plural = 'сторисы'

    def __str__(self):
        return self.title

    def get_link(self):
        return f'http://{settings.CURRENT_HOST}/stories/{self.link_name}'
