from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm

from .models import Promotion, PromoCategory


class BaseAdmin(ModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


class UsersInline(admin.TabularInline):
    model = Promotion.users.through
    extra = 0

    can_delete = False


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
        'display_volunteers',
    )
    fields = (
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
    inlines = [UsersInline, ]
    readonly_fields = (UsersInline, )
    list_filter = ('is_active', 'city', 'category', ('start_date', RangeDateFilter))
    search_fields = ('name', 'start_date', 'description')
    ordering = ('-start_date',)
    list_editable = ('price', 'is_active', 'quantity', 'for_curators_only')


@admin.register(PromoCategory)
class PromoCategoryAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)
