from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .serializers import PromotionSerializer, PromoCategorySerializer, FeedbackSerializer
from django.db import models
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Promotion, User, Participation, PromoCategory, Feedback
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from .forms import FeedbackForm


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

        # Возврат баллов волонтеру
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


# class PromoCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     queryset = PromoCategory.objects.all()
#     serializer_class = PromoCategorySerializer
#     permission_classes = [IsAuthenticated]


class FeedbackViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Пользователи могут создавать отзывы и просматривать только свои, администраторы могут просматривать все.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        """Пользователи видят только свои отзывы, администраторы - все"""
        if self.request.user.is_staff:
            return Feedback.objects.all()
        return Feedback.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='submit')
    def submit_feedback(self, request):
        """
        Отправка отзыва
        """
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Присваиваем отзыв пользователю
            return Response({"message": "Спасибо за ваш отзыв!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='cancel')
    def cancel_feedback(self, request, pk):
        """
        Отмена отправленного отзыва
        """
        feedback = get_object_or_404(Feedback, pk=pk, user=request.user)

        if feedback:
            feedback.delete()
            return Response({"message": "Отзыв успешно удален."}, status=status.HTTP_200_OK)
        return Response({'error': 'Вы не можете удалить этот отзыв'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'], url_path='feedback_stats')
    def feedback_stats(self, request):
        """
        Получение статистики по отзывам (например, количество отзывов)
        """
        if self.request.user.is_staff:
            total_feedback = Feedback.objects.count()
        else:
            total_feedback = Feedback.objects.filter(user=self.request.user).count()

        return Response({"total_feedback": total_feedback})
