# Generated by Django 5.1 on 2024-11-17 15:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address_app', '0024_alter_beneficiar_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beneficiar',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='beneficiar', to='address_app.address', verbose_name='адрес проживания'),
        ),
        migrations.AlterField(
            model_name='beneficiar',
            name='comment',
            field=models.TextField(blank=True, default='', null=True, verbose_name='комментарий'),
        ),
        migrations.AlterField(
            model_name='beneficiar',
            name='second_phone',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='доп. телефон'),
        ),
    ]