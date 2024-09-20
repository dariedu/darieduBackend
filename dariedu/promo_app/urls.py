from django.urls import include, path
from rest_framework import routers
from . import views
# from .views import VolunteerPromotionsViewSet, CuratorPromotionsViewSet

router = routers.DefaultRouter()
router.register(r'promotions', views.PromotionViewSet)
# router.register(r'promo_categories', views.PromoCategoryViewSet)


urlpatterns = [
    path('', include(router.urls)),
]