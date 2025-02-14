from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from statistics_app.models import Statistics, StatisticsByWeek, StatisticsByMonth, StatisticsByYear, AllStatistics
from .methods import all_statistics_week

User = get_user_model()


@shared_task
def update_statistics():
    stats_queryset = cache.get(settings.CACHE_STATS_QUERYSET_KEY)
    print('stats_queryset', stats_queryset)

    if stats_queryset is None:
        stats_queryset = Statistics.objects.all()
        cache.set(settings.CACHE_STATS_QUERYSET_KEY, stats_queryset, timeout=60)

    for stats in stats_queryset:
        # статистика за неделю
        cached_stats_week = cache.get(f"{settings.CACHE_STATS_WEEK_KEY}_{stats.volunteer.id}")

        if cached_stats_week is None:
            cached_stats_week = stats.save_weekly_statistics()
            cache.set(f"{settings.CACHE_STATS_WEEK_KEY}_{stats.volunteer.id}", cached_stats_week, timeout=60)

        weekly_stats_record, _ = StatisticsByWeek.objects.update_or_create(
            user=stats.volunteer,
            defaults={
                'points': cached_stats_week['total_points'],
                'hours': cached_stats_week['total_volunteer_hours']
            }
        )

        if not _:
            weekly_stats_record.points = cached_stats_week['total_points']
            weekly_stats_record.hours = cached_stats_week['total_volunteer_hours']
            weekly_stats_record.save()

        # статистика за месяц
        cached_stats_month = cache.get(f"{settings.CACHE_STATS_MONTH_KEY}_{stats.volunteer.id}")

        if cached_stats_month is None:
            cached_stats_month = stats.save_monthly_statistics()
            cache.set(f"{settings.CACHE_STATS_MONTH_KEY}_{stats.volunteer.id}", cached_stats_month, timeout=60)

        month_stats_record, _ = StatisticsByMonth.objects.update_or_create(
            user=stats.volunteer,
            defaults={
                'points': cached_stats_month['total_points'],
                'hours': cached_stats_month['total_volunteer_hours']
            }
        )

        if not _:
            month_stats_record.points = cached_stats_month['total_points']
            month_stats_record.hours = cached_stats_month['total_volunteer_hours']
            month_stats_record.save()

        # статистика за год
        cached_stats_year = cache.get(f"{settings.CACHE_STATS_YEAR_KEY}_{stats.volunteer.id}")

        if cached_stats_year is None:
            cached_stats_year = stats.save_yearly_statistics()
            cache.set(f"{settings.CACHE_STATS_YEAR_KEY}_{stats.volunteer.id}", cached_stats_year, timeout=3600)

        year_stats_record, _ = StatisticsByYear.objects.update_or_create(
            user=stats.volunteer,
            defaults={
                'points': cached_stats_year['total_points'],
                'hours': cached_stats_year['total_volunteer_hours']
            }
        )

        if not _:
            year_stats_record.points = cached_stats_year['total_points']
            year_stats_record.hours = cached_stats_year['total_volunteer_hours']
            year_stats_record.save()


@shared_task
def all_statistics():
    all_stats = cache.get(settings.CACHE_STATS_ALL_KEY)

    if all_stats is None:
        all_stats = all_statistics_week()
        cache.set(settings.CACHE_STATS_ALL_KEY, all_stats, timeout=60)

    try:
        all_statistic = AllStatistics.objects.get()
        print('all_statistic', all_statistic)
        all_statistic.points_week = all_stats['week_points']
        all_statistic.hours_week = all_stats['week_hours']
        all_statistic.points_month = all_stats['month_points']
        all_statistic.hours_month = all_stats['month_hours']
        all_statistic.points_year = all_stats['year_points']
        all_statistic.hours_year = all_stats['year_hours']
        all_statistic.save()
    except AllStatistics.DoesNotExist:
        AllStatistics.objects.create(
            points_week=all_stats['week_points'],
            hours_week=all_stats['week_hours'],
            points_month=all_stats['month_points'],
            hours_month=all_stats['month_hours'],
            points_year=all_stats['year_points'],
            hours_year=all_stats['year_hours']
        )
