from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Feedback, RequestMessage, PhotoReport


class BaseAdmin(ModelAdmin):
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'user', 'created_at')
    list_filter = ('type', 'user')
    search_fields = ('text',)


@admin.register(RequestMessage)
class RequestMessageAdmin(BaseAdmin):
    list_display = (
        "type",
        "text",
        "user",
        'form',
    )
    list_filter = ('type',)
    search_fields = ('type', 'text', 'user')


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
