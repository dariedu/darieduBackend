from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
import logging

from statistics_app.models import Statistics, StatisticsByWeek, StatisticsByMonth, StatisticsByYear, AllStatistics
from .methods import all_statistics_week

User = get_user_model()
logger = logging.getLogger('celery_log')


@shared_task
def update_statistics():
    logger.info("Updating statistics")

    stats_queryset = cache.get(settings.CACHE_STATS_QUERYSET_KEY)

    if stats_queryset is None:
        stats_queryset = Statistics.objects.all()
        logger.info("Statistics queryset is from database: %s", stats_queryset)
        cache.set(settings.CACHE_STATS_QUERYSET_KEY, stats_queryset, timeout=60)

    for stats in stats_queryset:
        # статистика за неделю
        cached_stats_week = cache.get(f"{settings.CACHE_STATS_WEEK_KEY}_{stats.volunteer.id}")
        logger.info("Statistics week is from cache: %s", cached_stats_week)

        if cached_stats_week is None:
            cached_stats_week = stats.save_weekly_statistics()
            logger.info("Statistics week is from database: %s", cached_stats_week)
            cache.set(f"{settings.CACHE_STATS_WEEK_KEY}_{stats.volunteer.id}", cached_stats_week, timeout=60)

        total_points = cached_stats_week.get('total_points', 0) or 0
        total_volunteer_hours = cached_stats_week.get('total_volunteer_hours', 0) or 0

        weekly_stats_record, _ = StatisticsByWeek.objects.update_or_create(
            user=stats.volunteer,
            defaults={
                'points': total_points,
                'hours': total_volunteer_hours
            }
        )

        if not _:
            weekly_stats_record.points = total_points
            weekly_stats_record.hours = total_volunteer_hours
            weekly_stats_record.save()
            logger.info("Statistics week is from database: %s", cached_stats_week)

        # статистика за месяц
        cached_stats_month = cache.get(f"{settings.CACHE_STATS_MONTH_KEY}_{stats.volunteer.id}")

        if cached_stats_month is None:
            cached_stats_month = stats.save_monthly_statistics()
            logger.info("Statistics month is from database: %s", cached_stats_month)
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
            logger.info("Statistics month is from database: %s", cached_stats_month)

        # статистика за год
        cached_stats_year = cache.get(f"{settings.CACHE_STATS_YEAR_KEY}_{stats.volunteer.id}")

        if cached_stats_year is None:
            cached_stats_year = stats.save_yearly_statistics()
            logger.info("Statistics year is from database: %s", cached_stats_year)
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
            logger.info("Statistics year is from database: %s", cached_stats_year)


@shared_task
def all_statistics():
    logger.info("Updating all statistics")
    all_stats = cache.get(settings.CACHE_STATS_ALL_KEY)

    if all_stats is None:
        all_stats = all_statistics_week()
        logger.info("All statistics is from database: %s", all_stats)

        cache.set(settings.CACHE_STATS_ALL_KEY, all_stats, timeout=60)

    try:
        all_statistic = AllStatistics.objects.get()
        logger.info('All statistic object', all_statistic)
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
    logger.info("All statistics updated")
