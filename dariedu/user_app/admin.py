from django.contrib import admin
from django.db import models
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)

from .models import Rating, User


class UserAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True

    list_display = (
        'tg_id',
        'photo',
        'name',
        'surname',
        'last_name',
        'city_id',
        'email',
        'phone',
        'rating_id',
        'volunteer_hour',
        'is_superuser',
        'is_staff',
    )
    list_filter = (
        'city_id',
        'is_superuser',
        'is_staff',
    )
    fieldsets = [
        (None, {"fields": [
            "tg_id",
            "last_name",
            "name",
            "surname",
            "photo",  # TODO: add preview
            "email",
            "phone",
            # "rating_id", # TODO: add somehow
            # "city_id",
            "volunteer_hour"
        ]}),
        ("Permissions", {"fields": ["is_staff", "is_superuser"]}),
    ]
    search_fields = ('tg_id', 'name', 'surname', 'last_name', 'city_id', 'email', 'phone', 'rating_id')


admin.site.register(User, UserAdmin)
admin.site.register(Rating)

