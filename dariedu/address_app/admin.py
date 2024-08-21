from django.contrib import admin

from .models import Address, Location, City, RouteSheet, Beneficiar


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'link', 'location', 'route_sheet')
    list_filter = ('location__city', 'location')
    search_fields = ('address', 'location__city', 'location')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('address', 'link', 'city', 'curator')
    list_filter = ('city', 'curator')
    search_fields = ('address', 'city', 'curator__last_name')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('city',)


@admin.register(RouteSheet)
class RouteSheetAdmin(admin.ModelAdmin):
    list_display = ('map', 'address_route_sheet__location')


@admin.register(Beneficiar)
class BeneficiarAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'address', 'comment')
    search_fields = ('full_name', 'phone', 'address')
    list_filter = ('address',)

