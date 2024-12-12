# Generated by Django 5.1 on 2024-12-01 17:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistics_app', '0002_alter_volunteerstats_week'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteerstats',
            name='month',
            field=models.PositiveIntegerField(default=12, verbose_name='Месяц'),
        ),
        migrations.AlterField(
            model_name='volunteerstats',
            name='volunteer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stats', to=settings.AUTH_USER_MODEL, verbose_name='Волонтер'),
        ),
    ]