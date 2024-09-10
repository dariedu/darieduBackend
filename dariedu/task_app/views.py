from django.core.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from django.db.models import F
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user_app.models import User
from .exceptions import BadRequest
from .models import Task, Delivery
# from .permissions import IsAbleCompleteTask  # для метода завершения задачи куратором
from .serializers import TaskSerializer, DeliverySerializer


class TaskViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint that provides methods to work with tasks.

    Actions:
        list: get a list of available tasks
        my: get a user specific tasks (supports filtering)
        accept: accept an available task
        refuse: refuse a user specific active uncompleted task
    """
    queryset = Task.objects.filter(
        is_active=True,
        is_completed=False,
        end_date__gt=timezone.now(),
        volunteers_needed__gt=F('volunteers_taken')
    )
    serializer_class = TaskSerializer
    ordering_fields = ['start_date', 'end_date', 'price']

    def get_queryset(self):
        """
        Get queryset for specific action.

        Actions:
            list: all available tasks
            my: user specific tasks + filtering against query params
            accept: all available tasks
            refuse: user specific active uncompleted tasks
            complete: active uncompleted tasks only
        """
        if self.action == 'my':
            # all tasks of current user
            queryset = User.objects.get(pk=1).tasks.all()
            # queryset = self.request.user.tasks.all() # TODO swap to comment

            is_active = self.request.query_params.get('is_active', None)
            is_completed = self.request.query_params.get('is_completed', None)

            if is_active is not None:
                if is_active == '0' or is_active == '1':
                    bool_is_active = bool(int(is_active))
                    queryset = queryset.filter(is_active=bool_is_active)
                else:
                    raise BadRequest(f"Incorrect 'is_active' value: {is_active}! Must be either 0 or 1.")

            if is_completed is not None:
                if is_completed == '0' or is_completed == '1':
                    bool_is_completed = bool(int(is_completed))
                    queryset = queryset.filter(is_completed=bool_is_completed)
                else:
                    raise BadRequest(f"Incorrect 'is_completed' value: {is_completed}! Must be either 0 or 1.")

            return queryset

        elif self.action == 'refuse':
            # the user can only abandon his active uncompleted task
            # return self.request.user.tasks.filter(is_active=True, is_completed=False)
            return User.objects.get(pk=1).tasks.filter(is_active=True, is_completed=False)  # TODO swap to comment

        # Вернуть по необходимости!
        # Для метода завершения задачи куратором
        # elif self.action == 'complete':
        #     # can complete only active and uncompleted tasks
        #     return Task.objects.filter(is_active=True, is_completed=False)

        # all available tasks
        return super().get_queryset()

    def get_permissions(self):
        if self.action == 'complete':
            pass
            # для метода завершения задачи куратором
            # permission_classes = [IsAbleCompleteTask]
        else:
            # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'], url_name='my_tasks')
    def my(self, request):
        """
        Get current user's tasks.
        Returns all user's tasks by default.

        Filtering by is_active and/or is_completed is supported.

        Authenticated only.
        """
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='task_accept')
    def accept(self, request, pk=None):
        """
        Accept an available task.

        Post request body should be empty. Will be ignored anyway.

        Authenticated only.
        """
        task = self.get_object()

        user = User.objects.get(pk=1)
        if user in task.volunteers.all():  # TODO change to request.user
            raise BadRequest("You have already taken this task!")

        serializer = self.get_serializer(task, data={'volunteers_taken': task.volunteers_taken + 1}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='task_refuse')
    def refuse(self, request, pk=None):
        """
        Abandon the task.
        Can only abandon an active uncompleted task.

        Post request body should be empty. Will be ignored anyway.

        Authenticated only.
        """
        task = self.get_object()

        serializer = self.get_serializer(task, data={'volunteers_taken': task.volunteers_taken - 1}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # Вернуть по необходимости!
    # Метод завершения задачи куратором
    # @action(detail=True, methods=['post'], url_name='task_complete')
    # def complete(self, request, pk=None):
    #     """
    #     Complete the task.
    #     Can only complete an active uncompleted task.
    #
    #     Post request body should be empty. Will be ignored anyway.
    #
    #     Curators only.
    #     """
    #     task = self.get_object()
    #
    #     serializer = self.get_serializer(task, data={'is_active': False, 'is_completed': True}, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #
    #     return Response(data=serializer.data, status=status.HTTP_200_OK)


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
