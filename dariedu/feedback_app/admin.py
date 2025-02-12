import zoneinfo

from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export.forms import ImportForm
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import SelectableFieldsExportForm

from .models import Feedback, RequestMessage, PhotoReport


ZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
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
            return obj.text[:90] + '...' if len(obj.text) > 90 else obj.text
        return None

    @admin.display(description="дата")
    def created_at_format(self, obj):
        return obj.created_at.astimezone(ZONE).strftime("%d.%m.%y %H:%M")
    created_at_format.admin_order_field = 'created_at'

    list_display = ('type', 'user', 'text_short', 'created_at_format')
    list_filter = ('type', 'user', 'created_at')
    search_fields = ('text',)
    list_display_links = ('text_short', 'type', 'user')
    autocomplete_fields = ('user', )
    readonly_fields = ('type', 'user', 'text', 'created_at')  # for prod


@admin.register(RequestMessage)
class RequestMessageAdmin(BaseAdmin):

    @admin.display(description="на какой локации")
    def about_location_short(self, obj):
        if obj.about_location:
            return obj.about_location[:45] + '...' if len(obj.about_location) > 45 else obj.about_location
        return None

    @admin.display(description="присутствие")
    def about_presence_short(self, obj):
        if obj.about_presence:
            return obj.about_presence[:45] + '...' if len(obj.about_presence) > 45 else obj.about_presence
        return None

    @admin.display(description="график работы")
    def about_worktime_short(self, obj):
        if obj.about_worktime:
            return obj.about_worktime[:45] + '...' if len(obj.about_worktime) > 45 else obj.about_worktime
        return None

    @admin.display(description="дата")
    def date_format(self, obj):
        return obj.date.strftime("%d.%m.%y")
    date_format.admin_order_field = 'date'
    list_display = (
        "type",
        "about_location_short",
        "about_presence_short",
        "about_worktime_short",
        "user",
        'date_format',
    )
    list_filter = ('type', 'date', 'user')
    search_fields = ('about_location', 'about_presence', 'about_worktime')
    list_display_links = ('type', 'about_location_short', 'about_presence_short', 'about_worktime_short')
    autocomplete_fields = ('user', )

    readonly_fields = ('type', 'user', 'date')  # for prod


@admin.register(PhotoReport)
class PhotoReportAdmin(BaseAdmin):
    @admin.display(description="дата")
    def date_format(self, obj):
        return obj.date.strftime("%d.%m.%y")
    date_format.admin_order_field = 'date'

    list_display = (
        "address",
        "get_link",
        "display_beneficiar",
        "date_format",
        "user",
        'comment',
        'is_absent'
    )
    list_filter = ('date', 'user', 'address')
    search_fields = ('comment',)
    list_display_links = ('address', 'display_beneficiar')
    autocomplete_fields = ('user', )

    readonly_fields = ('user', 'date')  # for prod

    def get_link(self, obj: PhotoReport):
        if obj.photo_view:
            return format_html(f'<a href={obj.photo_view}>Ссылка</a>')

    get_link.short_description = 'Ссылка на фото'
