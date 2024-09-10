from django.shortcuts import render
from rest_framework import mixins, viewsets

from stories_app.models import Stories
from stories_app.serializers import StoriesSerializer


class StoriesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Stories.objects.all()
    serializer_class = StoriesSerializer
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    filterset_fields = ['hidden']
