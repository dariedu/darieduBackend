from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)
from .models import Statistics, StatisticsByWeek, StatisticsByMonth, StatisticsByYear, AllStatistics


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True

# TODO: Удалить перед слиянием в main
@admin.register(Statistics)
class StatsAdmin(BaseAdmin):
    list_display = ('volunteer', 'volunteer_hours', 'period', 'points')
    list_filter = ('period', 'volunteer')
    search_fields = ('volunteer__username',)
    ordering = ('-volunteer_hours',)


@admin.register(StatisticsByWeek)
class StatsByWeekAdmin(BaseAdmin):
    list_display = ('user', 'hours', 'points')
    list_filter = ('user',)
    search_fields = ('user__username',)
    readonly_fields = ('user', 'hours', 'points')
    ordering = ('-hours',)


@admin.register(StatisticsByMonth)
class StatsByMonthAdmin(BaseAdmin):
    list_display = ('user', 'hours', 'points')
    list_filter = ('user',)
    search_fields = ('user__username',)
    readonly_fields = ('user', 'hours', 'points')
    ordering = ('-hours',)


@admin.register(StatisticsByYear)
class StatsByYearAdmin(BaseAdmin):
    list_display = ('user', 'hours', 'points')
    list_filter = ('user',)
    search_fields = ('user__username',)
    readonly_fields = ('user', 'hours', 'points')
    ordering = ('-hours',)


@admin.register(AllStatistics)
class AllStatsAdmin(BaseAdmin):
    list_display = ('points_week', 'hours_week', 'points_month', 'hours_month', 'points_year',
                    'hours_year')
    # list_filter = ('user',)
    search_fields = ('points_week', 'hours_week', 'points_month', 'hours_month', 'points_year',
                     'hours_year',)
    readonly_fields = ('points_week', 'hours_week', 'points_month', 'hours_month', 'points_year',
                       'hours_year')
    ordering = ('-hours_week', '-points_week')
