import datetime
import zoneinfo
from typing import Optional

from django.contrib import admin
from django.conf import settings
from django.db.models import ForeignKey
from django.forms import ModelChoiceField
from django.http import HttpRequest

from import_export.admin import ExportActionMixin, ImportExportModelAdmin

from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm
from unfold.decorators import action

from .export_prom import CombineResourcePromo
from .models import Promotion, PromoCategory, User

ZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm  # ExportForm
    compressed_fields = True  # Default: False
    list_select_related = True  # Default: False
    list_filter_submit = True
    list_fullwidth = True


class UsersInline(admin.TabularInline):
    model = Promotion.users.through
    extra = 0
    list_display = ('user', )
    fields = ('user', )
    readonly_fields = ('user', )
    can_delete = False
    verbose_name = 'участник'
    verbose_name_plural = 'участники'


@admin.register(Promotion)
class PromotionAdmin(BaseAdmin, ExportActionMixin):
    resource_class = CombineResourcePromo
    actions = ['export']

    @admin.display(description="описание поощрения")
    def description_short(self, obj):
        if obj.description:
            return obj.description[:45] + '...' if len(obj.description) > 45 else obj.description
        return None

    @admin.display(description="дата начала")
    def start_date_format(self, obj):
        return obj.start_date.astimezone(ZONE).strftime("%d.%m.%y %H:%M")
    start_date_format.admin_order_field = 'start_date'

    @admin.display(description="дата окончания")
    def end_date_format(self, obj):
        if obj.end_date:
            return obj.end_date.astimezone(ZONE).strftime("%d.%m.%y %H:%M")
        return None
    end_date_format.admin_order_field = 'end_date'

    list_display = (
        'name',
        'category',
        'address',
        'price',
        'is_active',
        'start_date_format',
        'is_permanent',
        'end_date_format',
        'available_quantity',
        'quantity',
        'for_curators_only',
        'description_short',
        'city',
        'display_volunteers',
        'contact_person',
    )
    fields = (
        'name',
        'category',
        'address',
        'price',
        'is_active',
        'start_date',
        'is_permanent',
        'end_date',
        'available_quantity',
        'quantity',
        'for_curators_only',
        'description',
        'city',
        'ticket_file',
        'about_tickets',
        'picture',
        'contact_person',
    )
    inlines = [UsersInline, ]
    list_filter = ('is_active', 'city', 'category', 'for_curators_only', 'available_quantity', 'start_date')
    search_fields = ('name', 'start_date', 'description')
    ordering = ('-start_date',)
    list_editable = ('price', 'is_active', 'quantity', 'for_curators_only')
    list_display_links = ('name', 'category')

    @action(description="Копировать")
    def copy(self, request, queryset, *args):
        """Copy creates for next week, not active"""
        for obj in queryset:
            new_obj = Promotion.objects.create(
                name=obj.name + '_copy',
                category=obj.category,
                address=obj.address,
                price=obj.price,
                is_active=False,
                start_date=obj.start_date + datetime.timedelta(days=7),
                is_permanent=obj.is_permanent,
                end_date=obj.end_date + datetime.timedelta(days=7) if obj.end_date else None,
                available_quantity=obj.quantity,
                quantity=obj.quantity,
                for_curators_only=obj.for_curators_only,
                description=obj.description,
                city=obj.city,
                about_tickets=obj.about_tickets,
                contact_person=obj.contact_person
            )

            if obj.ticket_file:
                new_obj.ticket_file.save(
                    obj.ticket_file.name,
                    obj.ticket_file,
                    save=True
                )

            if obj.picture:
                new_obj.picture.save(
                    obj.picture.name,
                    obj.picture,
                    save=True
                )
            new_obj.save()

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions['copy'] = (
            self.copy.__func__,
            'copy',
            'Копировать'
        )
        return actions

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs
    ) -> Optional[ModelChoiceField]:
        if db_field.name == 'contact_person':
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PromoCategory)
class PromoCategoryAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)
