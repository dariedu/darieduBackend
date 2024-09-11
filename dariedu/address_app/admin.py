from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
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
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Address)
class AddressAdmin(BaseAdmin):
    list_display = ('address', 'link', 'location', 'route_sheet__name')
    list_filter = ('location__city', 'location')
    search_fields = ('address', 'location__city', 'location')


@admin.register(Location)
class LocationAdmin(BaseAdmin):
    list_display = ('address', 'link', 'city', 'curator', 'media_files')
    list_filter = ('city', 'curator')
    search_fields = ('address', 'city', 'curator__last_name')


@admin.register(City)
class CityAdmin(BaseAdmin):
    list_display = ('city',)


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('route_address')


@admin.register(RouteSheet)
class RouteSheetAdmin(BaseAdmin):
    list_display = ('name', 'user', 'map',)
    # inlines = [AddressInline, ]

    # def address_link(self, obj):
    #     url = (
    #             reverse("admin:address_app_address_changelist")
    #             + "?"
    #             + urlencode({"route_address__id": f"{obj.id}"})
    #     )
    #     return format_html('<a href="{}">{} Address</a>', url)
    #
    # address_link.short_description = "Address"


@admin.register(Beneficiar)
class BeneficiarAdmin(BaseAdmin):
    list_display = ('full_name', 'phone', 'address', 'comment')
    search_fields = ('full_name', 'phone', 'address')
    list_filter = ('address',)

