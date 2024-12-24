from django.conf import settings
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .methods import last_week_statistics, last_month_statistics, last_year_statistics

User = get_user_model()


class Statistics(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statistics', verbose_name='Волонтер')
    points = models.PositiveIntegerField(default=0, verbose_name='Баллы')
    volunteer_hours = models.PositiveIntegerField(default=0, verbose_name='Часы')
    period = models.DateField(default=timezone.now, verbose_name='Период')

    class Meta:
        verbose_name = "Статистика волонтера"
        verbose_name_plural = "Статистика волонтеров"
        unique_together = ('volunteer', 'period')

    def __str__(self):
        return f'{self.volunteer} - {self.points} points, {self.volunteer_hours} hours on {self.period}'

    def save_weekly_statistics(self):
        result = last_week_statistics(self)

        return result

    def save_monthly_statistics(self):
        result = last_month_statistics(self.volunteer)

        return result

    def save_yearly_statistics(self):
        result = last_year_statistics(self.volunteer)

        return result

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(settings.CACHE_STATS_QUERYSET_KEY)
        cache.delete(settings.CACHE_STATS_WEEK_KEY)
        cache.delete(settings.CACHE_STATS_MONTH_KEY)
        cache.delete(settings.CACHE_STATS_YEAR_KEY)


class StatisticsByWeek(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='stats_by_week', verbose_name="Волонтер")
    points = models.PositiveIntegerField(default=0, verbose_name="Баллы потраченные за неделю")
    hours = models.PositiveIntegerField(default=0, verbose_name="Заработанные часы за неделю")

    class Meta:
        verbose_name = "Статистика волонтера по неделям"
        verbose_name_plural = "Статистика волонтеров по неделям"
        unique_together = ('user', 'points', 'hours')

    def __str__(self):
        return f'{self.user} - {self.points}/{self.hours}'


class StatisticsByMonth(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='stats_by_month', verbose_name="Волонтер")
    points = models.PositiveIntegerField(default=0, verbose_name="Баллы потраченные за месяц")
    hours = models.PositiveIntegerField(default=0, verbose_name="Заработанные часы за месяц")

    class Meta:
        verbose_name = "Статистика волонтера по месяцам"
        verbose_name_plural = "Статистика волонтеров по месяцам"
        unique_together = ('user', 'points', 'hours')

    def __str__(self):
        return f'{self.user} - {self.points}/{self.hours}'


class StatisticsByYear(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='stats_by_year', verbose_name="Волонтер")
    points = models.PositiveIntegerField(default=0, verbose_name="Баллы потраченные за год")
    hours = models.PositiveIntegerField(default=0, verbose_name="Заработанные часы за год")

    class Meta:
        verbose_name = "Статистика волонтера по годам"
        verbose_name_plural = "Статистика волонтеров по годам"
        unique_together = ('user', 'points', 'hours')

    def __str__(self):
        return f'{self.user} - {self.points}/{self.hours}'
