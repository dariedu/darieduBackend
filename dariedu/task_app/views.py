from django.db.models import F
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .exceptions import BadRequest
from .models import Task, Delivery, DeliveryAssignment, TaskCategory
from .permissions import IsAbleCompleteTask, IsCurator
from .serializers import TaskSerializer, DeliverySerializer, DeliveryAssignmentSerializer, TaskVolunteerSerializer, \
    TaskCategorySerializer  #DeliveryVolunteerSerializer


class TaskViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
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
        volunteers_needed__gt=F('volunteers_taken')
    )
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['start_date', 'end_date']

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

        if self.action == 'list':
            # all available tasks
            user_tasks = self.request.user.tasks.values_list('id', flat=True)
            return Task.objects.filter(
                is_active=True,
                is_completed=False,
                end_date__gt=timezone.now(),
                volunteers_needed__gt=F('volunteers_taken')
            ).exclude(id__in=user_tasks)
        if self.action == 'my':
            # all tasks of current user
            queryset = self.request.user.tasks.all()

            return queryset

        elif self.action == 'refuse':
            # the user can only abandon his active uncompleted task
            return self.request.user.tasks.filter(is_active=True, is_completed=False)

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

        if task.volunteers_taken >= task.volunteers_needed:
            raise BadRequest("This task already has enough volunteers!")

        Task.objects.filter(pk=task.pk).update(volunteers_taken=F('volunteers_taken') + 1)
        task.volunteers.add(request.user)

        task.refresh_from_db()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='task_refuse')
    def refuse(self, request, pk=None):
        """
        Abandon the task.
        Can only abandon an active uncompleted task.

        Post request body should be empty. Will be ignored anyway.

        Authenticated only.
        """
        task = self.get_object()

        if request.user not in task.volunteers.all():
            raise BadRequest("You haven't taken this task!")
        Task.objects.filter(pk=task.pk).update(volunteers_taken=F('volunteers_taken') - 1)

        task.volunteers.remove(request.user)

        task.refresh_from_db()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='task_complete')
    def complete(self, request, pk=None):
        """
        Complete the task.
        Can only complete an active uncompleted task.

        Post request body should be empty. Will be ignored anyway.

        Curators only.
        """
        task = self.get_object()

        if request.user not in task.volunteers.all():
            raise BadRequest("You haven't taken this task!")

        # Атомарное обновление количества волонтеров
        Task.objects.filter(pk=task.pk).update(
            volunteers_taken=F('volunteers_taken') - 1
        )
        # Удаление волонтера
        task.volunteers.remove(request.user)

        # Обновляем объект из БД
        task.refresh_from_db()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='task_complete')
    def complete(self, request, pk=None):
        task = self.get_object()

        if not request.user.is_curator or request.user != task.curator:
            raise PermissionDenied("Only the task curator can complete the task")

        if task.is_completed:
            raise BadRequest("Task is already completed")

        task.is_completed = True
        task.is_active = False
        task.save()

        task.volunteers.all().update(
            volunteer_hour=F('volunteer_hour') + task.volunteer_price,
            point=F('point') + task.volunteer_price
        )

        task.curator.update(
            volunteer_hour=F('volunteer_hour') + task.curator_price,
            point=F('point') + task.curator_price
        )

        task.refresh_from_db()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    # def get_serializer(self, *args, **kwargs):
    #     if self.request.user.is_staff:
    #         serializer = DeliverySerializer
    #     else:
    #         serializer = DeliverySerializer
    #     return serializer(*args, **kwargs)

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
        total_deliveries = Delivery.objects.filter(in_execution=True)
        id_deliveries = total_deliveries.values_list('id', flat=True)
        active_deliveries = Delivery.objects.filter(is_active=True)
        id_active_deliveries = active_deliveries.values_list('id', flat=True)

        return Response({
            'выполняются доставки (id)': id_deliveries,
            'количество активных доставок (id)': id_active_deliveries,
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

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_delivery(self, request, pk):
        delivery = self.get_object()
        if self.request.user != delivery.curator:
            return Response({'error': 'You are not authorized to complete this delivery'}, status=403)
        else:
            if delivery.is_completed:
                return Response({'error': 'Delivery is already completed'}, status=400)
            else:
                delivery.is_completed = True
                delivery.in_execution = False
                delivery.is_active = False
                delivery.is_free = False
                delivery.curator.update(volunteer_hour=F('volunteer_hour') + 4,
                                        point=F('point') + 4)
                delivery.assignments.volunteer.update(volunteer_hour=F('volunteer_hour') + delivery.price,
                                                      point=F('point') + delivery.price)
                delivery.save()
                return Response({'message': 'Delivery completed successfully'}, status=200)
