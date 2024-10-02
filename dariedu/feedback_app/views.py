from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from address_app.models import Address
from .models import Feedback, RequestMessage, PhotoReport
from .serializers import FeedbackSerializer, RequestMessageSerializer, PhotoReportSerializer


class FeedbackViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['type']


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
