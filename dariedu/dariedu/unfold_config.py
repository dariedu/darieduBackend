from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD_CONFIG = {
        "SITE_TITLE": 'Добро пожаловать',
        "SITE_HEADER": "заголовок для вкладки",
        "HIDE_SIDEBAR": False,
        # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
        "SITE_ICON": {
            "light": lambda request: static("icon-light.svg"),  # light mode
            "dark": lambda request: static("icon-dark.svg"),  # dark mode
        },
        # "SITE_LOGO": lambda request: static("logo.svg"),  # both modes, optimise for 32px height
        "SITE_LOGO": {
            "light": lambda request: static("logo-light.svg"),  # light mode
            "dark": lambda request: static("logo-dark.svg"),  # dark mode
        },
        "SITE_SYMBOL": "speed",  # symbol from icon set
        "SITE_FAVICONS": [
            {
                "rel": "icon",
                "sizes": "32x32",
                "type": "image/svg+xml",
                "href": lambda request: static("favicon.svg"),
            },
        ],
        "EXTENSIONS": {
                "modeltranslation": {
                    "flags": {
                        "en": "🇬🇧",
                        "ru": "🇷🇺",
                    },
                },
            },
        "SHOW_HISTORY": True,
        "SHOW_VIEW_ON_SITE": False,
        "COLORS": {
            "font": {
                "subtle-light": "107 114 128",
                "subtle-dark": "156 163 175",
                "default-light": "75 85 99",
                "default-dark": "209 213 219",
                "important-light": "17 24 39",
                "important-dark": "243 244 246",
            },
            "primary": {
                "50": "250 245 255",
                "100": "243 232 255",
                "200": "233 213 255",
                "300": "56 177 120",
                "400": "192 132 252",
                "500": "56 177 120",
                "600": "56 177 120",
                "700": "56 177 120",
                "800": "107 33 168",
                "900": "88 28 135",
                "950": "59 7 100",
            },
        },
        "SIDEBAR": {
            "show_search": False,
            "show_all_applications": True,
            "navigation": [
                {
                    # "title": _("Уведомления"),
                    "separator": True,
                    # "collapsible": True,
                    "items": [
                        {
                            "title": _("Уведомления"),
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:notifications_app_notification_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                    ],
                },
                {

                    "title": _("Доставки и добрые дела"),
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": _("Доставки"),
                            "icon": "local_shipping",
                            "link": reverse_lazy("admin:task_app_delivery_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Добрые дела"),
                            "icon": "task",
                            "link": reverse_lazy("admin:task_app_task_changelist"),
                        },
                        {
                            "title": _("Категории добрых дел"),
                            "icon": "task",
                            "link": reverse_lazy("admin:task_app_taskcategory_changelist"),
                        },
                    ],
                },
                {
                    "title": _("Адреса"),
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": _("Города"),
                            "icon": "location_city",
                            "link": reverse_lazy("admin:address_app_city_changelist"),
                            # "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Локации"),
                            "icon": "location_on",
                            "link": reverse_lazy("admin:address_app_location_changelist"),
                            # "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Маршрутные листы"),
                            "icon": "map",
                            "link": reverse_lazy("admin:address_app_routesheet_changelist"),
                            # "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Адреса"),
                            "icon": "dns",
                            "link": reverse_lazy("admin:address_app_address_changelist"),
                            # "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Благополучатели"),
                            "icon": "loyalty",
                            "link": reverse_lazy("admin:address_app_beneficiar_changelist"),
                            # "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                    ],
                },
                {
                    "title": _("Пользователи"),
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": _("Все пользователи"),
                            "icon": "manage_accounts",
                            "link": reverse_lazy("admin:user_app_user_changelist"),
                            # "badge": 'admin',
                            "permission": lambda request: request.user.is_superuser,
                        },
{
                            "title": _("Волонтёры"),
                            "icon": "manage_accounts",
                            "link": reverse_lazy("admin:user_app_volunteer_changelist"),
                            # "badge": 'admin',
                            "permission": lambda request: request.user.is_superuser,
                        },
{
                            "title": _("Кураторы"),
                            "icon": "manage_accounts",
                            "link": reverse_lazy("admin:user_app_curator_changelist"),
                            # "badge": 'admin',
                            "permission": lambda request: request.user.is_superuser,
                        },
{
                            "title": _("Сотрудники"),
                            "icon": "manage_accounts",
                            "link": reverse_lazy("admin:user_app_employee_changelist"),
                            # "badge": 'admin',
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Уровень"),
                            "icon": "trending_up",
                            "link": reverse_lazy("admin:user_app_rating_changelist"),
                            # "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },

                    ],
                },
                {
                    "title": _("Поощрения"),
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": _("Поощрения"),
                            "icon": "app_promo",
                            "link": reverse_lazy("admin:promo_app_promotion_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Категории"),
                            "icon": "category",
                            "link": reverse_lazy("admin:promo_app_promocategory_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        }
                    ],
                },
                {
                    # "title": _("Сторисы"),
                    "separator": True,
                    # "collapsible": True,
                    "items": [
                        {
                            "title": _("Сторисы"),
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:stories_app_stories_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                    ],
                },
                {
                    "title": _("Обратная связь"),
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": _("Фотоотчеты"),
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:feedback_app_photoreport_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Заявки на кураторство"),
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:feedback_app_requestmessage_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Обратная связь"),
                            "icon": "reviews",
                            "link": reverse_lazy("admin:feedback_app_feedback_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },

                    ],
                },
                {
                    "title": _("Статистика"),
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": _("Статистика volunteers"),  # TODO: Удалить перед слиянием в main
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:statistics_app_statistics_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Статистика за неделю"),
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:statistics_app_statisticsbyweek_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Статистика за месяц"),
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:statistics_app_statisticsbymonth_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Статистика за год"),
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:statistics_app_statisticsbyyear_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Статистика баллов и часов"),
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:statistics_app_allstatistics_changelist"),
                            # "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                    ]
                }
            ],
        },
    }


