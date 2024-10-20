from typing import Optional

from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import ForeignKey
from django.forms import ModelChoiceField
from django.http import HttpRequest
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)

from import_export.admin import ExportActionMixin

from user_app.models import User

from .export_XLSX import CombinedResource, CombinedResourceDelivery
from .models import Delivery, Task, DeliveryAssignment, TaskCategory


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Task)
class TaskAdmin(BaseAdmin, ExportActionMixin):
    resource_class = CombinedResource
    actions = ['export_as_xlsx']

    @admin.display(description="описание доброго дела")
    def description_short(self, obj):
        if obj.description:
            return obj.description[:40] + '...' if len(obj.description) > 40 else obj.description
        return None

    @admin.display(description="дата начала")
    def start_date_format(self, obj):
        return obj.start_date.strftime("%d.%m.%y %H:%M")

    @admin.display(description="дата конца")
    def end_date_format(self, obj):
        return obj.end_date.strftime("%d.%m.%y %H:%M")

    list_display = (
        'start_date_format',
        'end_date_format',
        'name',
        'description_short',
        'category',
        'volunteer_price',
        'curator_price',
        'volunteers_needed',
        'volunteers_taken',
        'is_active',
        'is_completed',
        'curator',
        'city',
    )
    list_display_links = ('start_date_format', 'end_date_format', 'name', 'description_short')
    list_editable = ('volunteer_price', 'curator_price', 'volunteers_needed', 'is_active', 'is_completed')
    list_filter = ['is_active', 'category', 'start_date']
    readonly_fields = ('volunteers', )  # TODO maybe we should have opportunity to edit volunteers
    search_fields = ('name', 'start_date', 'description')
    ordering = ('-start_date',)
    start_date_format.admin_order_field = 'start_date'
    end_date_format.admin_order_field = 'end_date'

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs
    ) -> Optional[ModelChoiceField]:
        if db_field.name == 'curator':
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(TaskCategory)
class TaskCategoryAdmin(BaseAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)


class VolunteerInline(admin.TabularInline):
    model = DeliveryAssignment
    extra = 0

    can_delete = False
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }


@admin.register(Delivery)
class DeliveryAdmin(BaseAdmin, ExportActionMixin):
    resource_class = CombinedResourceDelivery
    actions = ['export_as_xlsx']

    @admin.display(description="дата начала")
    def date_format(self, obj):
        return obj.date.strftime("%d.%m.%y %H:%M")

    list_display = (
        'location',
        'display_route_sheet',
        'date_format',
        'price',
        'is_active',
        'is_free',
        'in_execution',
        'is_completed',
        'curator',
        'volunteers_needed',
        'volunteers_taken',
        'display_volunteers',
    )
    list_display_links = ('date_format', 'location', 'display_route_sheet')
    list_filter = ['is_active', 'is_free', 'is_completed', 'in_execution',
                   ('date', RangeDateFilter)]

    search_fields = ('date', 'route_sheet')
    ordering = ('-date',)
    date_format.admin_order_field = 'date'
    fields = (
        'date',
        'price',
        'curator',
        'location',
        'is_free',
        'is_active',
        'is_completed',
        'in_execution',
        'volunteers_needed',
        'volunteers_taken',
        'route_sheet',
    )
    list_editable = ('is_active', 'is_completed', 'in_execution', 'is_free', 'volunteers_needed')

    inlines = [VolunteerInline, ]

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs
    ) -> Optional[ModelChoiceField]:
        if db_field.name == 'curator':
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(BaseAdmin):
    list_display = (
        'delivery',
    )
