from django.contrib import admin
from .models import VolunteerStats

@admin.register(VolunteerStats)
class VolunteerStatsAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'week', 'month', 'year', 'hours', 'points')
    list_filter = ('year', 'month', 'week', 'volunteer')
    search_fields = ('volunteer__username',)
    ordering = ('-hours',)  # Сортировка по убыванию часов
