import logging

from django.contrib.auth import get_user_model
from django.db.models import Q
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
    BeneficiarSerializer, RouteAssignmentSerializer
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
        delivery = [delivery.id for delivery in Delivery.objects.filter(in_execution=True,
                                                                        assignments__volunteer=self.request.user)]
        # logging.info(delivery)
        route_assignment = RouteAssignment.objects.filter(volunteer=self.request.user, delivery__id__in=delivery)
        if self.request.user.is_staff:
            # logging.info(RouteSheet.objects.filter(location__curator=self.request.user, delivery__is_active=True))
            # logging.info(RouteSheet.objects.filter(location__curator=self.request.user))
            return RouteSheet.objects.filter(
                Q(location__curator=self.request.user, delivery__is_active=True) |
                Q(id__in=route_assignment.values_list('route_sheet_id', flat=True))).distinct()
        else:
            return RouteSheet.objects.filter(
                id__in=route_assignment.values_list('route_sheet_id', flat=True)).distinct()

    @action(detail=False, methods=['post'], url_name='assign_route')
    def assign(self, request):
        """
        Assign a routesheet by curator to a volunteer with id=volunteer_id for delivery with id=delivery_id
        Body:
        {
            "routesheet_id": {id},
            "volunteer_id": {id}
            "delivery_id": {id}
        }
        """
        if self.request.user.is_staff:
            routesheet_id = self.request.data.get('routesheet_id', None)
            logging.info(routesheet_id)
            volunteer_id = self.request.data.get('volunteer_id', None)
            logging.info(volunteer_id)
            delivery_id = self.request.data.get('delivery_id', None)
            logging.info(delivery_id)
            try:
                routesheet = RouteSheet.objects.get(id=routesheet_id)
            except RouteSheet.DoesNotExist as error:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={'detail': 'Такой маршрут не существует'})
            except Exception as error:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Некорректные данные маршрута'})
            try:
                delivery = Delivery.objects.get(id=delivery_id)
            except Delivery.DoesNotExist as error:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={'detail': 'Такой доставки не существует'})
            except Exception as error:
                logging.info(error)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Некорректные данные доставки'})
            if delivery.curator != self.request.user:
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'detail': 'Вы не являетесь куратором этой доставки'})
            if delivery.is_completed:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Доставка уже завершена'})
            if routesheet.id not in delivery.route_sheet.all().values_list('id', flat=True):
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Данного маршрута нет в этой доставке'})
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
                try:
                    route = RouteAssignment.objects.get(route_sheet=routesheet, delivery=delivery)
                    route.delete()
                except RouteAssignment.DoesNotExist as error:
                    pass

                RouteAssignment.objects.create(volunteer=user, route_sheet=routesheet, delivery=delivery)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'detail': 'Пользователь не записан на эту доставку'})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'detail': 'Доступ запрещен'})


class RouteAssignmentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = RouteAssignment.objects.all()
    serializer_class = RouteAssignmentSerializer
    permission_classes = [IsAuthenticated]
