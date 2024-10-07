from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Feedback, RequestMessage, PhotoReport


class BaseAdmin(ModelAdmin):
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
    created_at_format.admin_order_field = 'start_date'

    list_display = ('id', 'type', 'user', 'created_at_format', 'text_short')
    list_filter = ('type', 'user')
    search_fields = ('text',)


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
    date_format.admin_order_field = 'start_date'
    list_display = (
        "type",
        "text_short",
        "user",
        'form',
        'date_format',
    )
    list_filter = ('type', 'date', 'user')
    search_fields = ('type', 'text', 'user', 'date')


@admin.register(PhotoReport)
class PhotoReportAdmin(BaseAdmin):
    list_display = (
        "address",
        "photo",
        "date",
        "user",
        'comment',
    )
    list_filter = ('date', 'user')
    search_fields = ('address', 'user', 'comment')
