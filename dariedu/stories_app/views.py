from django.shortcuts import render
from django.views.generic import DetailView
from rest_framework import mixins, viewsets

from stories_app.models import Stories
from stories_app.serializers import StoriesSerializer


class StoriesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Stories.objects.filter(hidden=False)
    serializer_class = StoriesSerializer
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    filterset_fields = ['hidden']


class StoriesDetailView(DetailView):
    # TODO: image does not work, correct path after deployment
    model = Stories
    template_name = 'stories/stories.html'
    context_object_name = 'stories'
    slug_field = 'link_name'
