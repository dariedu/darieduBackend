from django.shortcuts import render
from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Rating
from .serializers import UserSerializer, RatingSerializer, RegistrationSerializer, TelegramDataSerializer
from .google_drive.upload_file import get_link_view


class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def perform_create(self, serializer):
        """Расширенный функционал метода create - добавление фотографии на google drive"""
        import re

        request = serializer.validated_data  # Данные из сериализатора, не путать с self.request
        file_name = request['photo']
        full_name = request['last_name'] + request['name'] + request['surname']
        telegram_id = request['tg_id']

        regex = re.compile(r'\.\w*')
        prefix = regex.search(file_name.name).group()

        request['photo'].name = f'{full_name}_{telegram_id}{prefix}'
        data = serializer.save()

        view_link = get_link_view(data.photo)
        data.photo_view = view_link
        data.save()


class CustomTokenObtainPairView(APIView):
    serializer_class = TelegramDataSerializer

    def post(self, request):
        tg_id = request.data.get('tg_id')

        if not tg_id:
            return Response({'error': 'tg_id is required'}, status=400)

        user = User.objects.filter(tg_id=tg_id).first()

        if not user:
            return Response({'error': 'User not found'}, status=404)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

      
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
