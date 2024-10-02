from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import format_html

from address_app.models import City
from user_app.models import User
from django.utils import timezone


class Promotion(models.Model):
    category = models.ForeignKey('PromoCategory', on_delete=models.CASCADE,
                                 null=True, blank=True, verbose_name='категория')
    name = models.CharField(max_length=255, verbose_name='название')
    price = models.PositiveIntegerField(verbose_name='стоимость')
    description = models.TextField(blank=True, null=True, verbose_name='описание')
    start_date = models.DateTimeField(default=timezone.now, verbose_name='дата начала поощрения')
    quantity = models.PositiveIntegerField(verbose_name='количество')  # общее количество поощрений
    available_quantity = models.PositiveIntegerField(verbose_name='доступное количество',
                                                     default=0)  # показ доступного количества поощрений
    for_curators_only = models.BooleanField(default=False, verbose_name='только для кураторов')
    is_active = models.BooleanField(default=True, verbose_name='активная')
    file = models.URLField(blank=True, null=True, verbose_name='файл')  # TODO: upload to where ?

    # Срок действия поощрения.
    # Если поощрение бессрочное, устанавливается `is_permanent = True`, а поле `end_date`
    # можно оставить пустым.
    # Если у поощрения есть конкретный срок действия, поле `is_permanent` будет `False`, и
    # нужно указать дату в `end_date`.
    is_permanent = models.BooleanField(default=False, verbose_name='бессрочное поощрение')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='срок действия')  # Дата окончания действия

    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='город')
    users = models.ManyToManyField(User, through='Participation', blank=True, verbose_name='получатель')
    picture = models.ImageField(blank=True, null=True, verbose_name='картинка')  # TODO: or URL?

    def __str__(self):
        return self.name

    def get_available_promotions(user):
        if user.is_staff:
            # Куратор видит все активные поощрения
            promotions = Promotion.objects.filter(is_active=True)
        else:
            #  Волонтер видит только поощрения, не предназначенные только для кураторов
            promotions = Promotion.objects.filter(is_active=True, for_curators_only=False)
        return promotions

    def clean(self):
        if not self.is_permanent and not self.end_date:
            raise ValidationError("Укажите срок действия или отметьте поощрение как бессрочное.")
        if self.is_permanent and self.end_date:
            raise ValidationError("Бессрочное поощрение не должно иметь срока действия.")
        if self.available_quantity > self.quantity:
            raise ValidationError("Доступное количество не может быть больше общего количества.")

    def save(self, *args, **kwargs):
        if not self.pk:  # Если поощрение создаётся впервые, синхронизируем available_quantity с quantity
            self.available_quantity = self.quantity
        super().save(*args, **kwargs)

    # Подсчет числа участников поощрений
    def volunteers_count(self):
        return self.participation_set.count()

    @admin.display(description="участники")
    def display_volunteers(self):
        verbose_name = "участник" if self.volunteers_count() == 1 else "участники"
        return format_html("<br>".join([str(user) for user in self.users.all()]))

    class Meta:
        verbose_name = 'поощрение'
        verbose_name_plural = 'поощрения'


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='волонтер')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, verbose_name='поощрение')
    received_at = models.DateTimeField(auto_now_add=True, verbose_name='дата получения')

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        # Проверяем, есть ли доступные поощрения
        if self.promotion.available_quantity <= 0:
            raise ValidationError("Нет доступных поощрений.")

        # Уменьшаем доступное количество поощрений
        self.promotion.available_quantity -= 1
        self.promotion.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Возвращаем поощрение в доступное количество
        self.promotion.available_quantity += 1
        self.promotion.save()

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'участники'
        verbose_name_plural = 'участники'


class PromoCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name='название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория поощрений'
        verbose_name_plural = 'категории поощрений'