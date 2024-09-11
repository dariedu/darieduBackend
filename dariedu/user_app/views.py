from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Rating
from .serializers import UserSerializer, RatingSerializer, RegistrationSerializer, LoginSerializer


class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        tg_id = request.data.get('tg_id')
        password = request.data.get('password')
        user = authenticate(tg_id=tg_id, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'tg_id': tg_id
            })
        else:
            return Response({"error": "Invalid credentials"}, status=401)

class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    filterset_fields = ['is_superuser', 'is_staff', 'city', 'rating']


class RatingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    serializer_class = RatingSerializer


def FlatpageView(request):
    return render(request, 'defaults/default_api.html')
