from django.utils import timezone
from django.db.models import Sum
from celery import shared_task
from .models import *
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def update_volunteer_stats():
    today = timezone.now()
    current_week_start = today - timedelta(days=today.weekday())  # Начало текущей недели
    current_week_end = current_week_start + timedelta(days=6)     # Конец текущей недели
    current_month_start = today.replace(day=1)                    # Начало текущего месяца
    current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)  # Конец месяца

    for volunteer in User.objects.filter(is_staff=False):  # Фильтр для выбора только волонтеров
        # Часы за текущую неделю из Task
        weekly_task_hours = volunteer.tasks.filter(
            is_completed=True,
            end_date__range=(current_week_start, current_week_end)
        ).aggregate(total_hours=Sum('volunteer_price'))['total_hours'] or 0

        # Часы за текущую неделю из Delivery
        weekly_delivery_hours = volunteer.assignments.filter(
            delivery__is_completed=True,
            delivery__date__range=(current_week_start, current_week_end)
        ).aggregate(total_hours=Sum('delivery__price'))['total_hours'] or 0

        weekly_hours = weekly_task_hours + weekly_delivery_hours

        # Обновляем статистику за неделю
        WeeklyVolunteerStats.objects.update_or_create(
            volunteer=volunteer,
            start_date=current_week_start,
            end_date=current_week_end,
            defaults={'hours': weekly_hours, 'points': volunteer.point}
        )

        # Часы за текущий месяц из Task
        monthly_task_hours = volunteer.tasks.filter(
            is_completed=True,
            end_date__month=current_month_start.month,
            end_date__year=current_month_start.year
        ).aggregate(total_hours=Sum('volunteer_price'))['total_hours'] or 0

        # Часы за текущий месяц из Delivery
        monthly_delivery_hours = volunteer.assignments.filter(
            delivery__is_completed=True,
            delivery__date__month=current_month_start.month,
            delivery__date__year=current_month_start.year
        ).aggregate(total_hours=Sum('delivery__price'))['total_hours'] or 0

        monthly_hours = monthly_task_hours + monthly_delivery_hours

        # Обновляем статистику за месяц
        MonthlyVolunteerStats.objects.update_or_create(
            volunteer=volunteer,
            start_date=current_month_start,
            end_date=current_month_end,
            defaults={'hours': monthly_hours, 'points': volunteer.point}
        )

@shared_task
def update_consolidated_monthly_stats():
    """
    Задача для обновления сводной статистики за текущий месяц.
    """
    today = timezone.now()
    start_date = today.replace(day=1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    ConsolidatedMonthlyStats.update_statistics(start_date=start_date, end_date=end_date)