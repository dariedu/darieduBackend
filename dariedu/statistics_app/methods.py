from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone


def last_week_statistics(self):
    from .models import Statistics

    today = timezone.now().date()
    start_week = today - timedelta(days=7)

    weekly_stats = Statistics.objects.filter(
        volunteer=self.volunteer,
        period__gte=start_week
    ).aggregate(
        total_points=Sum('points'),
        total_volunteer_hours=Sum('volunteer_hours')
    )

    return weekly_stats


def last_month_statistics(volunteer):
    from .models import Statistics

    today = timezone.now().date()
    start_month = today.replace(day=1)

    monthly_stats = Statistics.objects.filter(
        volunteer=volunteer,
        period__gte=start_month
    ).aggregate(
        total_points=Sum('points'),
        total_volunteer_hours=Sum('volunteer_hours')
    )

    return monthly_stats


def last_year_statistics(volunteer):
    from .models import Statistics

    today = timezone.now().date()
    start_year = today.replace(month=1, day=1)

    yearly_stats = Statistics.objects.filter(
        volunteer=volunteer,
        period__gte=start_year
    ).aggregate(
        total_points=Sum('points'),
        total_volunteer_hours=Sum('volunteer_hours')
    )

    return yearly_stats
