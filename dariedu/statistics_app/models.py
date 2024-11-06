from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class VolunteerStats(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stats', verbose_name="Волонтер")
    week = models.PositiveIntegerField(verbose_name="Неделя")
    month = models.PositiveIntegerField(verbose_name="Месяц", default=datetime.now().month)
    year = models.PositiveIntegerField(verbose_name="Год")
    hours = models.PositiveIntegerField(default=0, verbose_name="Часы")
    points = models.PositiveIntegerField(default=0, verbose_name="Баллы")

    class Meta:
        verbose_name = "Статистика волонтера"
        verbose_name_plural = "Статистика волонтеров"
        unique_together = ('volunteer', 'week', 'year')

    def __str__(self):
        return f'{self.volunteer} - {self.week}/{self.year}'

    def save(self, *args, **kwargs):
        # Считываем значения volunteer_hour и point для записи в статистику
        self.hours = self.volunteer.volunteer_hour
        self.points = self.volunteer.point
        super().save(*args, **kwargs)
