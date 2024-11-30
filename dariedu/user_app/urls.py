from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'ratings', views.RatingViewSet)
router.register(r'current_user', views.CurrentUserViewSet, basename='current_user')

urlpatterns = [
    path('', include(router.urls)),
    path('api/', views.FlatpageView, name='FlatpageView'),
]
