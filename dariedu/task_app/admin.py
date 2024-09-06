from django.contrib import admin
from django.db.models import TextChoices
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)
from unfold.decorators import display

from .models import Delivery, Task
from django.utils.translation import gettext_lazy as _


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Task)
class TaskAdmin(BaseAdmin):
    list_display = (
        'name',
        'description',
        'date',
        'category',
        'price',
        'duration',
        'quantity',
        'is_active',
        'volunteer',
        'curator',
        'city',
    )
    list_filter = ['is_active', 'category', ('date', RangeDateFilter)]
    search_fields = ('name', 'date', 'description')
    ordering = ('-date',)


@admin.register(Delivery)
class DeliveryAdmin(BaseAdmin):
    list_display = (
        'date',
        'price',
        'is_free',
        'is_active',
        'volunteer',
        'route_sheet'
    )
    list_filter = ['is_active', 'is_free', 'route_sheet', ('date', RangeDateFilter)]
    search_fields = ('date', 'route_sheet')
    ordering = ('-date',)
