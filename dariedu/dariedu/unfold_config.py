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
        "SIDEBAR": {
            "show_search": True,
            "show_all_applications": True,
            "navigation": [
                {
                    "title": _("Пользователи"),
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": _("Пользователи"),
                            "icon": "manage_accounts",
                            "link": reverse_lazy("admin:user_app_user_changelist"),
                            "badge": 'admin',
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Рейтинг"),
                            "icon": "trending_up",
                            "link": reverse_lazy("admin:user_app_rating_changelist"),
                            "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },

                    ],
                },
                {
                    "title": _("Адреса"),
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": _("Город"),
                            "icon": "location_city",
                            "link": reverse_lazy("admin:address_app_city_changelist"),
                            "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Локация"),
                            "icon": "location_on",
                            "link": reverse_lazy("admin:address_app_location_changelist"),
                            "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Маршрутная карта"),
                            "icon": "map",
                            "link": reverse_lazy("admin:address_app_routesheet_changelist"),
                            "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Адрес"),
                            "icon": "dns",
                            "link": reverse_lazy("admin:address_app_address_changelist"),
                            "badge": "admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Бенефициар"),
                            "icon": "loyalty",
                            "link": reverse_lazy("admin:address_app_beneficiar_changelist"),
                            "badge": "admin",
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
                            "title": _("Запросы"),
                            "icon": "request_quote",
                            "link": reverse_lazy("admin:feedback_app_requestmessage_changelist"),
                            "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Отзывы"),
                            "icon": "reviews",
                            "link": reverse_lazy("admin:feedback_app_feedback_changelist"),
                            "badge": "main admin",
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
                            "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                    ],
                },
                {
                    "title": _("Задания"),
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": _("Доставка"),
                            "icon": "local_shipping",
                            "link": reverse_lazy("admin:task_app_delivery_changelist"),
                            "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },
                        {
                            "title": _("Задания"),
                            "icon": "task",
                            "link": reverse_lazy("admin:task_app_task_changelist"),
                            "badge": "main admin",
                            "permission": lambda request: request.user.is_superuser,
                        },

                    ],
                },
            ],
        },
    }


