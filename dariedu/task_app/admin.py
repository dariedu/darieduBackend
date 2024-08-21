from django.contrib import admin

from .models import Task, Delivery


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
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
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'date', 'description')
    ordering = ('-date',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'price',
        'is_free',
        'is_active',
        'volunteer',
        'route_sheet'
    )
    list_filter = ('is_active', 'is_free', 'route_sheet')
    search_fields = ('date', 'route_sheet')
    ordering = ('-date',)
