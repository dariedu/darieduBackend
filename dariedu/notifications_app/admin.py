import zoneinfo

from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm

from .models import Notification


ZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Notification)
class NotificationAdmin(BaseAdmin):

    @admin.display(description="дата")
    def created_format(self, obj):
        return obj.created.astimezone(ZONE).strftime("%d.%m.%y %H:%M")
    created_format.admin_order_field = 'created'

    @admin.display(description="описание")
    def text_short(self, obj):
        if obj.text:
            return obj.text[:90] + '...' if len(obj.text) > 90 else obj.text
        return None

    list_display = ('title', 'text_short', 'get_link', 'created_format')
    list_filter = ('created', 'title')
    readonly_fields = ('title', 'text', 'obj_link', 'created')
    search_fields = ('title', 'text', 'created')
    list_display_links = ('title', 'text_short')

    def get_link(self, obj):
        if obj.obj_link:
            return format_html(f'<a href={obj.obj_link}>Ссылка</a>')

    get_link.short_description = 'Ссылка на объект'
