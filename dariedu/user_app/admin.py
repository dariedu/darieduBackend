from django.contrib import admin

from .models import User, Rating


class UserAdmin(admin.ModelAdmin):
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

