from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.views import APIView

from .serializers import PromotionSerializer, PromoCategorySerializer, ParticipationSerializer
from django.db import models
from rest_framework.decorators import action, api_view
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Promotion, User, Participation, PromoCategory
from django.core.exceptions import ValidationError


class PromotionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Curators can see all available promotions, users can see only his"""
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    filterset_fields = ['category', 'city', 'start_date', 'is_active']
    ordering_fields = ['start_date', 'price']

    def get_queryset(self):
        """Curator can see all active promotions, user can see only his"""
        if self.action == 'list':
            now = timezone.now()
            if self.request.user.is_staff:
                return Promotion.objects.filter(is_active=True).filter(
                    models.Q(is_permanent=True) | models.Q(end_date__gte=now))
            else:
                return Promotion.objects.filter(is_active=True, for_curators_only=False).filter(
                    models.Q(is_permanent=True) | models.Q(end_date__gte=now))

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

        # Проверка достаточности баллов у волонтёра
        if user.point < promotion.price:
            return Response({'error': 'Недостаточно баллов для приобретения'}, status=400)

        # Уменьшение количества баллов на стоимость поощрения
        user.point -= promotion.price
        user.save()

        serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})

        # Присвоение поощрения волонтёру через создание записи в Participation
        try:
            Participation.objects.create(user=user, promotion=promotion)

            # Обновляем serializer для возврата актуальной информации
            serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

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

        # Возврат баллов волонтёру
        user.point += promotion.price
        user.save()

        # Удаляем запись о получении поощрения
        participation.delete()

        # Обновляем serializer для возврата актуальной информации
        serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})

        try:
            return Response({'message': 'Поощрение успешно отменено, баллы возвращены.'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'Internal Server Error'}, status=500)

    @action(detail=False, methods=['get'], url_path='promo_categories')
    def get_categories(self, request):
        """
        Вывод категорий поощрений
        """
        categories = PromoCategory.objects.all()
        serializer = PromoCategorySerializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my_promo')
    def get_my_promotions(self, request):
        """
        Вывод взятых активных поощрений
        """
        user = request.user
        participations = Participation.objects.filter(user=user)
        promotions = [participation.promotion for participation in participations]

        serializer = self.get_serializer(promotions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ParticipationView(APIView):
    """
    Подтверждение участия в поощрении
    """
    def post(self, request):
        promotion_id = request.data.get('promotion_id')
        tg_id = request.data.get('tg_id')
        participation = Participation.objects.filter(promotion_id=promotion_id, user__tg_id=tg_id).first()
        if participation:
            participation.is_active = True
            participation.save_without_reward_check()
            return Response({'message': 'Участие обновлено'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Участие не найдено'}, status=status.HTTP_404_NOT_FOUND)
