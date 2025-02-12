# Generated by Django 5.1 on 2024-10-11 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback_app', '0004_remove_photoreport_photo_photoreport_photo_download_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestmessage',
            name='text',
        ),
        migrations.RemoveField(
            model_name='requestmessage',
            name='type',
        ),
        migrations.AddField(
            model_name='requestmessage',
            name='about_location',
            field=models.CharField(blank=True, help_text='На какой локации вы бы хотели стать куратором и почему?', max_length=255, null=True, verbose_name='на какой локации'),
        ),
        migrations.AddField(
            model_name='requestmessage',
            name='about_presence',
            field=models.CharField(blank=True, help_text='Готовы ли вы присутствовать на локациии во время доставок?', max_length=255, null=True, verbose_name='присутствие'),
        ),
        migrations.AddField(
            model_name='requestmessage',
            name='about_worktime',
            field=models.CharField(blank=True, help_text='Какой у вас график работы/учебы?', max_length=255, null=True, verbose_name='график работы'),
        ),
    ]
