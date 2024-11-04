from django.utils import timezone
from django.db.models import Sum
from celery import shared_task
from .models import VolunteerStats
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def update_volunteer_stats():
    today = timezone.now()
    current_week = today.isocalendar()[1]
    current_year = today.year
    current_month = today.month

    for volunteer in User.objects.filter(is_staff=False):  # Фильтр для выбора только волонтеров
        # Часы за текущую неделю из Task
        weekly_task_hours = volunteer.tasks.filter(
            is_completed=True,
            end_date__gte=today - timedelta(days=7)
        ).aggregate(total_hours=Sum('volunteer_price'))['total_hours'] or 0

        # Часы за текущую неделю из Delivery
        weekly_delivery_hours = volunteer.assignments.filter(
            delivery__is_completed=True,
            delivery__date__gte=today - timedelta(days=7)
        ).aggregate(total_hours=Sum('delivery__price'))['total_hours'] or 0

        weekly_hours = weekly_task_hours + weekly_delivery_hours

        # Часы за текущий месяц из Task
        monthly_task_hours = volunteer.tasks.filter(
            is_completed=True,
            end_date__month=current_month,
            end_date__year=current_year
        ).aggregate(total_hours=Sum('volunteer_price'))['total_hours'] or 0

        # Часы за текущий месяц из Delivery
        monthly_delivery_hours = volunteer.assignments.filter(
            delivery__is_completed=True,
            delivery__date__month=current_month,
            delivery__date__year=current_year
        ).aggregate(total_hours=Sum('delivery__price'))['total_hours'] or 0

        monthly_hours = monthly_task_hours + monthly_delivery_hours

        # Обновляем статистику за неделю
        VolunteerStats.objects.update_or_create(
            volunteer=volunteer,
            week=current_week,
            year=current_year,
            defaults={'hours': weekly_hours, 'points': volunteer.point}
        )

        # Обновляем статистику за месяц
        VolunteerStats.objects.update_or_create(
            volunteer=volunteer,
            month=current_month,
            year=current_year,
            defaults={'hours': monthly_hours, 'points': volunteer.point}
        )
