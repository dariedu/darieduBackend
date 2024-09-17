from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from .models import Promotion, PromoCategory


class BaseAdmin(ModelAdmin):
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Promotion)
class PromotionAdmin(BaseAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'is_active',
        'start_date',
        'is_permanent',
        'end_date',
        'available_quantity',
        'quantity',
        'for_curators_only',
        'description',
        'city',
        'file',
    )
    list_filter = ('is_active', 'city', 'category', ('start_date', RangeDateFilter))
    search_fields = ('name', 'start_date', 'description')
    ordering = ('-start_date',)


@admin.register(PromoCategory)
class PromoCategoryAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)
