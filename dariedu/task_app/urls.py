from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'tasks', views.TaskViewSet)
router.register(r'deliveries', views.DeliveryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    ]