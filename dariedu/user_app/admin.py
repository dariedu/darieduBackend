from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)

from .google_export import export_to_gs
from user_app.models import User, Rating, Volunteer, Employee, Curator

from .export import CombineResource


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True
    actions = [export_to_gs]


@admin.register(User)
class UserAdmin(BaseAdmin, ExportActionMixin):
    resource_class = CombineResource
    actions = ['export']

    @admin.display(description='интересы')
    def short_interests(self, obj):
        if obj.interests:
            return obj.interests[:25] + '...' if len(obj.interests) > 25 else obj.interests
        return None

    @admin.display(description="день рождения")
    def birthday_format(self, obj):
        if obj.birthday:
            return obj.birthday.strftime('%d.%m.%Y')
        return None
    birthday_format.admin_order_field = 'birthday'

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
        'birthday_format',
        'is_adult',
        'short_interests',
        'metier',
        'consent_to_personal_data',
    )
    list_filter = (
        'city',
        'is_superuser',
        'is_staff',
        'is_adult',
        'consent_to_personal_data',
        'rating',
        'metier',
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
            "metier",
            "interests",
            "consent_to_personal_data",
        ]}),
        ("Уровень доступа", {"fields": ["is_staff", "is_superuser"]}),
    ]
    search_fields = ('tg_id', 'name', 'surname', 'last_name', 'email', 'phone')
    list_display_links = ('tg_id', 'tg_username', 'last_name', 'name', 'surname')


@admin.register(Volunteer)
class VolunteerAdmin(UserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False, is_superuser=False)


@admin.register(Curator)
class CuratorAdmin(UserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=True, is_superuser=False)


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_superuser=True)


@admin.register(Rating)
class RatingAdmin(BaseAdmin):

    list_display = ('level', 'hours_needed')
    ordering = ('hours_needed',)
    list_editable = ('hours_needed',)
