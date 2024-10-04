from django.db.models import F
from django.dispatch import receiver
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models.signals import m2m_changed

from .exceptions import BadRequest
from .models import Task, Delivery, DeliveryAssignment, TaskCategory
from .permissions import IsAbleCompleteTask, IsCurator  # для метода завершения задачи куратором
from .serializers import TaskSerializer, DeliverySerializer, DeliveryAssignmentSerializer, TaskVolunteerSerializer, \
    TaskCategorySerializer, DeliveryVolunteerSerializer
from .tasks import send_message_to_telegram


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
        complete: mark task as completed and add points to volunteers
        curator_of: get list of tasks where current user is curator
    """
    queryset = Task.objects.filter(
        is_active=True,
        is_completed=False,
        end_date__gt=timezone.now(),
        volunteers_needed__gt=F('volunteers_taken')  # TODO switch off when we will make autocomplete
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
            curator_of: all tasks where current user is the curator
        """
        if self.action == 'my':
            # all tasks of current user
            queryset = self.request.user.tasks.all()

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
            return self.request.user.tasks.filter(is_active=True, is_completed=False)

        # Вернуть по необходимости!
        # Для метода завершения задачи куратором
        elif self.action == 'complete':
            # can complete only active and uncompleted tasks
            return Task.objects.filter(is_active=True, is_completed=False)

        elif self.action == 'curator_of':
            # return tasks where the current user is curator
            return self.request.user.task_curator.filter(is_active=True, is_completed=False)

        # all available tasks
        return super().get_queryset()

    def get_permissions(self):
        if self.action == 'complete':
            pass
            # для метода завершения задачи куратором
            permission_classes = [IsAbleCompleteTask]
        elif self.action == 'curator_of':
            permission_classes = [IsCurator]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return TaskSerializer
        else:
            return TaskVolunteerSerializer

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

        if request.user in task.volunteers.all():
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
    @action(detail=True, methods=['post'], url_name='task_complete')
    def complete(self, request, pk=None):
        """
        Complete the task.
        Can only complete an active uncompleted task.

        Post request body should be empty. Will be ignored anyway.

        Curators only.
        """
        task = self.get_object()

        serializer = self.get_serializer(task, data={'is_active': False, 'is_completed': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_name='task_curator_of')
    def curator_of(self, request):
        """
        Get all tasks where current user is the curator of the task.

        Curators only.
        """
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_name='task_categories')
    def get_categories(self, request):
        """
        Вывод категорий задач
        """
        categories = TaskCategory.objects.all()
        serializer = TaskCategorySerializer(categories, many=True)
        return Response(serializer.data)


class DeliveryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Delivery.objects.all()

        free = self.request.query_params.get('free', None)
        active = self.request.query_params.get('active', None)
        completed = self.request.query_params.get('completed', None)

        if action == 'deliveries_curator' and self.request.user.is_staff:
            return queryset.filter(is_active=True, curator=user)

        if free is not None and free.lower() == 'true':
            queryset = queryset.filter(is_free=True).distinct()
        if active is not None and active.lower() == 'true':
            queryset = queryset.filter(is_active=True, assignments__volunteer=user).distinct()
        if completed is not None and completed.lower() == 'true':
            queryset = queryset.filter(is_completed=True, assignments__volunteer=user).distinct()
        return queryset

    def get_serializer(self, *args, **kwargs):
        if self.request.user.is_staff:
            serializer = DeliverySerializer
        else:
            serializer = DeliveryVolunteerSerializer
        return serializer(*args, **kwargs)

    @action(detail=False, methods=['get'], url_path='volunteer')
    def volunteer_deliveries(self, request):
        # serializer = DeliveryVolunteerSerializer
        free_deliveries = self.get_queryset().filter(is_free=True).exclude(
            assignments__volunteer=request.user).distinct()
        active_deliveries = self.get_queryset().filter(is_active=True, assignments__volunteer=request.user).distinct()
        completed_deliveries = self.get_queryset().filter(is_completed=True,
                                                          assignments__volunteer=request.user).distinct()
        free_serializer = self.get_serializer(free_deliveries, many=True)
        active_serializer = self.get_serializer(active_deliveries, many=True)
        completed_serializer = self.get_serializer(completed_deliveries, many=True)
        response_data = {
            'свободные доставки': free_serializer.data,
            'мои активные доставки': active_serializer.data,
            'мои завершенные доставки': completed_serializer.data
        }
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='curator')
    def deliveries_curator(self, request):
        total_deliveries = Delivery.objects.filter(in_execution=True).count()
        active_deliveries_count = Delivery.objects.filter(is_active=True).count()

        return Response({
            'выполняются доставки': total_deliveries,
            'количество активных доставок': active_deliveries_count,
        })

    @action(detail=True, methods=['post'], url_path='take')
    def take_delivery(self, request, pk):
        delivery = self.get_object()

        if delivery.is_free:
            assignment = DeliveryAssignment.objects.create(delivery=delivery)
            assignment.save()
            assignment.volunteer.add(request.user)
            serializer = DeliveryAssignmentSerializer(assignment)
            return Response({status.HTTP_201_CREATED: serializer.data})
        else:
            return Response({'error': 'Delivery is already taken'}, status=400)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_delivery(self, request, pk):
        delivery = self.get_object()
        delivery_assignment = delivery.assignments.filter(volunteer=request.user).first()

        if delivery_assignment:
            delivery_assignment.volunteer.remove(request.user)
            return Response({'message': 'Delivery cancelled successfully'}, status=200)
        else:
            return Response({'error': 'You are not authorized to cancel this delivery'}, status=403)

@receiver(m2m_changed, sender=Task.volunteers.through)
def send_message_to_telegram_on_volunteer_signup(sender, instance, action, **kwargs):
    if action == 'post_add':
        task_id = instance.id
        send_message_to_telegram.delay(task_id)
