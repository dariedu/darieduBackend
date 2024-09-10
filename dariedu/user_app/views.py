from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from .models import User, Rating
from .serializers import UserSerializer, RatingSerializer


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    filterset_fields = ['is_superuser', 'is_staff', 'city', 'rating']


class RatingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    serializer_class = RatingSerializer


def FlatpageView(request):
    return render(request, 'defaults/default_api.html')
