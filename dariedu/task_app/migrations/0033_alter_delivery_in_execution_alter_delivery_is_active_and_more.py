# Generated by Django 5.1 on 2025-02-23 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address_app', '0029_alter_routeassignment_route_sheet'),
        ('task_app', '0032_alter_task_curator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='in_execution',
            field=models.BooleanField(default=False, verbose_name='выпол.'),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='актив.'),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='завер.'),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='is_free',
            field=models.BooleanField(default=True, verbose_name='своб.'),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='route_sheet',
            field=models.ManyToManyField(related_name='delivery', to='address_app.routesheet', verbose_name='маршрут'),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='volunteers_needed',
            field=models.PositiveIntegerField(default=1, verbose_name='нужно'),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='volunteers_taken',
            field=models.PositiveIntegerField(default=0, verbose_name='взяли'),
        ),
    ]
