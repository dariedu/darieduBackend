from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)

from .models import Stories


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Stories)
class StoriesAdmin(BaseAdmin):

    @admin.display(description="Текст сториса")
    def text_short(self, obj):
        if obj.text:
            return obj.text[:40] + '...' if len(obj.text) > 40 else obj.text
        return None

    list_display = ('title', 'link_name', 'text_short', 'hidden')
    list_filter = ('hidden',)
    search_fields = ('title', 'link_name', 'text')
    list_editable = ('hidden',)
    list_display_links = ('title', 'link_name')
