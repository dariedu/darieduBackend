from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from .models import Promotion

class BaseAdmin(ModelAdmin):
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Promotion)
class PromotionAdmin(BaseAdmin):
    list_display = ('category', 'name', 'price', 'description', 'start_date', 'quantity', 'is_active', 'city')
    list_filter = ('is_active', 'city', 'category', ('start_date', RangeDateFilter))
    search_fields = ('name', 'start_date', 'description')
    ordering = ('-start_date',)
