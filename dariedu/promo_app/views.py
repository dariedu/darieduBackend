from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .serializers import PromotionSerializer
from django.db import models
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Promotion, User
from django.core.exceptions import ValidationError



class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    filterset_fields = ['category', 'city', 'start_date', 'is_active']
    ordering_fields = ['start_date', 'price']

    @action(detail=True, methods=['post'], url_path='redeem')
    def redeem_promotion(self, request, pk):
        promotion = get_object_or_404(Promotion, pk=pk)
        user = request.user

        # Проверка достаточности баллов у волонтера
        if user.point < promotion.price:
            return Response({'error': 'Недостаточно баллов для приобретения'}, status=400)

        # Уменьшение количества баллов на стоимость поощрения
        user.point -= promotion.price
        user.save()

        serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})

        try:
            # Присвоение поощрения волонтеру
            return Response({status.HTTP_201_CREATED: serializer.data})
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'Internal Server Error'}, status=500)

    # Функция для отмены поощрения
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_redeem(self, request, pk):
        promotion = get_object_or_404(Promotion, pk=pk)
        user = request.user

        # Возврат баллов волонтеру
        user.point += promotion.price
        user.save()

        serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})

        try:
            # Отмена поощрения в БД
            return Response({status.HTTP_200_OK: 'Акция успешно отменена, баллы возвращены.'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'Internal Server Error'}, status=500)


class VolunteerPromotionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Только активные поощрения, которые доступны волонтерам
        now = timezone.now()
        promotions = Promotion.objects.filter(is_active=True, for_curators_only=False).filter(
            models.Q(is_permanent=True) | models.Q(end_date__gte=now)
        )
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)


class CuratorPromotionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Кураторы видят все активные поощрения
        now = timezone.now()
        promotions = Promotion.objects.filter(is_active=True).filter(
            models.Q(is_permanent=True) | models.Q(end_date__gte=now)
        )
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)






