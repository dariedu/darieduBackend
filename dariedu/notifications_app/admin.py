from unfold.admin import ModelAdmin
from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('title', 'text', 'form', 'created')
    list_filter = ('created',)
    readonly_fields = ('title', 'text', 'form', 'created')
    search_fields = ('title', 'text', 'created')
