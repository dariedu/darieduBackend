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

from user_app.models import User
from .models import Delivery, Task, DeliveryAssignment, TaskCategory


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Task)
class TaskAdmin(BaseAdmin):

    # formfield_overrides = {
    #     models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    # }

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
        'is_completed',
        'curator',
        'city',
    )
    list_editable = ('price', 'volunteers_needed', 'is_active', 'is_completed')
    list_filter = ['is_active', 'category', ('start_date', RangeDateFilter)]
    readonly_fields = ('volunteers', )  # TODO maybe we should have opportunity to edit volunteers
    search_fields = ('name', 'start_date', 'description')
    ordering = ('-start_date',)

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
    verbose_name = 'Волонтер'
    verbose_name_plural = 'Волонтеры'


@admin.register(Delivery)
class DeliveryAdmin(BaseAdmin):
    list_display = (
        'location',
        'date',
        'price',
        'is_active',
        'is_free',
        'in_execution',
        'is_completed',
        'curator',
        'volunteers_needed',
        'volunteers_taken',
        'display_route_sheet',
        'display_volunteers',
    )

    list_filter = ['is_active', 'is_free', 'is_completed', 'in_execution',
                   ('date', RangeDateFilter)]

    search_fields = ('date', 'route_sheet')
    ordering = ('-date',)
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
        'route_sheet'
    )  # TODO add volunteers somehow
    inlines = [VolunteerInline, ]
    readonly_fields = (VolunteerInline, )
    list_editable = ('is_active', 'is_completed', 'in_execution', 'is_free', 'volunteers_needed')

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
        'display_volunteers'
    )
