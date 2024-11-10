from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import WeeklyVolunteerStats

User = get_user_model()

@shared_task
def collect_weekly_volunteer_stats():
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    for volunteer in User.objects.filter(volunteer_hour__gt=0):  # Фильтрация по volunteer_hour
        hours = calculate_hours_for_week(volunteer, start_of_week, end_of_week)
        points = calculate_points_for_week(volunteer, start_of_week, end_of_week)

        # Обновление или создание записи статистики
        WeeklyVolunteerStats.objects.update_or_create(
            volunteer=volunteer,
            start_date=start_of_week,
            end_date=end_of_week,
            defaults={'hours': hours, 'points': points}
        )

def calculate_hours_for_week(volunteer, start_date, end_date):
    # Ваша логика расчета часов за неделю для конкретного волонтера
    return volunteer.volunteer_hour  # или другая логика для подсчета

def calculate_points_for_week(volunteer, start_date, end_date):
    # Ваша логика расчета баллов за неделю для конкретного волонтера
    return volunteer.point  # или другая логика для подсчета
