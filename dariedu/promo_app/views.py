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
from .models import Promotion, User, Participation
from django.core.exceptions import ValidationError

class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    filterset_fields = ['category', 'city', 'start_date', 'is_active']
    ordering_fields = ['start_date', 'price']

    @action(detail=True, methods=['post'], url_path='redeem')
    def redeem_promotion(self, request, pk):
        """
        Приобретение поощрения
        """
        promotion = get_object_or_404(Promotion, pk=pk)
        user = request.user

        # Проверка доступности поощрения
        if promotion.available_quantity <= 0:
            return Response({'error': 'Это поощрение недоступно'}, status=400)

        # Проверка достаточности баллов у волонтера
        if user.point < promotion.price:
            return Response({'error': 'Недостаточно баллов для приобретения'}, status=400)

        # Уменьшение количества баллов на стоимость поощрения
        user.point -= promotion.price
        user.save()

        serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})

        # Присвоение поощрения волонтеру через создание записи в Participation
        try:
            Participation.objects.create(user=user, promotion=promotion)

            # Обновляем serializer для возврата актуальной информации
            serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'Internal Server Error'}, status=500)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_redeem(self, request, pk):
        """
        Отмена поощрения
        """
        promotion = get_object_or_404(Promotion, pk=pk)
        user = request.user

        # Найти запись Participation, если она существует
        participation = Participation.objects.filter(user=user, promotion=promotion).first()
        if not participation:
            return Response({'error': 'У вас нет этого поощрения'}, status=400)

        # Возврат баллов волонтеру
        user.point += promotion.price
        user.save()

        # Удаление записи о получении поощрения
        participation.delete()

        # Обновление serializer для возврата актуальной информации
        serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})

        try:
            return Response({'message': 'Поощрение успешно отменено, баллы возвращены.'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'Internal Server Error'}, status=500)

    @action(detail=True, methods=['get'], url_path='volunteers-count')
    def retrieve_volunteers_count(self, request, pk=None):
        """
        Показ числа участников поощрений
        """
        promotion = get_object_or_404(Promotion, pk=pk)
        data = {
            'promotion': PromotionSerializer(promotion).data,
            'volunteers_count': promotion.volunteers_count()  # Получаем количество волонтеров
        }
        return Response(data)


class VolunteerPromotionsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='available_volunteer')
    def get_volunteer_promotions(self, request):
        """
        Показ доступных поощрений для волонтера
        """
        now = timezone.now()
        promotions = Promotion.objects.filter(is_active=True, for_curators_only=False).filter(
            models.Q(is_permanent=True) | models.Q(end_date__gte=now)
        )
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)


class CuratorPromotionsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='available_curator')
    def get_curator_promotions(self, request):
        """
        Кураторы видят все активные поощрения
        """
        now = timezone.now()
        promotions = Promotion.objects.filter(is_active=True).filter(
            models.Q(is_permanent=True) | models.Q(end_date__gte=now)
        )
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)