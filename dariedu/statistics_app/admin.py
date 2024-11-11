from datetime import datetime
from django_admin_filters import DateRange, DateRangePicker
from django.contrib import admin
from .models import *
from rangefilter.filters import (
    DateRangeFilterBuilder,
    DateTimeRangeFilterBuilder,
    NumericRangeFilterBuilder,
    DateRangeQuickSelectListFilterBuilder,
)


User = get_user_model()

class MyDateRange(DateRange):
    FILTER_LABEL = "Интервал данных"
    FROM_LABEL = "От"
    TO_LABEL = "До"
    ALL_LABEL = 'Все'
    CUSTOM_LABEL = "пользовательский"
    NULL_LABEL = "без даты"
    BUTTON_LABEL = "Задать интервал"
    DATE_FORMAT = "YYYY-MM-DD HH:mm"

    is_null_option = True

    options = (
      ('1da', "24 часа вперед", 60 * 60 * 24),
      ('1dp', "последние 24 часа", 60 * 60 * -24),
    )

class MyDateRangePicker(DateRangePicker):
    WIDGET_LOCALE = 'ru'
    WIDGET_BUTTON_LABEL = "Выбрать"
    WIDGET_WITH_TIME = False
    DATE_FORMAT = "DD-MM-YYYY"

    WIDGET_START_TITLE = 'Начальная дата'
    WIDGET_START_TOP = -350
    # WIDGET_START_LEFT = -400

    WIDGET_END_TITLE = 'Конечная дата'
    WIDGET_END_TOP = -350
    # WIDGET_END_LEFT = -400

@admin.register(WeeklyVolunteerStats)
class WeeklyVolunteerStatsAdmin(admin.ModelAdmin):
    list_display = ('volunteer_name', 'hours', 'points')
    list_filter = (('start_date', MyDateRangePicker),)
    search_fields = ('volunteer__last_name', 'volunteer__name',)
    ordering = ('-hours',)  # Сортировка по убыванию часов

    def volunteer_name(self, obj):
        return f'{obj.volunteer.last_name} {obj.volunteer.name}'

    volunteer_name.short_description = 'Имя волонтера'




@admin.register(MonthlyVolunteerStats)
class MonthlyVolunteerStatsAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'hours', 'points')
    list_filter = ('volunteer', 'start_date', 'end_date')
    search_fields = ('volunteer__last_name', 'volunteer__name',)
    ordering = ('-hours',)  # Сортировка по убыванию часов

    # def volunteer_name(self, obj):
    #     return f'{obj.volunteer.last_name} {obj.volunteer.name}'
    #
    # volunteer_name.short_description = 'Имя волонтера'


@admin.register(ConsolidatedMonthlyStats)
class ConsolidatedMonthlyStatsAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'total_hours', 'total_points')
    search_fields = ('start_date', 'end_date')
    ordering = ('-total_hours',)  # Сортировка по убыванию общего количества часов