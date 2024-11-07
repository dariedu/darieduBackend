import zoneinfo
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from .models import *
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)

User = get_user_model()

ZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)

class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


# Админка для WeeklyVolunteerStats
@admin.register(WeeklyVolunteerStats)
class WeeklyVolunteerStatsAdmin(BaseAdmin):
    list_display = ('volunteer_name', 'start_date', 'end_date', 'hours', 'points')
    list_filter = ('volunteer', 'start_date', 'end_date')
    search_fields = ('volunteer__last_name', 'volunteer__name',)
    ordering = ('-hours',)  # Сортировка по убыванию часов

    def volunteer_name(self, obj):
        return f'{obj.volunteer.last_name} {obj.volunteer.name}'

    volunteer_name.short_description = 'Имя волонтера'

# Админка для MonthlyVolunteerStats
@admin.register(MonthlyVolunteerStats)
class MonthlyVolunteerStatsAdmin(BaseAdmin):
    list_display = ('volunteer_name', 'start_date', 'end_date', 'hours', 'points')
    list_filter = ('volunteer', 'start_date', 'end_date')
    search_fields = ('volunteer__last_name', 'volunteer__name',)
    ordering = ('-hours',)  # Сортировка по убыванию часов

    def volunteer_name(self, obj):
        return f'{obj.volunteer.last_name} {obj.volunteer.name}'

    volunteer_name.short_description = 'Имя волонтера'

# Админка для ConsolidatedMonthlyStats
@admin.register(ConsolidatedMonthlyStats)
class ConsolidatedMonthlyStatsAdmin(BaseAdmin):
    list_display = ('start_date', 'end_date', 'total_hours', 'total_points')
    search_fields = ('start_date', 'end_date')
    ordering = ('-total_hours',)  # Сортировка по убыванию общего количества часов