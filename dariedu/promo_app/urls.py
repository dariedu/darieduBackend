from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'promotions', views.PromotionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    ]