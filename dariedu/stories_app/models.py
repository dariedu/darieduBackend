from django.db import models


class Stories(models.Model):
    link_name = models.CharField(max_length=255, verbose_name='имя для ссылки', unique=True)
    cover = models.ImageField(blank=True, null=True, verbose_name='обложка', upload_to='stories_cover')
    title = models.CharField(max_length=255, verbose_name='заголовок', blank=True, null=True)
    text = models.TextField(verbose_name='текст', blank=True, null=True)
    media_files = models.FileField(blank=True, null=True, verbose_name='файлы', upload_to='stories_files')
    link = models.URLField(max_length=500, verbose_name='ссылка', blank=True, null=True)
    hidden = models.BooleanField(default=False, verbose_name='скрыт')

    class Meta:
        verbose_name = 'сторис'
        verbose_name_plural = 'сторисы'

    def __str__(self):
        return self.title

    def get_link(self):
        return self.link