from django.contrib import admin
from import_export.forms import ImportForm
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import SelectableFieldsExportForm

from .models import Feedback, RequestMessage, PhotoReport


class BaseAdmin(ModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Feedback)
class FeedbackAdmin(BaseAdmin):

    @admin.display(description="текст заявки")
    def text_short(self, obj):
        if obj.text:
            return obj.text[:45] + '...' if len(obj.text) > 45 else obj.text
        return None

    @admin.display(description="дата")
    def created_at_format(self, obj):
        return obj.created_at.strftime("%d.%m.%y %H:%M")
    created_at_format.admin_order_field = 'created_at'

    list_display = ('type', 'user', 'text_short', 'created_at_format')
    list_filter = ('type', 'user', 'created_at')
    search_fields = ('text',)
    list_display_links = ('text_short', 'type', 'user')
    autocomplete_fields = ('user', )
    # readonly_fields = ('type', 'user', 'text', 'created_at')  # for prod


@admin.register(RequestMessage)
class RequestMessageAdmin(BaseAdmin):

    @admin.display(description="текст заявки")
    def text_short(self, obj):
        if obj.text:
            return obj.text[:45] + '...' if len(obj.text) > 45 else obj.text
        return None

    @admin.display(description="дата")
    def date_format(self, obj):
        return obj.date.strftime("%d.%m.%y %H:%M")
    date_format.admin_order_field = 'date'
    list_display = (
        "type",
        "text_short",
        "user",
        'date_format',
    )
    list_filter = ('type', 'date', 'user')
    search_fields = ('type', 'text', 'user', 'date')
    list_display_links = ('text_short', 'type', 'user')
    autocomplete_fields = ('user', )

    # readonly_fields = ('type', 'user', 'text', 'date')  # for prod


@admin.register(PhotoReport)
class PhotoReportAdmin(BaseAdmin):
    @admin.display(description="дата")
    def date_format(self, obj):
        return obj.date.strftime("%d.%m.%y %H:%M")
    date_format.admin_order_field = 'date'

    list_display = (
        "address",
        "photo_view",
        "display_beneficiar",
        "date_format",
        "user",
        'comment',
    )
    list_filter = ('date', 'user', 'address')
    search_fields = ('address', 'user', 'comment')
    list_display_links = ('address', 'display_beneficiar')
    autocomplete_fields = ('user', )

    # readonly_fields = ('type', 'user', 'text', 'date')  # for prod
