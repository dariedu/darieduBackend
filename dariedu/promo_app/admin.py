from django.contrib import admin

from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'price', 'description', 'date', 'quantity', 'is_active', 'city', 'user')
    list_filter = ('is_active', 'city', 'category')
    search_fields = ('name', 'date', 'description')
    ordering = ('-date',)
