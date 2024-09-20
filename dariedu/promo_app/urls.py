from django.urls import include, path
from rest_framework import routers
from . import views
# from .views import VolunteerPromotionsViewSet, CuratorPromotionsViewSet

router = routers.DefaultRouter()
router.register(r'promotions', views.PromotionViewSet)
# router.register(r'promo-volunteer', views.VolunteerPromotionsViewSet, basename='volunteer-promotions')
# router.register(r'promo-curator', views.CuratorPromotionsViewSet, basename='curator-promotions')


urlpatterns = [
    path('', include(router.urls)),
    # path('api/promotions/volunteer/', VolunteerPromotionsViewSet.as_view(), name='volunteer-promotions'),
    # path('api/promotions/curator/', CuratorPromotionsViewSet.as_view(), name='curator-promotions'),
]