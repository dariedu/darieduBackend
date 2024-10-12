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
    list_display = ('user', )
    fields = ('user', )
    readonly_fields = ('user', )
    can_delete = False
    verbose_name = 'участник'
    verbose_name_plural = 'участники'


@admin.register(Promotion)
class PromotionAdmin(BaseAdmin):

    @admin.display(description="описание поощрения")
    def description_short(self, obj):
        if obj.description:
            return obj.description[:45] + '...' if len(obj.description) > 45 else obj.description
        return None

    @admin.display(description="дата начала")
    def start_date_format(self, obj):
        return obj.start_date.strftime("%d.%m.%y %H:%M")
    start_date_format.admin_order_field = 'start_date'

    @admin.display(description="дата конца")
    def end_date_format(self, obj):
        if obj.end_date:
            return obj.end_date.strftime("%d.%m.%y %H:%M")
        return None
    end_date_format.admin_order_field = 'end_date'

    list_display = (
        'name',
        'category',
        'address',
        'price',
        'is_active',
        'start_date_format',
        'is_permanent',
        'end_date_format',
        'available_quantity',
        'quantity',
        'for_curators_only',
        'description_short',
        'city',
        'display_volunteers',
    )
    fields = (
        'name',
        'category',
        'address',
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
        'picture',
    )
    inlines = [UsersInline, ]
    list_filter = ('is_active', 'city', 'category', 'for_curators_only', 'available_quantity', 'start_date')
    search_fields = ('name', 'start_date', 'description')
    ordering = ('-start_date',)
    list_editable = ('price', 'is_active', 'quantity', 'for_curators_only')
    list_display_links = ('name', 'category')


@admin.register(PromoCategory)
class PromoCategoryAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)
