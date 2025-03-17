import logging

from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view
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
    queryset = RouteSheet.objects.all().order_by('name')
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
                Q(id__in=route_assignment.values_list('route_sheet_id', flat=True))).distinct().order_by('name')
        else:
            return RouteSheet.objects.filter(
                id__in=route_assignment.values_list('route_sheet_id', flat=True)).distinct().order_by('name')

    @action(detail=False, methods=['post'], url_name='assign_route')
    def assign(self, request):
        """
        Assign a routesheet by curator to multiple volunteers for a delivery with id=delivery_id
        Body:
        {
            "routesheet_id": {id},
            "volunteer_ids": [{id1}, {id2}, ...],
            "delivery_id": {id}
        }
        """
        if self.request.user.is_staff:
            routesheet_id = request.data.get('routesheet_id', None)
            volunteer_ids = request.data.get('volunteer_ids', [])
            delivery_id = request.data.get('delivery_id', None)

            routesheet = get_object_or_404(RouteSheet, id=routesheet_id)
            delivery = get_object_or_404(Delivery, id=delivery_id)

            if delivery.curator != self.request.user:
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'detail': 'Вы не являетесь куратором этой доставки'})
            if delivery.is_completed:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Доставка уже завершена'})
            if routesheet.id not in delivery.route_sheet.all().values_list('id', flat=True):
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Данного маршрута нет в этой доставке'})

            route_assignment, created = RouteAssignment.objects.get_or_create(
                route_sheet=routesheet,
                delivery=delivery
            )

            current_count = route_assignment.volunteer.count()

            if current_count + len(volunteer_ids) > 2:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'На один маршрут можно назначить максимум два волонтера'})

            for volunteer_id in volunteer_ids:
                user = get_object_or_404(User, id=volunteer_id)

                if user in route_assignment.volunteer.all():
                    return Response(status=status.HTTP_400_BAD_REQUEST,
                                    data={'detail': f'Волонтёр с ID {volunteer_id} уже назначен на этот маршрут'})

                route_assignment.volunteer.add(user)

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'detail': 'Доступ запрещен'})

    @action(detail=False, methods=['post'], url_name='remove_volunteer')
    def remove_volunteer(self, request):
        """
        Remove a volunteer from a routesheet for a delivery with id=delivery_id
        Body:
        {
            "routesheet_id": {id},
            "volunteer_id": {id},
            "delivery_id": {id}
        }
        """
        if self.request.user.is_staff:
            routesheet_id = request.data.get('routesheet_id', None)
            volunteer_id = request.data.get('volunteer_id', None)
            delivery_id = request.data.get('delivery_id', None)

            routesheet = get_object_or_404(RouteSheet, id=routesheet_id)
            delivery = get_object_or_404(Delivery, id=delivery_id)

            if delivery.curator != self.request.user:
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'detail': 'Вы не являетесь куратором этой доставки'})
            if delivery.is_completed:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Доставка уже завершена'})
            if routesheet.id not in delivery.route_sheet.all().values_list('id', flat=True):
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Данного маршрута нет в этой доставке'})

            route_assignments = RouteAssignment.objects.filter(route_sheet=routesheet, delivery=delivery)

            if not route_assignments.exists():
                return Response(status=status.HTTP_404_NOT_FOUND, data={'detail': 'Назначение не найдено'})

            user = get_object_or_404(User, id=volunteer_id)

            for route_assignment in route_assignments:
                if user in route_assignment.volunteer.all():
                    route_assignment.volunteer.remove(user)
                    return Response(status=status.HTTP_200_OK)

            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': f'Волонтёр с ID {volunteer_id} не назначен на этот маршрут'})

        else:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'detail': 'Доступ запрещен'})

class RouteAssignmentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = RouteAssignment.objects.filter(delivery__date__gte=timezone.now() - timezone.timedelta(days=14))
    serializer_class = RouteAssignmentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='by_delivery')
    def by_delivery(self, request, pk=None):
        """
        Вывод маршрутов по доставке
        """
        delivery = get_object_or_404(Delivery, pk=pk)
        route_assignments = RouteAssignment.objects.filter(delivery=delivery)
        serializer = RouteAssignmentSerializer(route_assignments, many=True)
        return Response(serializer.data)
