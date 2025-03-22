# from django.db.models import Sum
# from datetime import timedelta
# from django.utils import timezone
#
#
# def last_week_statistics(self):
#     from .models import Statistics
#
#     today = timezone.now().date()
#     start_week = today - timedelta(days=7)
#
#     weekly_stats = Statistics.objects.filter(
#         volunteer=self.volunteer,
#         period__gte=start_week
#     ).aggregate(
#         total_points=Sum('points'),
#         total_volunteer_hours=Sum('volunteer_hours')
#     )
#
#     return weekly_stats
#
#
# def last_month_statistics(self):
#     from .models import Statistics
#
#     today = timezone.now().date()
#     start_month = today.replace(day=1)
#
#     monthly_stats = Statistics.objects.filter(
#         volunteer=self.volunteer,
#         period__gte=start_month
#     ).aggregate(
#         total_points=Sum('points'),
#         total_volunteer_hours=Sum('volunteer_hours')
#     )
#
#     return monthly_stats
#
#
# def last_year_statistics(self):
#     from .models import Statistics
#
#     today = timezone.now().date()
#     start_year = today.replace(month=1, day=1)
#
#     yearly_stats = Statistics.objects.filter(
#         volunteer=self.volunteer,
#         period__gte=start_year
#     ).aggregate(
#         total_points=Sum('points'),
#         total_volunteer_hours=Sum('volunteer_hours')
#     )
#
#     return yearly_stats
#
#
# def all_statistics_week():
#     from .models import Statistics
#
#     today = timezone.now().date()
#     start_week = today - timedelta(days=7)
#
#     weekly_stats = Statistics.objects.filter(period__gte=start_week).aggregate(
#         week_points=Sum('points'),
#         week_hours=Sum('volunteer_hours')
#     )
#
#     start_month = today.replace(day=1)
#
#     monthly_stats = Statistics.objects.filter(period__gte=start_month).aggregate(
#         month_points=Sum('points'),
#         month_hours=Sum('volunteer_hours')
#     )
#
#     start_year = today.replace(month=1, day=1)
#
#     yearly_stats = Statistics.objects.filter(period__gte=start_year).aggregate(
#         year_points=Sum('points'),
#         year_hours=Sum('volunteer_hours')
#     )
#
#     all_stats = {
#         'week_points': weekly_stats['week_points'] or 0,
#         'week_hours': weekly_stats['week_hours'] or 0,
#         'month_points': monthly_stats['month_points'] or 0,
#         'month_hours': monthly_stats['month_hours'] or 0,
#         'year_points': yearly_stats['year_points'] or 0,
#         'year_hours': yearly_stats['year_hours'] or 0,
#     }
#
#     return all_stats
