# Generated by Django 5.1 on 2025-03-09 10:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address_app', '0031_merge_20250302_2010'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='routeassignment',
            name='volunteer',
        ),
        migrations.AddField(
            model_name='routeassignment',
            name='volunteer',
            field=models.ManyToManyField(related_name='route_assignments', to=settings.AUTH_USER_MODEL, verbose_name='волонтёр'),
        ),
    ]
