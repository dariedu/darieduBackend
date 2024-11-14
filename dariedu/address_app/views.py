import logging

from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from task_app.models import Delivery
from user_app.serializers import UserSerializer
from .models import Address, Location, City, RouteSheet, Beneficiar, RouteAssignment
from .serializers import (
    AddressSerializer,
    LocationSerializer,
    CitySerializer,
    RouteSheetSerializer,
    BeneficiarSerializer
)

logging.basicConfig(level=logging.INFO)

User = get_user_model()


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
    # permission_classes = [IsAutheticated]


class RouteSheetViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = RouteSheet.objects.all()
    serializer_class = RouteSheetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Curator can see only his routesheets, volunter can see only his routesheets in execution"""
        if self.request.user.is_staff:
            # logging.info(RouteSheet.objects.filter(location__curator=self.request.user, delivery__is_active=True))
            # logging.info(RouteSheet.objects.filter(location__curator=self.request.user))
            return RouteSheet.objects.filter(location__curator=self.request.user, delivery__is_active=True)
        else:
            delivery = [delivery.id for delivery in Delivery.objects.filter(in_execution=True,
                                                                            assignment__volunteer=self.request.user)]
            return RouteSheet.objects.filter(delivery__id__in=delivery)

    @action(detail=True, methods=['post'], url_name='assign_route')
    def assign(self, request, pk=None):
        """
        Assign a routesheet by curator to a volunteer with id=volunteer_id for delivery with id=delivery_id
        Body:
        {
            "volunteer_id": {id}
            "delivery_id": {id}
        }
        """
        if self.request.user.is_staff:
            routesheet = self.get_object()
            volunteer_id = self.request.data.get('volunteer_id', None)
            logging.info(volunteer_id)
            delivery_id = self.request.data.get('delivery_id', None)
            logging.info(delivery_id)
            try:
                delivery = Delivery.objects.get(id=delivery_id)
            except Delivery.DoesNotExist as error:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={'detail': 'Такой доставки не существует'})
            except Exception as error:
                logging.info(error)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Некорректные данные доставки'})
            try:
                user = User.objects.get(id=volunteer_id)
            except User.DoesNotExist as error:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={'detail': 'Такого пользователя не существует'})
            except Exception as error:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Некорректные данные пользователя'})
            # все волонтёры, записанные на эту доставку:
            volunteers_id = [assignment.volunteer.first().id for assignment in delivery.assignments.all()]
            volunteers = User.objects.filter(id__in=volunteers_id)
            if user in volunteers:
                RouteAssignment.objects.create(volunteer=user, route_sheet=routesheet, delivery=delivery)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'detail': 'Пользователь не записан на эту доставку'})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'detail': 'Доступ запрещен'})
