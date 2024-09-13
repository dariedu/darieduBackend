from django.core.exceptions import ValidationError
from django.db import models
from address_app.models import City
from user_app.models import User


class Promotion(models.Model):
    category = models.CharField(max_length=255, verbose_name='категория')
    name = models.CharField(max_length=255, verbose_name='название')
    price = models.PositiveIntegerField(verbose_name='стоимость')
    description = models.TextField(blank=True, null=True, verbose_name='описание')
    date = models.DateTimeField(verbose_name='дата')
    quantity = models.PositiveIntegerField(verbose_name='количество')
    for_curators_only = models.BooleanField(default=False, verbose_name='только для кураторов')
    is_active = models.BooleanField(default=True, verbose_name='активная')
    file = models.FileField(upload_to='promotion/', blank=True, null=True, verbose_name='файл')  # TODO: upload to where ?

    # Срок действия поощрения.
    # Если поощрение бессрочное, устанавливается `is_permanent = True`, а поле `expiry_date`
    # можно оставить пустым.
    # Если у поощрения есть конкретный срок действия, поле `is_permanent` будет `False`, и
    # нужно указать дату в `expiry_date`.
    is_permanent = models.BooleanField(default=False, verbose_name='бессрочное поощрение')
    expiry_date = models.DateTimeField(blank=True, null=True, verbose_name='срок действия')  # Дата окончания действия

    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, verbose_name='город')
    users = models.ManyToManyField(User, through='Participation', blank=True, verbose_name='получатель')


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
        if not self.is_permanent and not self.expiry_date:
            raise ValidationError("Укажите срок действия или отметьте поощрение как бессрочное.")
        if self.is_permanent and self.expiry_date:
            raise ValidationError("Бессрочное поощрение не должно иметь срока действия.")

    class Meta:
        verbose_name = 'поощрение'
        verbose_name_plural = 'поощрения'


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='волонтер')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, verbose_name='поощрение')
    received_at = models.DateTimeField(auto_now_add=True, verbose_name='дата получения')

    def __str__(self):
        return f"{self.user} - {self.promotion}"

    class Meta:
        verbose_name = 'участие'
        verbose_name_plural = 'участия'