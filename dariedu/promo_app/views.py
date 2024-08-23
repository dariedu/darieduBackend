from django.shortcuts import render
from rest_framework import viewsets

from .models import Promotion
from .serializers import PromotionSerializer


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    filter_fields = ['category', 'city', 'date', 'is_active']
    ordering_fields = ['date', 'price']
