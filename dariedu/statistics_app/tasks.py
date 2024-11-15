# from celery import shared_task
# from django.contrib.auth import get_user_model
# from django.utils import timezone
# from datetime import timedelta
# from .models import *
#
# User = get_user_model()
#
#
# @shared_task
# def create_last_week():
#     """Создает запись для завершившейся недели (понедельник-воскресенье), если её еще нет."""
#     # Определяем текущую дату
#     today = timezone.now().date()
#
#     # Определяем начало и конец прошедшей недели
#     last_week_start = today - timedelta(days=today.weekday() + 7)  # Начало прошлой недели (понедельник)
#     last_week_end = last_week_start + timedelta(days=6)  # Конец прошлой недели (воскресенье)
#
#     # Проверяем, существует ли запись для завершённой недели
#     if not Week.objects.filter(start_date=last_week_start, end_date=last_week_end).exists():
#         # Создаем новую запись для завершённой недели
#         Week.objects.create(start_date=last_week_start, end_date=last_week_end)
#
#
