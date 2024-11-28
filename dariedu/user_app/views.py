import os

from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Rating
from .serializers import UserSerializer, RatingSerializer, RegistrationSerializer, TelegramDataSerializer
from address_app.signals import get_phone_number
from google_drive import GoogleUser


User = get_user_model()


class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                data={'error': f'{e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        """Расширенный функционал метода create - добавление фотографии на google drive"""
        import re

        try:
            request = serializer.validated_data  # Данные из сериализатора, не путать с self.request

            phone: str = request.get('phone')
            if phone:
                request['phone'] = get_phone_number(phone)

            if len(request['phone']) > 15 or len(request['phone']) < 10:
                raise Exception('validation with phone')

            file_name = request.get('photo')
            full_name = request.get('last_name') + request.get('name') + request.get('surname')
            telegram_id = request.get('tg_id')

            regex = re.compile(r'\.\w*')
            prefix = regex.search(file_name.name).group()

            request['photo'].name = f'{full_name}_{telegram_id}{prefix}'
            data = serializer.save()

            drive_user = GoogleUser()
            view_link = drive_user.get_link_view(data.photo)
            data.photo_view = view_link
            data.save()
        except Exception as e:
            raise Exception(f'{e}')


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
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_superuser', 'is_staff', 'city', 'rating']
    ordering_fields = ['id']

    def perform_update(self, serializer: UserSerializer):
        serializer.validated_data.pop('last_name', None)
        serializer.validated_data.pop('name', None)
        serializer.validated_data.pop('surname', None)
        serializer.validated_data.pop('phone', None)
        serializer.validated_data.pop('birthday', None)
        serializer.validated_data.pop('tg_username', None)

        gdrive = GoogleUser()
        val_photo = serializer.validated_data.get('photo')

        if not val_photo:
            serializer.save()
            return

        instance_photo = serializer.instance.photo
        file_id = serializer.instance.photo_view.split('/')[-2]
        photo_name = instance_photo.name.split(os.sep)[-1]
        instance_photo.delete()

        val_photo.name = photo_name
        serializer.validated_data['photo'] = val_photo

        data = serializer.save()

        gdrive.update_file(file_id=file_id, file=data.photo)

    def get_queryset(self):
        queryset = User.objects.all()
        tg_id = self.request.query_params.get('tg_id', None)
        if tg_id is not None:
            queryset = queryset.filter(tg_id=tg_id)
        return queryset


class RatingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RatingSerializer


def FlatpageView(request):
    return render(request, 'defaults/default_api.html')
