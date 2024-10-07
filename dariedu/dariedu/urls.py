"""
URL configuration for dariedu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from stories_app.views import StoriesDetailView
from user_app.urls import router as user_approuter
from task_app.urls import router as task_approuter
from promo_app.urls import router as promo_approuter
from feedback_app.urls import router as feedback_approuter
from address_app.urls import router as address_approuter
from stories_app.urls import router as stories_approuter
from user_app.views import RegistrationView, CustomTokenObtainPairView
from notifications_app.views import CreateNotificationView

router = routers.DefaultRouter()
router.registry.extend(user_approuter.registry)
router.registry.extend(task_approuter.registry)
router.registry.extend(promo_approuter.registry)
router.registry.extend(feedback_approuter.registry)
router.registry.extend(address_approuter.registry)
router.registry.extend(stories_approuter.registry)

urlpatterns = [
    path('api/notifications/', CreateNotificationView.as_view()),
    # path('api/', include('notifications_app.urls')),
    path('stories/<slug:slug>/', StoriesDetailView.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/registration/', RegistrationView.as_view()),

    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
