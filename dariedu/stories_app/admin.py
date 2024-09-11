from django.contrib import admin

from .models import Stories

@admin.register(Stories)
class StoriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'link_name', 'hidden')
    list_filter = ('hidden',)
    search_fields = ('title', 'link_name', 'text')
