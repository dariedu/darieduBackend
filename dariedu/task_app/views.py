from django.core.exceptions import ValidationError
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Delivery, Task
from .serializers import DeliverySerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_fields = [
        'is_active',
        'curator',
        'volunteer',
        'category',
        'date'
    ]
    ordering_fields = ['date', 'price']

class DeliveryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Deliveries"],
        summary="List deliveries",
        operation_id="listDeliveries",
        responses={200: OpenApiResponse(description="List deliveries")},
        description='List deliveries'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Deliveries"],
        summary="Get deliveries for volunteer",
        operation_id="getVolunteerDeliveries",
        responses={200: OpenApiResponse(description="Get volunteer deliveries")},
    )
    @action(detail=False, methods=['get'], url_path='volunteer')
    def volunteer_deliveries(self, request):
        user = request.user
        is_free_deliveries = Delivery.objects.filter(is_free=True)
        is_active_deliveries = Delivery.objects.filter(volunteer=user, is_active=True)
        is_free_serializer = self.get_serializer(is_free_deliveries, many=True)
        is_active_serializer = self.get_serializer(is_active_deliveries, many=True)

        return Response({
            'свободные': is_free_serializer.data,
            'мои активные доставки': is_active_serializer.data
        })

    @extend_schema(
        tags=["Deliveries"],
        summary="Get all deliveries for curator",
        operation_id="getAllDeliveriesByCurator",
        responses={200: OpenApiResponse(description="Get all deliveries for curator")},
    )
    @action(detail=False, methods=['get'], url_path='curator')
    def deliveries_curator(self, request):
        total_deliveries = Delivery.objects.count()
        active_deliveries = Delivery.objects.filter(is_active=True).count()

        return Response({
            'количество доставок': total_deliveries,
            'количество активных доставок': active_deliveries
        })

    @extend_schema(
        tags=["Deliveries"],
        summary="Take a delivery",
        operation_id="takeDelivery",
        request=None,
        responses={201: OpenApiResponse(description="Delivery taken successfully")},
    )
    @action(detail=True, methods=['post'], url_path='take')
    def take_delivery(self, request, pk):
        delivery = get_object_or_404(Delivery, pk=pk)
        if delivery.volunteer:
            return Response({'error': 'Delivery is already taken'}, status=400)
        serializer = DeliverySerializer(instance=delivery, data={}, context={'view': self, 'request': request},
                                        partial=True)
        try:
            serializer.create(serializer.instance)
            if serializer.is_valid():
                return Response({status.HTTP_201_CREATED: serializer.data})
        except ValidationError as e:
            return Response({'error': 'Volunteer already assigned to this delivery'}, status=400)
        except Exception as e:
            return Response({'error': 'Internal Server Error'}, status=500)

    @extend_schema(
        tags=["Deliveries"],
        summary="Cancel a delivery",
        operation_id="takeDelivery",
        request=None,
        responses={201: OpenApiResponse(description="Delivery successfully canceled")},
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_delivery(self, request, pk):
        delivery = self.get_object()
        serializer = DeliverySerializer(instance=delivery, data={}, context={'view': self, 'request': request},
                                        partial=True)
        if delivery.volunteer == request.user:
            delivery.is_active = False
            delivery.is_free = True
            delivery.volunteer = None
            delivery.save()
        if serializer.is_valid():
            return Response({status.HTTP_201_CREATED: serializer.data})
        else:
            return Response({'error': 'You are not authorized to cancel this delivery'}, status=403)
