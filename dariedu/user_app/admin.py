from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)

from user_app.models import User, Rating


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


@admin.register(User)
class UserAdmin(BaseAdmin):

    list_display = (
        'tg_id',
        'tg_username',
        'name',
        'surname',
        'last_name',
        'city',
        'email',
        'phone',
        'rating',
        'volunteer_hour',
        'point',
        'is_superuser',
        'is_staff',
        'photo',
        'avatar',
        'birthday',
        'is_adult',
        'interests',
        'consent_to_personal_data',
    )
    list_filter = (
        'city',
        'is_superuser',
        'is_staff',
        'is_adult',
        'consent_to_personal_data',
        'rating',
    )
    fieldsets = [
        (None, {"fields": [
            "tg_id",
            "tg_username",
            "last_name",
            "name",
            "surname",
            "birthday",
            "is_adult",
            "photo",  # TODO: add preview
            "volunteer_hour",
            "point",
            "email",
            "phone",
            "rating",
            "city",
            "interests",
        ]}),
        ("Уровень доступа", {"fields": ["is_staff", "is_superuser"]}),
    ]
    search_fields = ('tg_id', 'name', 'surname', 'last_name', 'city_id', 'email', 'phone')


@admin.register(Rating)
class RatingAdmin(BaseAdmin):

    list_display = ('level', 'hours_needed')
    ordering = ('hours_needed',)
    list_editable = ('hours_needed',)
