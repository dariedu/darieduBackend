from django.core.exceptions import ValidationError
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

    def list(self, request, *args, **kwargs):
        queryset = Delivery.objects.all()
        is_active = request.query_params.get('is_active')
        is_completed = request.query_params.get('is_completed')
        volunteer = request.query_params.get('volunteer')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        if is_completed is not None:
            is_completed = is_completed.lower() == 'true'
            queryset = queryset.filter(is_completed=is_completed)
        if volunteer is not None:
            queryset = queryset.filter(volunteer=volunteer)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='volunteer')
    def volunteer_deliveries(self, request):
        user = request.user
        is_free_deliveries = Delivery.objects.filter(is_free=True)
        is_active_deliveries = Delivery.objects.filter(volunteer=user, is_active=True)
        completed_deliveries = Delivery.objects.filter(volunteer=user, is_completed=True)
        is_free_serializer = self.get_serializer(is_free_deliveries, many=True)
        is_active_serializer = self.get_serializer(is_active_deliveries, many=True)
        is_completed_serializer = self.get_serializer(completed_deliveries, many=True)

        return Response({
            'свободные': is_free_serializer.data,
            'мои активные доставки': is_active_serializer.data,
            'мои завершенные доставки': is_completed_serializer.data
        })

    @action(detail=False, methods=['get'], url_path='curator')
    def deliveries_curator(self, request):
        total_deliveries = Delivery.objects.filter(in_execution=True).count()
        active_deliveries = Delivery.objects.filter(is_active=True).count()

        return Response({
            'выполняются доставки': total_deliveries,
            'количество активных доставок': active_deliveries
        })

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

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_delivery(self, request, pk):
        delivery = self.get_object()
        serializer = DeliverySerializer(instance=delivery, data={}, context={'view': self, 'request': request},
                                        partial=True)

        if not delivery.is_active:
            return Response({'error': 'Delivery is already finished'}, status=400)

        if delivery.volunteer != request.user and delivery.volunteer is None:
            return Response({'error': 'You are not authorized to cancel this delivery'}, status=403)

        if delivery.volunteer == request.user:
            delivery.is_active = True
            delivery.is_free = True
            delivery.in_execution = False
            delivery.volunteer = None
            delivery.save()
        if serializer.is_valid():
            return Response({status.HTTP_201_CREATED: serializer.data})
        else:
            return Response({'error': 'You are not authorized to cancel this delivery'}, status=403)
