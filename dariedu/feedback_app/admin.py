from django.contrib import admin

from .models import Feedback, RequestMessage


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "text",
        "user",
        'form',
    )
    list_filter = ('type',)
    search_fields = ('type', 'text', 'user')


@admin.register(RequestMessage)
class RequestMessageAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "text",
        "user",
        'form',
    )
    list_filter = ('type',)
    search_fields = ('type', 'text', 'user')
