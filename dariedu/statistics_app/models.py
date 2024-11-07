from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

User = get_user_model()

class WeeklyVolunteerStats(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_stats', verbose_name="Волонтер")
    start_date = models.DateField(verbose_name="Дата начала недели")
    end_date = models.DateField(verbose_name="Дата окончания недели")
    hours = models.PositiveIntegerField(default=0, verbose_name="Часы")
    points = models.PositiveIntegerField(default=0, verbose_name="Баллы")

    class Meta:
        verbose_name = "Статистика волонтера за неделю"
        verbose_name_plural = "Статистика волонтеров за неделю"
        unique_together = ('volunteer', 'start_date', 'end_date')

    def __str__(self):
        return f'{self.volunteer.last_name} {self.volunteer.name} за {self.start_date} - {self.end_date}'

    def save(self, *args, **kwargs):
        # Считываем значения volunteer_hour и point для записи в статистику
        self.hours = self.volunteer.volunteer_hour
        self.points = self.volunteer.point
        super().save(*args, **kwargs)


class MonthlyVolunteerStats(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_stats', verbose_name="Волонтер")
    start_date = models.DateField(verbose_name="Дата начала месяца")
    end_date = models.DateField(verbose_name="Дата окончания месяца")
    hours = models.PositiveIntegerField(default=0, verbose_name="Часы")
    points = models.PositiveIntegerField(default=0, verbose_name="Баллы")

    class Meta:
        verbose_name = "Статистика волонтера за месяц"
        verbose_name_plural = "Статистика волонтеров за месяц"
        unique_together = ('volunteer', 'start_date', 'end_date')

    def __str__(self):
        return f'{self.volunteer.last_name} {self.volunteer.name} - {self.start_date} - {self.end_date}'

    def save(self, *args, **kwargs):
        # Считываем значения volunteer_hour и point для записи в статистику
        self.hours = self.volunteer.volunteer_hour
        self.points = self.volunteer.point
        super().save(*args, **kwargs)


class ConsolidatedMonthlyStats(models.Model):
    start_date = models.DateField(verbose_name="Дата начала месяца")
    end_date = models.DateField(verbose_name="Дата окончания месяца")
    total_hours = models.PositiveIntegerField(default=0, verbose_name="Общее количество часов")
    total_points = models.PositiveIntegerField(default=0, verbose_name="Общее количество баллов")

    class Meta:
        verbose_name = "Сводная статистика"
        unique_together = ('start_date', 'end_date')

    def __str__(self):
        return f'Сводная статистика за {self.start_date} - {self.end_date}'

    @classmethod
    def update_statistics(cls, start_date, end_date):
        """
        Метод для обновления суммарных значений по часам и баллам за указанный месяц и год.
        """
        # Агрегация данных из модели MonthlyVolunteerStats
        stats = MonthlyVolunteerStats.objects.filter(start_date__gte=start_date, end_date__lte=end_date).aggregate(
            total_hours=Sum('hours'),
            total_points=Sum('points')
        )
        # Обновляем или создаем запись в ConsolidatedMonthlyStats
        consolidated_stat, created = cls.objects.get_or_create(start_date=start_date, end_date=end_date)
        consolidated_stat.total_hours = stats['total_hours'] or 0
        consolidated_stat.total_points = stats['total_points'] or 0
        consolidated_stat.save()




### Сигнал для автоматического обновления сводной статистики

# Связываем с событием сохранения VolunteerStats, чтобы обновлять ConsolidatedStatistics
# @receiver(post_save, sender=VolunteerStats)
# def update_consolidated_statistics(sender, instance, **kwargs):
#     """
#     Сигнал для обновления сводной статистики после сохранения VolunteerStats.
#     """
#     ConsolidatedStatistics.update_statistics(month=instance.month, year=instance.year)
