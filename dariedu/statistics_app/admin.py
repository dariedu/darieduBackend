from django.contrib import admin
from .models import *
from django.db.models import Sum
from django.contrib.auth import get_user_model

User = get_user_model()



@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ('__str__',)  # Диапазон дат недели
    ordering = ('-start_date',)  # Сортировка по дате начала недели



@admin.register(VolunteerStats)
class VolunteerStatsAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'volunteer_hours', 'points', 'timestamp')
    list_filter = ('volunteer', 'timestamp')
    search_fields = ('volunteer__name',)
    ordering = ('-timestamp',)
