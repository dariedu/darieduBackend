from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'feedbacks', views.FeedbackViewSet)
router.register(r'request_messages', views.RequestMessageViewSet)
router.register(r'photo_reports', views.PhotoReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    ]