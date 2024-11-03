from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets, mixins

from .serializers import NotificationSerializer


class CreateNotificationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save()
            return Response({'message': 'Уведомление создано успешно', 'notification_id': notification.id},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
