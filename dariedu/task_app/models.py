from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from address_app.models import RouteSheet, City, Location
from user_app.models import User


class Delivery(models.Model):
    date = models.DateTimeField(verbose_name='дата доставки')
    price = models.PositiveIntegerField('часы')
    curator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery',
                                blank=True, null=True, verbose_name='куратор',)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='delivery', verbose_name='Локация')
    is_free = models.BooleanField(default=True, verbose_name='свободная')
    is_active = models.BooleanField(default=True, verbose_name='активная')
    is_completed = models.BooleanField(default=False, verbose_name='завершена')
    in_execution = models.BooleanField(default=False, verbose_name='выполняется')
    volunteers_needed = models.PositiveIntegerField(verbose_name='требуется волонтеров', default=1)
    volunteers_taken = models.PositiveIntegerField(verbose_name='волонтеров взяли', default=0)

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

    @admin.display(description="Волонтеры")
    def display_volunteers(self):
        return format_html('<br>'.join([str(assignment) for assignment in self.assignments.all()]))

    class Meta:
        verbose_name = 'доставка'
        verbose_name_plural = 'доставки'


class DeliveryAssignment(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='assignments',
                                 verbose_name='доставка')
    volunteer = models.ManyToManyField(User, related_name='assignments', verbose_name='волонтер')

    def __str__(self):
        return format_html('<br>'.join([str(volunteer) for volunteer in self.volunteer.all()]))

    class Meta:
        verbose_name = 'доставка волонтера'
        verbose_name_plural = 'доставки волонтеров'


class Task(models.Model):
    category = models.ForeignKey('TaskCategory', on_delete=models.CASCADE,
                                 null=True, blank=True, verbose_name='категория')
    name = models.CharField(max_length=255, verbose_name='название')
    price = models.PositiveIntegerField(verbose_name='часы', default=2)
    description = models.TextField(blank=True, null=True, verbose_name='описание')
    start_date = models.DateTimeField(verbose_name='дата начала')
    end_date = models.DateTimeField(verbose_name='дата конца')
    volunteers_needed = models.PositiveIntegerField(verbose_name='требуется волонтеров', default=1)
    volunteers_taken = models.PositiveIntegerField(verbose_name='волонтеров взяли', default=0)
    is_active = models.BooleanField(default=True, verbose_name='активная')
    is_completed = models.BooleanField(default=False, verbose_name='завершена')

    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='город')
    curator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_curator', verbose_name='куратор')
    volunteers = models.ManyToManyField(User, blank=True, related_name='tasks', verbose_name='волонтеры')

    def __str__(self):
        return f'{self.name}, {self.start_date}'

    class Meta:
        verbose_name = 'задание'
        verbose_name_plural = 'задания'


class TaskCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name='название')
    icon = models.ImageField(blank=True, null=True, verbose_name='иконка', upload_to='task_category_icons/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория задания'
        verbose_name_plural = 'категории заданий'