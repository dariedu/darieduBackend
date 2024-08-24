from django.shortcuts import render
from rest_framework import viewsets

from .models import User, Rating
from .serializers import UserSerializer, RatingSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ['is_superuser', 'is_staff', 'city', 'rating']


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


def FlatpageView(request):
    return render(request, 'defaults/default_api.html')
