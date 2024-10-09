from typing import Optional

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper, ForeignKeyRawIdWidget
from django.db import models
from django.db.models import ForeignKey
from django.forms import ModelChoiceField, Select, Widget
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldForeignKeyRawIdWidget, UnfoldRelatedFieldWidgetWrapper

from task_app.models import Delivery
from user_app.models import User
from .models import Address, Beneficiar, City, Location, RouteSheet


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


class BeneficiarInline(TabularInline):
    model = Beneficiar
    extra = 0
    list_display = ('full_name', 'phone', 'comment')
    fields = ('full_name', 'phone', 'address', 'comment')
    can_delete = False


class AddressInline(TabularInline):
    model = Address
    extra = 0
    fields = ('address', 'link')
    can_delete = False


class RouteSheetInline(TabularInline):
    model = RouteSheet
    extra = 0
    fields = ('name', )
    can_delete = False
    # readonly_fields = ('name', )


@admin.register(Address)
class AddressAdmin(BaseAdmin):

    # TODO add action to add address into route sheet and to location
    list_display = ('route_sheet', 'location', 'address', 'display_beneficiar', 'display_comment')
    fields = ('address', 'link', 'location', 'route_sheet')
    list_filter = ('location__city', 'location', 'route_sheet')
    search_fields = ('address', 'location__city', 'location')
    inlines = [BeneficiarInline, ]
    readonly_fields = (BeneficiarInline, )


@admin.register(Location)
class LocationAdmin(BaseAdmin):

    @admin.display(description='описание')
    def short_description(self, obj):
        if obj.description:
            return obj.description[:40] + '...' if len(obj.description) > 40 else obj.description
        return None

    list_display = ('address', 'subway', 'curator', 'media_files', 'city', 'short_description')
    list_filter = ('city', 'curator')
    search_fields = ('address', 'city', 'subway', 'curator__last_name')
    fields = ('address', 'link', 'subway', 'curator', 'media_files', 'city', 'description')
    inlines = [AddressInline, RouteSheetInline]
    # readonly_fields = (AddressInline, )

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs
    ) -> Optional[ModelChoiceField]:
        if db_field.name == 'curator':
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(City)
class CityAdmin(BaseAdmin):
    list_display = ('city',)


@admin.register(RouteSheet)
class RouteSheetAdmin(BaseAdmin):

    autocomplete_fields = ('user',)
    list_display = ('name', 'user', 'map', 'location', 'display_curator', 'display_address')
    fields = ('name', 'map', 'location', 'user')
    inlines = [AddressInline, ]
    readonly_fields = (AddressInline,)
    list_filter = ('location',)


@admin.register(Beneficiar)
class BeneficiarAdmin(BaseAdmin):
    list_display = ('full_name', 'phone', 'address', 'category', 'comment')
    search_fields = ('full_name', 'phone', 'address')
    list_filter = ('address',)

