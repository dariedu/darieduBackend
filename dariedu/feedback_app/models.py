from django.db import models
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html

from address_app.models import RouteSheet
from promo_app.models import Promotion
from task_app.models import Delivery, Task


User = get_user_model()


class RequestMessage(models.Model):
    type = models.CharField(max_length=255, verbose_name='тип', default='стать куратором')
    about_location = models.CharField(max_length=255, verbose_name='на какой локации', blank=True, null=True,
                                      help_text='На какой локации вы бы хотели стать куратором и почему?')
    about_presence = models.CharField(max_length=255, verbose_name='присутствие', blank=True, null=True,
                                      help_text='Готовы ли вы присутствовать на локациии во время доставок?')
    about_worktime = models.CharField(max_length=255, verbose_name='график работы', blank=True, null=True,
                                      help_text='Какой у вас график работы/учебы?')
    date = models.DateField(verbose_name='дата', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('admin:feedback_app_requestmessage_change', args=[self.pk])

    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'


class Feedback(models.Model):
    TYPE_CHOICES = [
        ('completed_delivery', 'Завершенная доставка'),
        ('canceled_delivery', 'Отмененная доставка'),
        ('completed_promotion', 'Завершенное поощрение'),
        ('canceled_promotion', 'Отмененное поощрение'),
        ('completed_task', 'Завершенное доброе дело'),
        ('canceled_task', 'Отмененное доброе дело'),
        ('suggestion', 'Вопросы и предложения'),
    ]

    id = models.AutoField(primary_key=True, verbose_name="ID")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Тип обратной связи")
    text = models.TextField(verbose_name="Текст обратной связи", max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, null=True, blank=True,
                                 verbose_name="Доставка", related_name="feedbacks")
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, null=True, blank=True,
                                  verbose_name="Поощрение", related_name="feedbacks")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Доброе дело",
                             related_name="feedbacks")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def clean(self):
        # Проверка, что обратная связь может быть только о доставке или поощрении, но не о двух одновременно
        if self.type == 'delivery' and not self.delivery:
            raise ValidationError("Для обратной связи о доставке необходимо указать доставку.")
        if self.type == 'promotion' and not self.promotion:
            raise ValidationError("Для обратной связи о поощрении необходимо указать поощрение.")
        if self.type == 'task' and not self.task:
            raise ValidationError("Для обратной связи о доброе дело необходимо указать доброе дело.")
        if self.delivery and self.promotion:
            raise ValidationError("Обратная связь может быть связана только с одной моделью: "
                                  "либо доставка, либо поощрение, либо доброе дело.")

    def __str__(self):
        if self.type == 'delivery':
            return f"Обратная связь о доставке {self.delivery} от {self.user.name} {self.user.last_name}"
        elif self.type == 'promotion':
            return f"Обратная связь о поощрении {self.promotion} от {self.user.name} {self.user.last_name}"
        elif self.type == 'task':
            return f"Обратная связь о доброе дело {self.task} от {self.user.name} {self.user.last_name}"
        return f"Отзыв от {self.user.name} {self.user.last_name}"

    def get_absolute_url(self):
        return reverse('admin:feedback_app_feedback_change', args=[self.pk])

    class Meta:
        verbose_name = 'обратная связь'
        verbose_name_plural = 'обратная связь'


class PhotoReport(models.Model):
    address = models.ForeignKey('address_app.Address', on_delete=models.SET_NULL, verbose_name='адрес'
                                , null=True, blank=True)
    photo_view = models.URLField(max_length=500, verbose_name='показ фотографии', blank=True, null=True)
    photo_download = models.FileField(max_length=500, verbose_name='загрузка фотографии', blank=True, null=True)
    date = models.DateField(verbose_name='дата', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='пользователь', null=True, blank=True)
    delivery_id = models.ForeignKey(Delivery, on_delete=models.SET_NULL, verbose_name='доставка',
                                    blank=True, null=True)
    route_sheet_id = models.ForeignKey(RouteSheet, on_delete=models.SET_NULL, verbose_name='маршрутный лист',
                                       null=True, blank=True)
    comment = models.TextField(verbose_name='комментарий', blank=True, null=True, max_length=255)

    @admin.display(description='благополучатели')
    def display_beneficiar(self):
        return format_html('<br>'.join([beneficiar.full_name for beneficiar in self.address.beneficiar.all()]))
