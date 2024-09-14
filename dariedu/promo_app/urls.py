from django.urls import include, path
from rest_framework import routers
from . import views
from .views import VolunteerPromotionsView, CuratorPromotionsView

router = routers.DefaultRouter()
router.register(r'promotions', views.PromotionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/promotions/volunteer/', VolunteerPromotionsView.as_view(), name='volunteer-promotions'),
    path('api/promotions/curator/', CuratorPromotionsView.as_view(), name='curator-promotions'),
]