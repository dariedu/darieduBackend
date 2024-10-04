from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from address_app.models import Address
from .models import Feedback, RequestMessage, PhotoReport
from .serializers import FeedbackSerializer, RequestMessageSerializer, PhotoReportSerializer


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

        **Параметры:**
        - `type`: Строка, тип отзыва (delivery или promotion)
        - `text`: Текст отзыва
        - `delivery`: ID доставки (если применимо)
        - `promotion`: ID поощрения (если применимо)

        **Ответ:**
        - 201: Если отзыв успешно создан.
        - 400: Если данные невалидные.
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

        **Параметры:**
        - `pk`: ID отзыва

        **Ответ:**
        - 200: Если отзыв успешно удален.
        - 403: Если пользователь не может удалить этот отзыв.
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

        **Ответ:**
        - Общее количество отзывов для администратора или количество отзывов текущего пользователя.
        """
        if self.request.user.is_staff:
            total_feedback = Feedback.objects.count()
        else:
            total_feedback = Feedback.objects.filter(user=self.request.user).count()

        return Response({"total_feedback": total_feedback})


class RequestMessageViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = RequestMessage.objects.all()
    serializer_class = RequestMessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['type']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PhotoReportViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """API to manage photo reports"""
    queryset = PhotoReport.objects.all()
    serializer_class = PhotoReportSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create new photo report"""
        address_id = request.data.get('address')

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return Response({'detail': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)

        photo_report = PhotoReport.objects.create(
            user=request.user,
            address=address,
            # photo=request.data.get('photo'),  # TODO add URL from cloud storage
            comment=request.data.get('comment')
        )

        photo_report.save()
        return Response(status=status.HTTP_201_CREATED)
