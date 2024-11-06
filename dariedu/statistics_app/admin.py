from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)
from .models import VolunteerStats


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(VolunteerStats)
class VolunteerStatsAdmin(BaseAdmin):
    list_display = ('volunteer', 'week', 'month', 'year', 'hours', 'points')
    list_filter = ('year', 'month', 'week', 'volunteer')
    search_fields = ('volunteer__username',)
    ordering = ('-hours',)  # Сортировка по убыванию часов
