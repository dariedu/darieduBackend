from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Feedback, Request


class BaseAdmin(ModelAdmin):
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    warn_unsaved_form = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True

@admin.register(Feedback)
class FeedbackAdmin(BaseAdmin):
    list_display = (
        "type",
        "text",
        "user",
        'form',
    )
    list_filter = ('type',)
    search_fields = ('type', 'text', 'user')


@admin.register(Request)
class RequestAdmin(BaseAdmin):
    list_display = (
        "type",
        "text",
        "user",
        'form',
    )
    list_filter = ('type',)
    search_fields = ('type', 'text', 'user')
