import os

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework import serializers

from .models import Rating
from .serializers import UserSerializer, RatingSerializer, RegistrationSerializer, TelegramDataSerializer, \
    PhoneUpdateSerializer
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

      
class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_superuser', 'is_staff', 'city', 'rating']
    ordering_fields = ['id']

    def perform_update(self, serializer: UserSerializer):
        import re
        import copy

        if serializer.validated_data.get('phone'):
            raise serializers.ValidationError('Обновление номера телефона запрещено.')

        gdrive = GoogleUser()
        val_photo = serializer.validated_data.get('photo')

        if not val_photo:
            serializer.save()
            return

        instance_photo = serializer.instance.photo
        copy_instance_photo = copy.copy(instance_photo)

        if copy_instance_photo:
            file_id = serializer.instance.photo_view.split('/')[-2]
            photo_name = instance_photo.name.split(os.sep)[-1]
            instance_photo.delete()
        else:
            regex = re.compile(r'\.\w*')
            prefix = regex.search(val_photo.name).group()
            full_name = serializer.instance.last_name + serializer.instance.name + serializer.instance.surname
            photo_name = f'{full_name}_{serializer.instance.tg_id}{prefix}'

        val_photo.name = photo_name
        serializer.validated_data['photo'] = val_photo

        data = serializer.save()

        if copy_instance_photo:
            gdrive.update_file(file_id=file_id, file=data.photo)
        else:
            link = gdrive.get_link_view(data.photo)
            data.photo_view = link
            data.save()

    def get_queryset(self):
        queryset = User.objects.all()
        tg_id = self.request.query_params.get('tg_id', None)
        if tg_id is not None:
            queryset = queryset.filter(tg_id=tg_id)
        return queryset


class UpdatePhoneView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['update-phone'],
        summary='Обновление номера телефона',
        request=OpenApiTypes.NONE
    )
    def patch(self, request, tg_id):
        """
        Обновление номера телефона через телеграм бот
        """
        user = get_object_or_404(User, tg_id=tg_id)

        phone_number = request.data.get('phone', None)
        if phone_number is None:
            return Response({"detail": "Номер телефона не предоставлен."}, status=status.HTTP_400_BAD_REQUEST)

        user.phone = phone_number
        user.save()

        serializer = PhoneUpdateSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RatingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RatingSerializer


class CurrentUserViewSet(generics.ListAPIView, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


def FlatpageView(request):
    return render(request, 'defaults/default_api.html')
