# Generated by Django 5.1 on 2024-09-17 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promo_app', '0008_rename_expiry_date_promotion_end_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='название')),
            ],
            options={
                'verbose_name': 'категория поощрений',
                'verbose_name_plural': 'категории поощрений',
            },
        ),
        migrations.AddField(
            model_name='promotion',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='картинка'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='category',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='категория'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='file',
            field=models.URLField(blank=True, null=True, verbose_name='файл'),
        ),
    ]