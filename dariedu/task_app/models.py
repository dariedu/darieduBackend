from django.urls import reverse
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from address_app.models import RouteSheet, City, Location
from user_app.models import User

from dariedu.settings import CURRENT_HOST


class Delivery(models.Model):
    date = models.DateTimeField(verbose_name='дата доставки')
    price = models.PositiveIntegerField('часы', default=2)
    curator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery',
                                blank=True, null=True, verbose_name='куратор',)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='delivery', verbose_name='Локация')
    is_free = models.BooleanField(default=True, verbose_name='свободная')
    is_active = models.BooleanField(default=True, verbose_name='активная')
    is_completed = models.BooleanField(default=False, verbose_name='завершена')
    in_execution = models.BooleanField(default=False, verbose_name='выполняется')
    volunteers_needed = models.PositiveIntegerField(verbose_name='требуется волонтёров', default=1)
    volunteers_taken = models.PositiveIntegerField(verbose_name='волонтёров взяли', default=0)

    route_sheet = models.ManyToManyField(RouteSheet, related_name='delivery', verbose_name='маршрутный лист')

    def clean(self):
        if self.is_completed:
            self.is_free = False
            self.is_active = False
            self.in_execution = False

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @admin.display(description="Маршрутный лист")
    def display_route_sheet(self):
        return format_html('<br>'.join([str(route_sheet) for route_sheet in self.route_sheet.all()]))

    @admin.display(description="Волонтёры")
    def display_volunteers(self):
        return format_html('<br>'.join([str(assignment) for assignment in self.assignments.all()]))

    class Meta:
        verbose_name = 'доставка'
        verbose_name_plural = 'доставки'


class DeliveryAssignment(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='assignments',
                                 verbose_name='доставка')
    volunteer = models.ManyToManyField(User, related_name='assignments', verbose_name='волонтёр')

    def __str__(self):
        return format_html('<br>'.join([str(volunteer) for volunteer in self.volunteer.all()]))

    class Meta:
        verbose_name = 'доставка волонтёра'
        verbose_name_plural = 'доставки волонтёров'


class Task(models.Model):
    category = models.ForeignKey('TaskCategory', on_delete=models.CASCADE,
                                 null=True, blank=True, verbose_name='категория')
    name = models.CharField(max_length=255, verbose_name='название')
    volunteer_price = models.PositiveIntegerField(verbose_name='волонтёрские часы', default=2)
    curator_price = models.PositiveIntegerField(verbose_name='кураторские часы', default=2)
    description = models.TextField(blank=True, null=True, verbose_name='описание')
    start_date = models.DateTimeField(verbose_name='дата начала')
    end_date = models.DateTimeField(verbose_name='дата конца')
    volunteers_needed = models.PositiveIntegerField(verbose_name='требуется волонтёров', default=1)
    volunteers_taken = models.PositiveIntegerField(verbose_name='волонтёров взяли', default=0)
    is_active = models.BooleanField(default=True, verbose_name='активная')
    is_completed = models.BooleanField(default=False, verbose_name='завершена')

    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='город')
    curator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_curator', verbose_name='куратор')
    volunteers = models.ManyToManyField(User, blank=True, related_name='tasks', verbose_name='волонтёры')

    def __str__(self):
        return f'{self.name}, {self.start_date}'

    def get_absolute_url(self):
        return reverse('admin:task_app_task_change', args=[self.pk])

    class Meta:
        verbose_name = 'доброе дело'
        verbose_name_plural = 'добрые дела'


class TaskCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name='название')
    icon = models.ImageField(blank=True, null=True, verbose_name='иконка', upload_to='task_category_icons/',
                             help_text='размер 32x32 пикселей, форматы SVG, PNG')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория добрых дел'
        verbose_name_plural = 'категории добрых дел'
