from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
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
from .models import Promotion, Participation, PromoCategory
from django.core.exceptions import ValidationError


class PromotionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Curators can see all available promotions, users can see only his"""
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    filterset_fields = ['category', 'city', 'is_active']
    ordering_fields = ['start_date', 'price']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Curator can see all active promotions, user can see only his"""
        if self.action == 'list':
            now = timezone.now()
            user = self.request.user
            participations = Participation.objects.filter(user=user)
            promotions = [participation.promotion.pk for participation in participations]
            if user.is_staff:
                return Promotion.objects.filter(is_active=True).filter(
                    models.Q(is_permanent=True) | models.Q(end_date__gte=now)).exclude(pk__in=promotions)
            else:
                return Promotion.objects.filter(is_active=True, for_curators_only=False).filter(
                    models.Q(is_permanent=True) | models.Q(end_date__gte=now)).exclude(pk__in=promotions)

        if self.action == 'get_my_promotions':
            user = self.request.user
            participations = Participation.objects.filter(user=user)
            promotions = [participation.promotion.pk for participation in participations]
            queryset = Promotion.objects.filter(pk__in=promotions)

            after = self.request.query_params.get('after', None)
            before = self.request.query_params.get('before', None)
            is_active = self.request.query_params.get('is_active', None)
            if after:
                try:
                    after = timezone.datetime.strptime(after, '%Y-%m-%d')
                    queryset = queryset.filter(models.Q(is_permanent=True) | models.Q(end_date__date__gte=after))
                except ValueError:
                    pass
            if before:
                try:
                    before = timezone.datetime.strptime(before, '%Y-%m-%d')
                    queryset = queryset.filter(start_date__date__lte=before)
                except ValueError:
                    pass
            if is_active:
                if is_active == 'true':
                    queryset = queryset.filter(is_active=True)
                elif is_active == 'false':
                    queryset = queryset.filter(is_active=False)
            return queryset

    @action(detail=True, methods=['post'], url_path='redeem')
    def redeem_promotion(self, request, pk):
        """
        Приобретение поощрения
        """
        promotion = get_object_or_404(Promotion, pk=pk)
        user = request.user

        if promotion.available_quantity <= 0:
            return Response({'error': 'Это поощрение недоступно'}, status=400)
        if user.point < promotion.price:
            return Response({'error': 'Недостаточно баллов для приобретения'}, status=400)
        if Participation.objects.filter(user=user, promotion=promotion).exists():
            return Response({'error': 'Вы уже приобрели этот поощрение'}, status=400)

        user.point -= promotion.price
        user.save(update_fields=['point'])

        serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})

        try:
            Participation.objects.create(user=user, promotion=promotion)

            serializer = PromotionSerializer(instance=promotion, context={'view': self, 'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @extend_schema(
        tags=['promo_confirm/cancel'],
        summary="Отмена поощрения",
        request=OpenApiTypes.NONE,
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_redeem(self, request, pk):
        """
        Отмена поощрения
        """
        promotion = get_object_or_404(Promotion, pk=pk)
        user = request.user

        participation = Participation.objects.filter(user=user, promotion=promotion).first()
        if not participation:
            return Response({'error': 'У вас нет этого поощрения'}, status=400)

        user.point += promotion.price
        user.save(update_fields=['point'])
        participation.delete()

        try:
            return Response({'message': 'Поощрение успешно отменено, баллы возвращены.'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'Internal Server Error'}, status=500)

    @extend_schema(
        tags=['promo_confirm/cancel'],
        summary="Подтверждение участия в поощрении",
        request=OpenApiTypes.NONE
    )
    @action(detail=True, methods=['post'], url_path='confirmed')
    def confirmed(self, request, pk):
        """
        Подтверждение участия в поощрении
        """
        try:
            promotion = get_object_or_404(Promotion, pk=pk)
            user = request.user
            participation = Participation.objects.filter(user=user, promotion=promotion).first()

            if not participation:
                return Response({'error': 'У вас нет этого поощрения'}, status=400)

            if participation.is_active:
                return Response({'error': 'Участие уже подтверждено'}, status=status.HTTP_400_BAD_REQUEST)

            participation.is_active = True
            participation.save_without_reward_check()

            return Response({'message': 'Участие подтверждено'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

        except Exception as e:
            return Response({'error': 'Internal Server Error'}, status=500)

    @extend_schema(
        tags=['promo_confirm/cancel'],
        summary="Получение не подтвержденных поощрений",
        request=OpenApiTypes.NONE
    )
    @action(detail=False, methods=['get'], url_path='not_confirmed')
    def get_not_confirmed(self, request):
        """
        Получение не подтвержденных поощрений
        """
        try:
            user = request.user
            participation = Participation.objects.filter(user=user, is_active=False, promotion__is_active=True).all()

            serializer = ParticipationSerializer(participation, many=True)

            return Response(serializer.data)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @extend_schema(
        tags=['promo_confirm/cancel'],
        summary="Получение подтвержденных поощрений",
        request=OpenApiTypes.NONE
    )
    @action(detail=False, methods=['get'], url_path='confirmed')
    def get_confirmed(self, request):
        """
        Получение подтвержденных поощрений
        """
        try:
            user = request.user
            participation = Participation.objects.filter(user=user, is_active=True, promotion__is_active=True).all()

            serializer = ParticipationSerializer(participation, many=True)

            return Response(serializer.data)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

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
        Вывод взятых поощрений
        фильтры:
        after - начало периода
        before - конец периода
        is_active - активные поощрения
        Календарь поощрений, взятых пользователем
        Пример: api/promotions/my_promo/?after=2024-10-05&before=2024-10-20
        Формат даты: YYYY-MM-DD
        можно использовать вместе или по отдельности
        """
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#
# class ParticipationView(APIView):
#     """
#     Подтверждение участия в поощрении
#     """
#     def post(self, request):
#         promotion_id = request.data.get('promotion_id')
#         tg_id = request.data.get('tg_id')
#         participation = Participation.objects.filter(promotion_id=promotion_id, user__tg_id=tg_id).first()
#         if participation:
#             participation.is_active = True
#             participation.save_without_reward_check()
#             return Response({'message': 'Участие обновлено'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'error': 'Участие не найдено'}, status=status.HTTP_404_NOT_FOUND)
