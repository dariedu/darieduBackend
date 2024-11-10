# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import WeeklyVolunteerStats, ConsolidatedMonthlyStats, MonthlyVolunteerStats
# from django.db.models import Sum
# import logging
#
# logger = logging.getLogger(__name__)
#
#
#
# @receiver(post_save, sender=WeeklyVolunteerStats)
# def update_weekly_and_consolidated_stats(sender, instance, created, **kwargs):
#     """
#     Сигнал для обновления статистики по часам и баллам после сохранения записи
#     о статистике волонтера за неделю.
#     """
#     # Если запись создана (не обновлена), то выполняем действия по обновлению статистики
#     if created:
#         logger.info(f"Создана запись WeeklyVolunteerStats: {instance.start_date} - {instance.end_date}")
#         # Обновление статистики для конкретного волонтера
#         # Подсчитываем текущие часы и баллы волонтёра
#         instance.volunteer.volunteer_hour = instance.hours
#         instance.volunteer.point = instance.points
#         instance.volunteer.save()
#
#         # Подсчитываем суммарные часы и баллы по всем волонтёрам за этот период
#         start_date = instance.start_date
#         end_date = instance.end_date
#
#         # Агрегируем данные по часам и баллам за неделю для всех волонтёров
#         stats = WeeklyVolunteerStats.objects.filter(start_date__gte=start_date, end_date__lte=end_date).aggregate(
#             total_hours=Sum('hours'),
#             total_points=Sum('points')
#         )
#
#         # Создаем или обновляем сводную статистику за этот период (по месяцам)
#         consolidated_stat, created = ConsolidatedMonthlyStats.objects.get_or_create(
#             start_date=start_date,
#             end_date=end_date
#         )
#
#         # Обновляем сводную статистику по часам и баллам
#         consolidated_stat.total_hours = stats['total_hours'] or 0
#         consolidated_stat.total_points = stats['total_points'] or 0
#         consolidated_stat.save()
#
#
#
# @receiver(post_save, sender=MonthlyVolunteerStats)
# def update_monthly_stats(sender, instance, created, **kwargs):
#     """
#     Сигнал для обновления статистики волонтёра за месяц и сводной статистики.
#     """
#     # Если запись была создана, обновляем статистику
#     if created:
#         # Обновляем данные по часам и баллам волонтёра
#         instance.volunteer.volunteer_hour = instance.hours
#         instance.volunteer.point = instance.points
#         instance.volunteer.save()
#
#         # Агрегируем данные по всем волонтёрам за текущий месяц
#         start_date = instance.start_date
#         end_date = instance.end_date
#
#         # Агрегируем данные по часам и баллам для всех волонтёров
#         stats = MonthlyVolunteerStats.objects.filter(start_date__gte=start_date, end_date__lte=end_date).aggregate(
#             total_hours=Sum('hours'),
#             total_points=Sum('points')
#         )
#
#         # Создаем или обновляем сводную статистику для текущего месяца
#         consolidated_stat, created = ConsolidatedMonthlyStats.objects.get_or_create(
#             start_date=start_date,
#             end_date=end_date
#         )
#
#         # Обновляем суммарные часы и баллы
#         consolidated_stat.total_hours = stats['total_hours'] or 0
#         consolidated_stat.total_points = stats['total_points'] or 0
#         consolidated_stat.save()
