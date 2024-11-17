from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone

from address_app.models import City


User = get_user_model()


class Promotion(models.Model):
    category = models.ForeignKey('PromoCategory', on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name='категория')
    name = models.CharField(max_length=255, verbose_name='название')
    price = models.PositiveIntegerField(verbose_name='стоимость')
    description = models.TextField(blank=True, null=True, verbose_name='описание')
    start_date = models.DateTimeField(default=timezone.now, verbose_name='дата начала')
    quantity = models.PositiveIntegerField(verbose_name='Общее количество', default=1)
    available_quantity = models.PositiveIntegerField(verbose_name='доступное количество', default=1,
                                                     help_text='Изначально должно быть равно количеству. '
                                                               'Будет меняться автоматически')
    for_curators_only = models.BooleanField(default=False, verbose_name='только для кураторов')
    is_active = models.BooleanField(default=True, verbose_name='активная')
    ticket_file = models.URLField(blank=True, null=True, verbose_name='файл')  # TODO: upload to where ?
    about_tickets = models.TextField(blank=True, null=True, verbose_name='информация о билетах', max_length=255)

    # Срок действия поощрения.
    # Если поощрение бессрочное, устанавливается `is_permanent = True`, а поле `end_date`
    # можно оставить пустым.
    # Если у поощрения есть конкретный срок действия, поле `is_permanent` будет `False`, и
    # нужно указать дату в `end_date`.
    is_permanent = models.BooleanField(default=False, verbose_name='бессрочное поощрение')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='дата окончания',
                                    help_text='Только если поощрение не бессрочное')

    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='город')
    users = models.ManyToManyField(User, through='Participation', blank=True, verbose_name='получатель')
    picture = models.ImageField(blank=True, null=True, upload_to='promo_pictures/', verbose_name='картинка',
                                help_text='Ширина 328px, высота 205px')
    address = models.CharField(max_length=255, verbose_name='адрес', blank=True, null=True)
    contact_person = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='contact_persons',
                                       verbose_name='контактное лицо', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_available_promotions(user):
        if user.is_staff:
            # Куратор видит все активные поощрения
            promotions = Promotion.objects.filter(is_active=True)
        else:
            #  волонтёр видит только поощрения, не предназначенные только для кураторов
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

    def get_absolute_url(self):
        return reverse('admin:promo_app_promotion_change', args=[self.pk])

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='волонтёр')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, verbose_name='поощрение')
    received_at = models.DateTimeField(auto_now_add=True, verbose_name='дата получения')
    is_active = models.BooleanField(default=False, verbose_name='подтверждение')

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

    def save_without_reward_check(self, *args, **kwargs):
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


