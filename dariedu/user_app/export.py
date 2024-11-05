from django.contrib.auth import get_user_model

from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateWidget

from task_app.models import Delivery, DeliveryAssignment, Task
from feedback_app.models import RequestMessage, Feedback


User = get_user_model()


class CombineResource(resources.ModelResource):
    rating = Field(attribute='rating', column_name='Уровень')
    volunteer_hour = Field(attribute='volunteer_hour', column_name='Волонтёрский часов за всё время')
    point = Field(attribute='point', column_name='Баллов на счету')
    last_name = Field(attribute='last_name', column_name='Фамилия')
    name = Field(attribute='name', column_name='Имя')
    surname = Field(attribute='surname', column_name='Отчество')
    tg_id = Field(attribute='tg_id', column_name='Telegram ID')
    city = Field(attribute='city', column_name='Город проживания')
    birthday = Field(attribute='birthday', column_name='Дата рождения', widget=DateWidget(format='%d.%m.%Y'))
    tg_username = Field(attribute='tg_username', column_name='Имя пользователя в Telegram ')
    phone = Field(attribute='phone', column_name='Номер телефона')
    email = Field(attribute='email', column_name='Электронная почта')
    metier = Field(attribute='metier', dehydrate_method='clean_status', column_name='Род деятельности')
    interests = Field(attribute='interests', column_name='Хобби')
    handling = Field(attribute='handling', column_name='Обращение из профиля пользователя (общая) ')
    deliveries = Field(attribute='deliveries', column_name='История доставок (дата, время и метро)')
    tasks = Field(attribute='tasks', column_name='История добрых дел')
    request = Field(attribute='request', column_name='Заявка на кураторство')

    def dehydrate_deliveries(self, user):
        delivery_data = []
        assignments = DeliveryAssignment.objects.filter(volunteer=user)
        print(assignments)
        for assignment in assignments:
            delivery = assignment.delivery  # This should be a single Delivery instance
            delivery_info = f'{delivery.date.strftime("%d.%m.%Y %H:%M")} - {delivery.location.subway}; '
            print(delivery_info)
            delivery_data.append(delivery_info)
        return '\n'.join(delivery_data) if delivery_data else "Нет доставок"

    def dehydrate_tasks(self, user):
        task_data = []
        tasks = Task.objects.filter(volunteers=user)
        for task in tasks:
            task_info = f'{task.name} - {task.end_date.strftime("%d.%m.%Y %H:%M")}; '
            task_data.append(task_info)
        return '\n'.join(task_data) if task_data else "Нет задач"

    def dehydrate_request(self, user):
        requests_data = []
        requests = RequestMessage.objects.filter(user=user)
        for request in requests:
            request_info = f'{request.date.strftime("%d.%m.%Y")} - {request.type}; '
            requests_data.append(request_info)
        return '\n'.join(requests_data) if requests_data else "Нет заявок"

    def dehydrate_handling(self, user):
        handling_data = []
        handling = Feedback.objects.filter(user=user)
        for feedback in handling:
            handling_info = f'{feedback.created_at.strftime("%d.%m.%Y")} : {feedback.text};   '
            handling_data.append(handling_info)
        return '\n'.join(handling_data) if handling_data else "Нет обращений"

    class Meta:
        model = User
        fields = ('rating', 'volunteer_hour', 'point', 'last_name', 'name', 'surname', 'tg_id', 'city', 'birthday',
                  'tg_username', 'phone', 'email', 'metier', 'interests', 'handling', 'deliveries', 'tasks', 'request')
        export_order = fields
