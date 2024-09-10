from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Promotion
from .serializers import PromotionSerializer
from django.db import models


class VolunteerPromotionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Только активные поощрения, которые доступны волонтерам
        now = timezone.now()
        promotions = Promotion.objects.filter(is_active=True, for_curators_only=False).filter(
            models.Q(is_permanent=True) | models.Q(expiry_date__gte=now)
        )
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)


class CuratorPromotionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Кураторы видят все активные поощрения
        now = timezone.now()
        promotions = Promotion.objects.filter(is_active=True).filter(
            models.Q(is_permanent=True) | models.Q(expiry_date__gte=now)
        )
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)






# from django.shortcuts import render
# from rest_framework import viewsets
# from .models import Promotion
# from .serializers import PromotionSerializer
#
#
# class PromotionViewSet(viewsets.ModelViewSet):
#     queryset = Promotion.objects.all()
#     serializer_class = PromotionSerializer
#     filterset_fields = ['category', 'city', 'date', 'is_active']
#     ordering_fields = ['date', 'price']
