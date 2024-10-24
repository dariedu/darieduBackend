import logging

from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user_app.models import User
from user_app.serializers import UserSerializer
from .models import Address, Location, City, RouteSheet, Beneficiar
from .serializers import (
    AddressSerializer,
    LocationSerializer,
    CitySerializer,
    RouteSheetSerializer,
    BeneficiarSerializer
)

logging.basicConfig(level=logging.INFO)


class LocationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """For curator to see his locations"""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready

    def get_queryset(self):
        """Curator can see only his locations"""
        if self.request.user.is_staff:
            return Location.objects.filter(curator=self.request.user)


class CityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    # permission_classes = [IsAutheticated]  # TODO swap to comment when authentication is ready


class RouteSheetViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = RouteSheet.objects.all()
    serializer_class = RouteSheetSerializer
    permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready

    def get_queryset(self):
        """Curator can see only his routesheets, volunter can see only his routesheets in execution"""
        if self.request.user.is_staff:
            # logging.info(RouteSheet.objects.filter(location__curator=self.request.user, delivery__is_active=True))
            # logging.info(RouteSheet.objects.filter(location__curator=self.request.user))
            return RouteSheet.objects.filter(location__curator=self.request.user, delivery__is_active=True)
        else:
            return RouteSheet.objects.filter(user=self.request.user, delivery__in_execution=True)

    @action(detail=True, methods=['post'], url_name='assign_route')
    def assign(self, request, pk=None):
        """
        Assign a routesheet by curator to a volunteer with id=volunteer_id
        Body:
        {
            "volunteer_id":
        }
        """
        if self.request.user.is_staff:
            routesheet = self.get_object()
            volunteer_id = self.request.data.get('volunteer_id', None)
            # все волонтёры, записанные на эту доставку:
            volunteers = routesheet.delivery.filter(is_active=True).assignment.volunteer.all()
            try:
                user = User.get(id=volunteer_id)
            except User.DoesNotExist as error:
                # logging.info(error, exc_info=True)
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={'detail': 'Такого пользователя не существует'})
            except Exception as error:
                # logging.info(error, exc_info=True)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Неправильные данные'})
            if user in volunteers:
                routesheet.user = user
                routesheet.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'detail': 'Пользователь не записан на эту доставку'})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'detail': 'Доступ запрещен'})
#