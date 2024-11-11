from django.contrib import admin
from .models import *
from django.db.models import Sum

@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ('__str__',)  # Диапазон дат недели
    ordering = ('-start_date',)  # Сортировка по дате начала недели


@admin.register(WeeklyVolunteerStats)
class WeeklyVolunteerStatsAdmin(admin.ModelAdmin):
    # Показываем волонтера, диапазон недели, часы и баллы
    list_display = ('volunteer', 'week_range', 'hours', 'points')

    # Добавляем фильтрацию по дате начала недели, чтобы можно было выбрать нужные недели
    date_hierarchy = 'start_date'
    list_filter = ('start_date',)
    ordering = ('-start_date',)

    def week_range(self, obj):
        """Метод для отображения диапазона недельной статистики."""
        return f'{obj.start_date} – {obj.end_date}'
    week_range.short_description = 'Неделя'


# @admin.register(WeeklyVolunteerStats)
# class WeeklyVolunteerStatsAdmin(admin.ModelAdmin):
#     list_display = ('volunteer_name', 'hours', 'points')
#     list_filter = (
#         ("start_date", DateRangeFilterBuilder()),
#     )
#     search_fields = ('volunteer__last_name', 'volunteer__name',)
#     ordering = ('-hours',)  # Сортировка по убыванию часов
#
#     def volunteer_name(self, obj):
#         return f'{obj.volunteer.last_name} {obj.volunteer.name}'
#
#     volunteer_name.short_description = 'Имя волонтера'




@admin.register(MonthlyVolunteerStats)
class MonthlyVolunteerStatsAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'hours', 'points')
    list_filter = ('volunteer', 'start_date', 'end_date')
    search_fields = ('volunteer__last_name', 'volunteer__name',)
    ordering = ('-hours',)  # Сортировка по убыванию часов

    def volunteer_name(self, obj):
        return f'{obj.volunteer.last_name} {obj.volunteer.name}'

    volunteer_name.short_description = 'Имя волонтера'


@admin.register(ConsolidatedMonthlyStats)
class ConsolidatedMonthlyStatsAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'total_hours', 'total_points')
    search_fields = ('start_date', 'end_date')
    ordering = ('-total_hours',)  # Сортировка по убыванию общего количества часов