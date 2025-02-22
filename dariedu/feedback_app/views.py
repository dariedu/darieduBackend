import os
from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from address_app.models import Address, Beneficiar, RouteSheet
from task_app.models import Delivery
from .models import Feedback, RequestMessage, PhotoReport
from .serializers import FeedbackSerializer, RequestMessageSerializer, PhotoReportSerializer

from google_drive import GoogleFeedback


class FeedbackViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Пользователи могут создавать отзывы и просматривать только свои, администраторы могут просматривать все.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        """Пользователи видят только свои отзывы, администраторы - все"""
        if self.action == 'list':
            if self.request.user.is_staff:
                return self.queryset.filter(created_at__gte=(timezone.now() - timezone.timedelta(days=14)))
            return self.queryset.filter(user=self.request.user,
                                        created_at__gte=(timezone.now() - timezone.timedelta(days=14)))

        return self.queryset.filter(created_at__gte=(timezone.now() - timezone.timedelta(days=14)))

    @action(detail=False, methods=['post'], url_path='submit', name='submit_feedback')
    def submit_feedback(self, request):
        """
        Отправка отзыва

        **Параметры:**
        - `type`: Строка, тип отзыва (delivery или promotion)
        - `text`: Текст отзыва
        - `delivery`: ID доставки (если применимо)
        - `task`: ID доброго дела (если применимо)
        - `promotion`: ID поощрения (если применимо)

        **Ответ:**
        - 201: Если отзыв успешно создан.
        - 400: Если данные невалидные.
        """

        data = request.data
        serializer = FeedbackSerializer(data=data)
        if serializer.is_valid():
            if data['type'] == 'completed_task_curator' or data['type'] == 'completed_delivery_curator':
                if not self.request.user.is_staff:
                    return Response({"error": "Только куратор может оставлять данный тип отзывов."}, status=400)
            # Проверка, что обратная связь может быть только о доставке или поощрении, но не о двух одновременно
            if (data['type'] == 'canceled_delivery' or
                data['type'] == 'completed_delivery' or
                data['type'] == 'completed_delivery_curator') and not data['delivery']:
                return Response(
                    {"error": "Для обратной связи о доставке необходимо указать доставку."}, status=400)
            elif ((data['type'] == 'canceled_promotion' or data['type'] == 'completed_promotion')
                  and not data['promotion']):
                return Response(
                    {"error": "Для обратной связи о поощрении необходимо указать поощрение."}, status=400)
            elif (data['type'] == 'canceled_task' or
                  data['type'] == 'completed_task' or
                  data['type'] == 'completed_task_curator') and not data['task']:
                return Response(
                    {"error": "Для обратной связи о добром деле необходимо указать доброе дело."}, status=400)
            elif ((data['type'] == 'suggestion' or data['type'] == 'support') and
                (data['delivery'] or data['promotion'] or data['task'])):
                return Response(
                    {"error":
                         "Для предложений или поддержки не требуется указывать доставку, поощрение или доброе дело."},
                    status=400)
            if (data['delivery'] and data['promotion']
                    or data['delivery'] and data['task']
                    or data['promotion'] and data['task']):
                return Response(
                    {"error": "Отзыв может быть связан не более чем с одной моделью: либо доставка, либо поощрение."},
                    status=400
                )
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
    queryset = PhotoReport.objects.filter(date_gte=datetime.now() - timedelta(days=14))
    serializer_class = PhotoReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['route_sheet_id', 'delivery_id']

    def create(self, request, *args, **kwargs):
        """
        Создание записи в базе данных и обработка данных
        На выход получаем следующие поля:
        address: ID адреса
        user: Авторизованный пользователь
        photo: Фотография прикрепляемого к отчёту
        comment: Комментарий
        На выходе status code:
        404 - если адрес не найден в БД
        400 - что-то случилось с фотографией, начиная от приёма и обработки фотографии, заканчивая загрузкой в google
        201 - если данные сохранены в бд
        """
        address_id = request.data.get('address')
        route_sheet_id = request.data.get('route_sheet_id')
        delivery_id = request.data.get('delivery_id')

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return Response({'detail': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            route_sheet = RouteSheet.objects.get(id=route_sheet_id)
        except RouteSheet.DoesNotExist:
            return Response({'detail': 'Route sheet not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            delivery = Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            return Response({'detail': 'Delivery not found.'}, status=status.HTTP_404_NOT_FOUND)

        if route_sheet.id not in delivery.route_sheet.all().values_list('id', flat=True):
            return Response({'detail': 'Route sheet not found in delivery.'}, status=status.HTTP_404_NOT_FOUND)

        beneficiary = Beneficiar.objects.filter(address_id=address_id).values_list('full_name')

        try:
            file = self.save_image_to_server(beneficiary)
            google_feedback = GoogleFeedback()
            links = google_feedback.feedback_links(file)
            self.delete_file(file)
        except Exception as e:
            return Response(data={'detail': f'Google drive or image - {e}'},
                            status=status.HTTP_400_BAD_REQUEST)

        photo_report = PhotoReport.objects.create(
            user=request.user,
            address=address,
            photo_view=links.get('view'),
            photo_download=links.get('download'),
            comment=request.data.get('comment'),
            route_sheet_id=route_sheet,
            delivery_id=delivery,
            is_absent=request.data.get('is_absent')
        )

        photo_report.save()
        return Response(status=status.HTTP_201_CREATED)

    def save_image_to_server(self, beneficiary):
        """Сохранение фотографии на сервере"""
        import re

        file = self.request.FILES['photo']

        regex = re.compile(r'\.\w*')
        prefix = regex.search(file.name).group()

        list_beneficiary = lambda x: [i[0] for i in x]

        file.name = ' и '.join(list_beneficiary(beneficiary)) + prefix

        with open(f'photo_report/{file.name}', 'wb+') as photo:
            for chunk in file.chunks():
                photo.write(chunk)

        return file

    @staticmethod
    def delete_file(file):
        """Удаление фотографии из сервера"""
        os.remove(f'photo_report/{file}')
