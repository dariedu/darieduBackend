from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
# router.register(r'addresses', views.AddressViewSet)
router.register(r'cities', views.CityViewSet)
# router.register(r'beneficiaries', views.BeneficiarViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'route_sheets', views.RouteSheetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    ]