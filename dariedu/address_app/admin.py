from typing import Optional
import logging

from django.contrib import admin
from django.contrib.admin.actions import action
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db.models import ForeignKey
from django.forms import ModelChoiceField
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm

from user_app.models import User
from .forms import AddToRouteSheetForm, AddToLocationForm
from .models import Address, Beneficiar, City, Location, RouteSheet


logging.basicConfig(level=logging.INFO)


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


@admin.register(Address)
class AddressAdmin(BaseAdmin):

    list_display = ('route_sheet', 'location', 'address', 'display_beneficiar', 'display_comment')
    fields = ('address', 'link', 'location', 'route_sheet')
    list_filter = ('location__city', 'location', 'route_sheet')
    search_fields = ('address', 'location__city', 'location')
    inlines = [BeneficiarInline, ]
    list_display_links = ('address', 'route_sheet', 'location')
    autocomplete_fields = ['location', 'route_sheet']

    @action(description='Добавить в маршрутный лист')
    def add_addresses_to_route_sheet(self, request, queryset):
        if 'apply' in request.POST:
            form = AddToRouteSheetForm(request.POST)
            if form.is_valid():
                route_sheet_id = form.cleaned_data['route_sheet']
                for address in queryset:
                    address.route_sheet = route_sheet_id
                    address.save()
                self.message_user(request, f"Адреса добавлены в маршрутный лист {route_sheet_id.name}")
                return HttpResponseRedirect(reverse('admin:address_app_address_changelist'))
        else:
            form = AddToRouteSheetForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})

        return render(request, 'admin/select_route_sheet.html',
                      {'addresses': queryset,
                       'form': form,
                       'title': 'Добавить в маршрутный лист'})

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions['add_addresses_to_route_sheet'] = (
            self.add_addresses_to_route_sheet.__func__,
            'add_addresses_to_route_sheet',
            'Добавить в маршрутный лист'
        )
        actions['add_addresses_to_location'] = (
            self.add_addresses_to_location.__func__,
            'add_addresses_to_location',
            'Добавить к локации'
        )
        return actions

    def change_view(self, request, object_id, form_url='add_route_sheet', extra_context=None):
        extra_context = extra_context or {}
        extra_context['route_sheets'] = RouteSheet.objects.all()
        extra_context['locations'] = Location.objects.all()
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    @action(description='Добавить к локации')
    def add_addresses_to_location(self, request, queryset):
        if 'apply' in request.POST:
            form = AddToLocationForm(request.POST)
            if form.is_valid():
                location_id = form.cleaned_data['location']
                for address in queryset:
                    address.location = location_id
                    address.save()
                self.message_user(request, f"Адреса добавлены к локации {location_id.address}")
                return HttpResponseRedirect(reverse('admin:address_app_address_changelist'))
        else:
            form = AddToLocationForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})

        return render(request, 'admin/select_location.html',
                      {'addresses': queryset,
                       'form': form,
                       'title': 'Добавить к локации'})


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
    list_display_links = ('address', 'subway', 'curator')

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

    autocomplete_fields = ('user', 'location')
    list_display = ('name', 'location', 'display_address', 'display_curator',  'user')
    fields = ('name', 'map', 'location', 'user')
    inlines = [AddressInline, ]
    list_filter = ('location',)
    search_fields = ('name', 'location__address')
    list_display_links = ('name', 'location')


@admin.register(Beneficiar)
class BeneficiarAdmin(BaseAdmin):
    list_display = ('full_name', 'address', 'phone', 'photo_link', 'presence', 'category', 'comment')
    search_fields = ('full_name', 'phone', 'address', 'comment')
    list_filter = ('address', 'category', 'presence')
    list_display_links = ('full_name', 'phone', 'address')
    autocomplete_fields = ['address']
    list_editable = ('presence', )
