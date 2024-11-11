from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import *

User = get_user_model()


@shared_task
def create_last_week():
    """Создает запись для завершившейся недели (понедельник-воскресенье), если её еще нет."""
    # Определяем текущую дату
    today = timezone.now().date()

    # Определяем начало и конец прошедшей недели
    last_week_start = today - timedelta(days=today.weekday() + 7)  # Начало прошлой недели (понедельник)
    last_week_end = last_week_start + timedelta(days=6)  # Конец прошлой недели (воскресенье)

    # Проверяем, существует ли запись для завершённой недели
    if not Week.objects.filter(start_date=last_week_start, end_date=last_week_end).exists():
        # Создаем новую запись для завершённой недели
        Week.objects.create(start_date=last_week_start, end_date=last_week_end)
    # Немедленно выполняем создание записи при запуске задачи
    create_last_week()


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
