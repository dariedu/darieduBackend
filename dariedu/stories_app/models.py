from django.db import models

from dariedu import settings


class Stories(models.Model):
    link_name = models.CharField(max_length=255, verbose_name='имя для ссылки', unique=True)
    cover = models.ImageField(blank=True, null=True, verbose_name='обложка', upload_to='stories_cover',
            help_text='Обложка для сториса в приложении. Ширина 116, высота 160 пикселей, формат SVG, PNG')
    title = models.CharField(max_length=255, verbose_name='заголовок', blank=True, null=True)
    text = models.TextField(verbose_name='текст', blank=True, null=True)
    media_files = models.FileField(blank=True, null=True, verbose_name='файлы', upload_to='stories_files')
    background = models.ImageField(blank=True, null=True, verbose_name='фон')
    hidden = models.BooleanField(default=False, verbose_name='скрыт')

    class Meta:
        verbose_name = 'сторис'
        verbose_name_plural = 'сторисы'

    def __str__(self):
        return self.title

    def get_link(self):
        return f'http://{settings.CURRENT_HOST}/stories/{self.link_name}'
