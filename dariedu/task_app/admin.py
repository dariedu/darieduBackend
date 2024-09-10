from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)
from .models import Delivery, Task, DeliveryAssignment


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
        'start_date',
        'end_date',
        'category',
        'price',
        'volunteers_needed',
        'volunteers_taken',
        'is_active',
        'curator',
        'city',
    )
    list_filter = ['is_active', 'category', ('start_date', RangeDateFilter)]
    search_fields = ('name', 'start_date', 'description')
    ordering = ('-start_date',)


@admin.register(Delivery)
class DeliveryAdmin(BaseAdmin):
    list_display = (
        'date',
        'price',
        'is_active',
        'is_free',
        'in_execution',
        'is_completed',
    )

    list_filter = ['is_active', 'is_free', 'is_completed', 'in_execution',
                   ('date', RangeDateFilter)]
    search_fields = ('date', 'route_sheet')
    ordering = ('-date',)

    @admin.register(DeliveryAssignment)
    class DeliveryAssignmentAdmin(BaseAdmin):
        list_display = (
            'delivery',
            'display_volunteers'
        )

        def display_volunteers(self, obj):
            return ", ".join([f"{volunteer.tg_id}" for volunteer in obj.volunteer.all()])

        display_volunteers.short_description = 'Волонтеры'
