from django.contrib import admin
from django.db import models
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)

from .models import Address, Beneficiar, City, Location, RouteSheet


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    warn_unsaved_form = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True

@admin.register(Address)
class AddressAdmin(BaseAdmin):
    list_display = ('address', 'link', 'location', 'route_sheet')
    list_filter = ('location__city', 'location')
    search_fields = ('address', 'location__city', 'location')


@admin.register(Location)
class LocationAdmin(BaseAdmin):
    list_display = ('address', 'link', 'city', 'curator')
    list_filter = ('city', 'curator')
    search_fields = ('address', 'city', 'curator__last_name')


@admin.register(City)
class CityAdmin(BaseAdmin):
    list_display = ('city',)


@admin.register(RouteSheet)
class RouteSheetAdmin(BaseAdmin):
    list_display = ('map', 'address_route_sheet__location')


@admin.register(Beneficiar)
class BeneficiarAdmin(BaseAdmin):
    list_display = ('full_name', 'phone', 'address', 'comment')
    search_fields = ('full_name', 'phone', 'address')
    list_filter = ('address',)

