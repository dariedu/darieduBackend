import datetime
import zoneinfo
from typing import Optional

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import ForeignKey
from django.forms import ModelChoiceField
from django.http import HttpRequest
from django.utils.html import format_html

from import_export.admin import ImportExportModelAdmin, ExportActionMixin

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.decorators import action
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)
from django import forms

from .export_XLSX import CombinedResource, CombinedResourceDelivery
from .models import Delivery, Task, DeliveryAssignment, TaskCategory, TaskParticipation


User = get_user_model()

ZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


class VolunteerTaskInline(admin.TabularInline):
    model = TaskParticipation
    extra = 0
    readonly_fields = ('volunteer', 'confirmed')
    can_delete = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_completed=False)


@admin.register(Task)
class TaskAdmin(BaseAdmin, ExportActionMixin):
    resource_class = CombinedResource
    actions = ['export_as_xlsx']
    inlines = [VolunteerTaskInline]

    @admin.display(description="описание доброго дела")
    def description_short(self, obj):
        if obj.description:
            return obj.description[:40] + '...' if len(obj.description) > 40 else obj.description
        return None

    @admin.display(description="дата начала")
    def start_date_format(self, obj):
        return obj.start_date.astimezone(ZONE).strftime("%d.%m.%y %H:%M")

    @admin.display(description="дата конца")
    def end_date_format(self, obj):
        return obj.end_date.astimezone(ZONE).strftime("%d.%m.%y %H:%M")

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
    readonly_fields = ('volunteers', 'is_one_day')  # TODO maybe we should have opportunity to edit volunteers
    search_fields = ('name', 'start_date', 'description')
    ordering = ('-start_date',)
    start_date_format.admin_order_field = 'start_date'
    end_date_format.admin_order_field = 'end_date'

    @action(description="Копировать")
    def copy(self, request, queryset, *args):
        """Copy creates for next week, not active"""
        for obj in queryset:
            new_obj = Task.objects.create(
                name=obj.name,
                description=obj.description,
                category=obj.category,
                start_date=obj.start_date + datetime.timedelta(days=7),
                end_date=obj.end_date + datetime.timedelta(days=7),
                volunteer_price=obj.volunteer_price,
                curator_price=obj.curator_price,
                is_active=False,
                city=obj.city,
                volunteers_needed=obj.volunteers_needed,
                volunteers_taken=0,
                curator=obj.curator,
                is_completed=False,
            )
            # new_obj.volunteers = None
            new_obj.save()

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions['copy'] = (
            self.copy.__func__,
            'copy',
            'Копировать'
        )
        return actions

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
    # formfield_overrides = {
    #     models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    # }


@admin.register(Delivery)
class DeliveryAdmin(BaseAdmin, ExportActionMixin):
    resource_class = CombinedResourceDelivery
    actions = ['export_as_xlsx']

    @admin.display(description="дата начала")
    def date_format(self, obj):
        return format_html(f'<b>{obj.date.astimezone(ZONE).strftime("%d.%m.%y %H:%M")}</b>')

    list_display = (
        'date_format',
        'location',
        'display_route_sheet',
        'curator',
        'volunteers_needed',
        'volunteers_taken',
        'display_volunteers',
        'is_active',
        'is_free',
        'in_execution',
        'is_completed',
        'price',
    )
    list_display_links = ('date_format', 'location', 'display_route_sheet')
    list_filter = ['is_active', 'is_free', 'is_completed', 'in_execution',
                   ('date', RangeDateFilter)]

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
        # 'assignments',
    )
    list_editable = ('is_active', 'is_completed', 'in_execution', 'is_free', 'volunteers_needed')
    inlines = [VolunteerInline, ]

    @action(description="Копировать")
    def copy(self, request, queryset, *args):
        """Copy creates for next week, not active"""
        for obj in queryset:
            new_obj = Delivery.objects.create(
                date=obj.date + datetime.timedelta(days=7),
                price=obj.price,
                curator=obj.curator,
                location=obj.location,
                is_free=True,
                is_active=False,
                is_completed=False,
                in_execution=False,
                volunteers_needed=obj.volunteers_needed,
                volunteers_taken=0,
            )
            new_obj.route_sheet.add(*obj.route_sheet.all())
            new_obj.save()

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions['copy'] = (
            self.copy.__func__,
            'copy',
            'Копировать'
        )
        return actions

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
