# Generated by Django 5.1 on 2024-11-13 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address_app', '0023_beneficiar_second_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beneficiar',
            name='category',
            field=models.CharField(blank=True, choices=[('Пенсионер', 'Пенсионер'), ('Ветеран ВОВ', 'Ветеран ВОВ'), ('Ветеран труда', 'Ветеран труда'), ('Инвалид I группы', 'Инвалид I группы'), ('Инвалид II группы', 'Инвалид II группы'), ('Инвалид III группы', 'Инвалид III группы')], default=None, max_length=255, null=True, verbose_name='категория'),
        ),
    ]