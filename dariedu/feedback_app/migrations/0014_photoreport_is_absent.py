# Generated by Django 5.1 on 2024-12-04 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback_app', '0013_alter_feedback_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='photoreport',
            name='is_absent',
            field=models.BooleanField(default=False, verbose_name='отсутствует'),
        ),
    ]