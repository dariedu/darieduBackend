# Generated by Django 5.1 on 2024-10-11 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback_app', '0003_merge_20241011_1449'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photoreport',
            name='photo',
        ),
        migrations.AddField(
            model_name='photoreport',
            name='photo_download',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='загрузка фотографии'),
        ),
        migrations.AddField(
            model_name='photoreport',
            name='photo_view',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='показ фотографии'),
        ),
    ]