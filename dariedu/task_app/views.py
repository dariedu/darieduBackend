from django.db.models import F
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from address_app.models import RouteAssignment
from dariedu.settings import CURRENT_HOST
from .models import Task, Delivery, DeliveryAssignment, TaskCategory, TaskParticipation
from .permissions import IsAbleCompleteTask, IsCurator, is_confirmed
from .serializers import TaskSerializer, DeliverySerializer, DeliveryAssignmentSerializer, TaskVolunteerSerializer, \
    TaskCategorySerializer, TaskParticipationSerializer
from .signals import volunteer_confirmed
from .tests.test_adminpanel import delivery


class TaskViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint that provides methods to work with tasks.

    Actions:
        list: get a list of available tasks + filtering by date (for start_date) YYYY-MM-DD, category and city
        my: get a user specific tasks (supports filtering)
        accept: accept an available task
        refuse: refuse a user specific active uncompleted task
        complete: mark task as completed and add points to volunteers
        curator_of: get list of tasks where current user is curator
        categories: get list of task categories
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['start_date', 'end_date']
    filterset_fields = ['category', 'city']

    def filter_queryset(self, queryset):
        user = self.request.user

        after = self.request.query_params.get('after', None)
        before = self.request.query_params.get('before', None)
        active = self.request.query_params.get('is_active', None)
        completed = self.request.query_params.get('is_completed', None)
        if after:
            try:
                after = timezone.datetime.strptime(after, '%Y-%m-%d')
                queryset = queryset.filter(end_date__date__gte=after)
            except ValueError:
                pass
        if before:
            try:
                before = timezone.datetime.strptime(before, '%Y-%m-%d')
                queryset = queryset.filter(start_date__date__lte=before)
            except ValueError:
                pass
        if active is not None and active.lower() == 'true':
            queryset = queryset.filter(is_active=True).distinct()
        elif active is not None and active.lower() == 'false':
            queryset = queryset.filter(is_active=False).distinct()
        if completed is not None and completed.lower() == 'true':
            queryset = queryset.filter(is_completed=True).distinct()
        elif completed is not None and completed.lower() == 'false':
            queryset = queryset.filter(is_completed=False).distinct()
        return queryset

    def get_queryset(self):
        """
        Get queryset for specific action.

        Actions:
            list: all available tasks + filtering by date (for start_date) YYYY-MM-DD, category and city
            my: user specific tasks + filtering against query params
            accept: all available tasks
            refuse: user specific active uncompleted tasks
            complete: active uncompleted tasks only
            curator_of: all tasks where current user is the curator
        """

        if self.action == 'list':
            # all available tasks
            user_tasks = self.request.user.tasks.values_list('id', flat=True)
            date = self.request.query_params.get('date', None)
            queryset = Task.objects.filter(
                is_active=True,
                is_completed=False,
                end_date__gt=timezone.now(),
                volunteers_needed__gt=F('volunteers_taken')
            ).exclude(id__in=user_tasks)
            if date:
                try:
                    date = timezone.datetime.strptime(date, '%Y-%m-%d')
                    queryset = queryset.filter(start_date__date=date)
                except ValueError:
                    pass
            return queryset

        if self.action == 'my':
            user = self.request.user
            queryset = user.tasks.all()
            queryset = self.filter_queryset(queryset)
            return queryset

        elif self.action == 'refuse':
            # the user can only abandon his active uncompleted task
            return self.request.user.tasks.filter(is_active=True, is_completed=False)

        elif self.action == 'complete':
            # curator can complete only active and uncompleted tasks
            return Task.objects.filter(is_active=True, is_completed=False)

        elif self.action == 'curator_of':
            # return tasks where the current user is curator
            queryset = self.request.user.task_curator
            queryset = self.filter_queryset(queryset)
            return queryset.filter(start_date__gte=timezone.now() - timezone.timedelta(days=14))

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
    @is_confirmed
    def my(self, request):
        """
        Get current user's tasks.
        Returns all user's tasks by default.
        Authenticated only.
        Filters:
        is_active - filter tasks by active status, for available is true or false
        is_completed - filter tasks by completed status, for history is true or false
        after - filter tasks by start date
        before - filter tasks by end date
        Пример фильтров для календаря: api/tasks/my/?after=2024-10-05&before=2024-10-20
        Формат даты: YYYY-MM-DD
        можно использовать вместе или по отдельности
        """
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='task_accept')
    @is_confirmed
    def accept(self, request, pk=None):
        """
        Accept an available task.
        Post request body should be empty. Will be ignored anyway.
        Authenticated only.
        """
        task = self.get_object()

        if request.user in task.volunteers.all():
            return Response({"error": "You've already taken this task!"}, status=status.HTTP_400_BAD_REQUEST)

        if task.volunteers_taken >= task.volunteers_needed:
            return Response({"error": "This task is full!"}, status=status.HTTP_400_BAD_REQUEST)

        Task.objects.filter(pk=task.pk).update(volunteers_taken=F('volunteers_taken') + 1)
        task.volunteers.add(request.user)

        TaskParticipation.objects.create(task=task, volunteer=request.user)

        task.refresh_from_db()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='task_refuse')
    @is_confirmed
    def refuse(self, request, pk=None):
        """
        Abandon the task.
        Can only abandon an active uncompleted task.
        Post request body should be empty. Will be ignored anyway.
        Authenticated only.
        """
        task = self.get_object()

        if request.user not in task.volunteers.all():
            return Response({"error": "You haven't taken this task!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participation = task.task_part.get(volunteer=request.user)
            participation.delete()
        except TaskParticipation.DoesNotExist:
            return Response({"error": "Participation record not found."}, status=status.HTTP_400_BAD_REQUEST)

        Task.objects.filter(pk=task.pk).update(volunteers_taken=F('volunteers_taken') - 1)

        task.volunteers.remove(request.user)

        task.refresh_from_db()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='task_confirm')
    @is_confirmed
    def confirm(self, request, pk):
        """
        Confirm the task.
        Can only confirm an active uncompleted task.
        Post request body should be empty. Will be ignored anyway.
        Curators only.
        """
        try:
            task = self.get_object()

            volunteer_participation = task.task_part.get(volunteer=request.user)

            if volunteer_participation is not None:
                if volunteer_participation.confirmed:
                    return Response({"error": "Вы уже подтвердили участие в этом добром деле!"},
                                    status=status.HTTP_400_BAD_REQUEST)
                volunteer_participation.confirmed = True
                volunteer_participation.save(update_fields=['confirmed'])
                serializer = TaskParticipationSerializer(volunteer_participation)

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Вы не взяли участие в этом добром деле!"},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_name='list_not_confirmed')
    @is_confirmed
    def list_not_confirmed(self, request):
        """
        Get a list of not confirmed tasks of a particular volunteer.
        """
        try:
            user = request.user
            tasks = TaskParticipation.objects.filter(volunteer=user, confirmed=False, task__is_active=True).all()

            if tasks is None:
                return Response({"error": "No tasks found"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = TaskParticipationSerializer(tasks, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_name='list_confirmed_tasks')
    @is_confirmed
    def list_confirmed_tasks(self, request):
        """
        Get a list of confirmed tasks of a particular volunteer.
        """
        try:
            user = request.user
            tasks = TaskParticipation.objects.filter(task__curator=user, confirmed=True, task__is_active=True).all()

            if tasks is None:
                return Response({"error": "No tasks found"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = TaskParticipationSerializer(tasks, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_name='task_complete')
    @is_confirmed
    def complete(self, request, pk=None):
        """
        Complete the task.
        Can only complete an active uncompleted task.
        Post request body should be empty. Will be ignored anyway.
        Curators only.
        """
        task = self.get_object()

        if task.is_completed:
            return Response({"error": "This task is already completed!"}, status=status.HTTP_400_BAD_REQUEST)

        task.is_completed = True
        task.is_active = False
        task.save(update_fields=['is_completed', 'is_active'])
        task.refresh_from_db()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_name='task_curator_of')
    @is_confirmed
    def curator_of(self, request):
        """
        Get all tasks FOR LAST TWO WEEKS where current user is the curator of the task.
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


class DeliveryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['date']

    def get_queryset(self):
        user = self.request.user
        queryset = Delivery.objects.all()

        free = self.request.query_params.get('free', None)
        active = self.request.query_params.get('active', None)
        completed = self.request.query_params.get('completed', None)
        date = self.request.query_params.get('date', None)

        # TODO it works only for list. need to add for volunteers and curators deliveries
        if date:
            try:
                date = timezone.datetime.strptime(date, '%Y-%m-%d')
                self.queryset = self.queryset.filter(date__date=date)
            except ValueError:
                pass

        if action == 'deliveries_curator' and self.request.user.is_staff:
            return queryset.filter(is_active=True, curator=user).order_by('date')

        if free is not None and free.lower() == 'true':
            queryset = queryset.filter(is_free=True).distinct().order_by('date')
        if active is not None and active.lower() == 'true':
            queryset = queryset.filter(is_active=True, assignments__volunteer=user).distinct().order_by('date')
        if completed is not None and completed.lower() == 'true':
            queryset = queryset.filter(is_completed=True, assignments__volunteer=user).distinct().order_by('date')
        return queryset

    @action(detail=False, methods=['get'], url_path='volunteer')
    def volunteer_deliveries(self, request):
        """
        Пример фильтров для календаря:
        api/deliveries/volunteer/?after=2024-10-05&before=2024-10-20 - для активных,
        выполняющихся и завершенных доставок
        api/deliveries/volunteer/?date=2024-10-20 - для свободных доставок, выбор по конкретной дате.
        Подойдет для главной страницы
        Формат даты: YYYY-MM-DD
        можно использовать вместе или по отдельности
        """
        after = self.request.query_params.get('after', None)
        before = self.request.query_params.get('before', None)
        date = self.request.query_params.get('date', None)

        free_deliveries = self.get_queryset().filter(is_free=True).exclude(
            assignments__volunteer=request.user).distinct().order_by('date')
        active_deliveries = self.get_queryset().filter(
            is_active=True, assignments__volunteer=request.user).distinct().order_by('date')
        completed_deliveries = self.get_queryset().filter(
            is_completed=True, assignments__volunteer=request.user).distinct().order_by('date')
        executing_deliveries = self.get_queryset().filter(is_active=True, assignments__volunteer=request.user,
                                                          in_execution=True).distinct().order_by('date')

        if after:
            try:
                after_date = timezone.datetime.strptime(after, '%Y-%m-%d')
                active_deliveries = active_deliveries.filter(date__date__gte=after_date)
                completed_deliveries = completed_deliveries.filter(date__date__gte=after_date)
            except ValueError:
                return Response({'error': 'Invalid date format for "after". Expected format: YYYY-MM-DD'},
                                status=400)

        if before:
            try:
                before_date = timezone.datetime.strptime(before, '%Y-%m-%d')
                active_deliveries = active_deliveries.filter(date__date__lte=before_date)
                completed_deliveries = completed_deliveries.filter(date__date__lte=before_date)
            except ValueError:
                return Response({
                    'error': 'Invalid date format for "before". Expected format: YYYY-MM-DD'
                }, status=400)

        if date:
            try:
                date = timezone.datetime.strptime(date, '%Y-%m-%d')
                free_deliveries = free_deliveries.filter(date__date=date)
            except ValueError:
                return Response({'error': 'Invalid date format for "date". Expected format: YYYY-MM-DD'},
                                status=400)

        free_serializer = self.get_serializer(free_deliveries, many=True)
        active_serializer = self.get_serializer(active_deliveries, many=True,
                                                context={'is_volunteer_view': True})
        completed_serializer = self.get_serializer(completed_deliveries, many=True,
                                                   context={'is_volunteer_view': True})

        executing_serializer = self.get_serializer(executing_deliveries, many=True,
                                                   context={'is_volunteer_view': True})

        response_data = {
            'свободные доставки': free_serializer.data,
            'мои активные доставки': active_serializer.data,
            'выполняются доставки': executing_serializer.data,
            'мои завершенные доставки': completed_serializer.data
        }
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='curator')
    @is_confirmed
    def deliveries_curator(self, request):
        total_deliveries = Delivery.objects.filter(in_execution=True, curator=request.user).order_by('date')
        active_deliveries = Delivery.objects.filter(
            is_active=True, curator=request.user, in_execution=False).order_by('date')
        complete_deliveries = Delivery.objects.filter(is_completed=True, curator=request.user).order_by('date')

        executing_deliveries = []
        for delivery in total_deliveries:
            route_sheet_ids = [route.id for route in delivery.route_sheet.all()]
            assignments = DeliveryAssignment.objects.filter(delivery=delivery)

            volunteers_info = []
            for assignment in assignments:
                for volunteer in assignment.volunteer.all():
                    volunteers_info.append({
                        "id": volunteer.id,
                        "tg_username": volunteer.tg_username,
                        "last_name": volunteer.last_name,
                        "name": volunteer.name,
                        "photo": (CURRENT_HOST + volunteer.photo.url) if volunteer.photo else None
                    })

            executing_deliveries.append({
                "id_delivery": delivery.id,
                "id_route_sheet": route_sheet_ids,
                'volunteers': volunteers_info
            })

        active_deliveries_list = []
        for delivery in active_deliveries:
            route_sheet_ids = [route.id for route in delivery.route_sheet.all()]
            assignments = DeliveryAssignment.objects.filter(delivery=delivery).order_by("delivery__date")

            volunteers_info = []
            for assignment in assignments:
                for volunteer in assignment.volunteer.all():
                    volunteers_info.append({
                        "id": volunteer.id,
                        "tg_username": volunteer.tg_username,
                        "last_name": volunteer.last_name,
                        "name": volunteer.name,
                        "photo": (CURRENT_HOST + volunteer.photo.url) if volunteer.photo else None
                    })

            active_deliveries_list.append({
                "id_delivery": delivery.id,
                "id_route_sheet": route_sheet_ids,
                'volunteers': volunteers_info
            })

        complete_deliveries_list = []
        for delivery in complete_deliveries:
            route_sheet_ids = [route.id for route in delivery.route_sheet.all()]
            assignments = DeliveryAssignment.objects.filter(delivery=delivery).order_by("delivery__date")

            volunteers_info = []
            for assignment in assignments:
                for volunteer in assignment.volunteer.all():
                    volunteers_info.append({
                        "id": volunteer.id,
                        "tg_username": volunteer.tg_username,
                        "last_name": volunteer.last_name,
                        "name": volunteer.name,
                        "photo": (CURRENT_HOST + volunteer.photo.url) if volunteer.photo else None
                    })

            complete_deliveries_list.append({
                "id_delivery": delivery.id,
                "id_route_sheet": route_sheet_ids,
                'volunteers': volunteers_info
            })

        return Response({
            'выполняются доставки': executing_deliveries,
            'активные доставки': active_deliveries_list,
            'завершенные доставки': complete_deliveries_list
        })

    @action(detail=True, methods=['post'], url_path='take')
    @is_confirmed
    def take_delivery(self, request, pk):
        delivery = self.get_object()

        if delivery.is_free:
            if not DeliveryAssignment.objects.filter(delivery=delivery, volunteer=request.user).exists():
                assignment = DeliveryAssignment.objects.create(delivery=delivery)
                assignment.save()
                assignment.volunteer.add(request.user)
                serializer = DeliveryAssignmentSerializer(assignment)
                return Response({status.HTTP_201_CREATED: serializer.data})
            else:
                return Response({'error': 'You have already taken this delivery'}, status=400)
        else:
            return Response({'error': 'Delivery is already taken'}, status=400)

    @action(detail=True, methods=['post'], url_path='cancel')
    @is_confirmed
    def cancel_delivery(self, request, pk):
        delivery = self.get_object()
        delivery_assignment = delivery.assignments.filter(volunteer=request.user).first()
        assignment = DeliveryAssignment.objects.filter(delivery=delivery, volunteer=request.user).first()
        route_assignment = RouteAssignment.objects.filter(delivery=delivery, volunteer=request.user).first()

        if delivery_assignment:
            if route_assignment:
                route_assignment.delete()
            delivery_assignment.volunteer.remove(request.user)
            assignment.delete()
            return Response({'message': 'Delivery cancelled successfully'}, status=200)
        else:
            return Response({'error': 'You are not authorized to cancel this delivery'}, status=403)

    @action(detail=True, methods=['post'], url_path='confirm')
    @is_confirmed
    def confirm_delivery(self, request, pk):
        """
        Confirm delivery.
        """
        try:
            delivery = self.get_object()
            assignment = delivery.assignments.filter(volunteer=request.user).first()

            if assignment is not None:

                if assignment.confirm:
                    return Response({'error': 'Вы уже подтвердили участие в этой доставке.'}, status=400)

                assignment.confirm = True
                assignment.save()

                volunteer_confirmed.send(sender=self.__class__, volunteer=request.user, assignment=assignment)

                return Response({'message': 'Delivery confirmed successfully'}, status=200)
            else:
                return Response({'error': 'You are not assigned to this delivery.'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['get'], url_path='list_not_confirm')
    @is_confirmed
    def list_not_confirm(self, request):
        try:
            deliveries = DeliveryAssignment.objects.filter(confirm=False, volunteer=request.user,
                                                           delivery__is_active=True).all()

            if deliveries is None:
                return Response({'error': 'No deliveries found'}, status=400)

            serializer = DeliveryAssignmentSerializer(deliveries, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['get'], url_path='list_confirm')
    @is_confirmed
    def list_confirm(self, request):
        try:
            deliveries = DeliveryAssignment.objects.filter(confirm=True, delivery__curator=request.user,
                                                           delivery__is_active=True).all()

            if deliveries is None:
                return Response({'error': 'No deliveries found'}, status=400)

            serializer = DeliveryAssignmentSerializer(deliveries, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'], url_path='complete')
    @is_confirmed
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

                delivery.save(update_fields=['is_completed', 'in_execution', 'is_active', 'is_free'])

                return Response({'message': 'Delivery completed successfully'}, status=200)

    @action(detail=True, methods=['post'], url_path='delivery_activation')
    @is_confirmed
    def delivery_activation(self, request, pk):
        try:
            delivery = self.get_object()
            if self.request.user != delivery.curator:
                return Response({'error': 'You are not authorized to activate this delivery'}, status=403)
            if delivery.in_execution is True:
                return Response({'error': 'Delivery is already in execution'}, status=400)
            else:
                delivery.in_execution = True
                delivery.save(update_fields=['in_execution'])
                return Response({'message': 'Delivery is in execution'}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
