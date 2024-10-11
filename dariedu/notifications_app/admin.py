from unfold.admin import ModelAdmin
from django.contrib import admin
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm

from .models import Notification


class BaseAdmin(ModelAdmin):
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
        return obj.created.strftime("%d.%m.%y %H:%M")
    created_format.admin_order_field = 'created'

    list_display = ('title', 'text', 'created_format')
    list_filter = ('created',)
    readonly_fields = ('title', 'text', 'created')
    search_fields = ('title', 'text', 'created')
    list_display_links = ('title', 'text')
