# Generated by Django 5.1 on 2024-09-13 21:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address_app', '0015_merge_0013_routesheet_user_0014_location_media_files'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='routesheet',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='route_sheets', to='address_app.location', verbose_name='локация'),
        ),
        migrations.AlterField(
            model_name='routesheet',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='route_sheets', to=settings.AUTH_USER_MODEL, verbose_name='волонтёр'),
        ),
    ]
