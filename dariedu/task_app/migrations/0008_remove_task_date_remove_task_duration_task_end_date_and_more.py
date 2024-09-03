# Generated by Django 5.1 on 2024-08-27 15:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_app', '0007_merge_20240827_1622'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='date',
        ),
        migrations.RemoveField(
            model_name='task',
            name='duration',
        ),
        migrations.AddField(
            model_name='task',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 27, 17, 44, 6, 651, tzinfo=datetime.timezone.utc), verbose_name='дата конца'),
        ),
        migrations.AddField(
            model_name='task',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 27, 15, 44, 6, 651, tzinfo=datetime.timezone.utc), verbose_name='дата начала'),
        ),
    ]