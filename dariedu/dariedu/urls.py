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

from user_app.urls import router as user_approuter
from task_app.urls import router as task_approuter


router = routers.DefaultRouter()
router.registry.extend(user_approuter.registry)
router.registry.extend(task_approuter.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
