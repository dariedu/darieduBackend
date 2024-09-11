from django.shortcuts import render
from rest_framework import viewsets, mixins

from .models import Feedback, RequestMessage
from .serializers import FeedbackSerializer, RequestMessageSerializer


class FeedbackViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    filterset_fields = ['type']


class RequestMessageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = RequestMessage.objects.all()
    serializer_class = RequestMessageSerializer
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    filterset_fields = ['type']
