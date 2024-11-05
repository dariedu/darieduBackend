from django.contrib.auth import get_user_model

from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, BooleanWidget, ForeignKeyWidget

from .models import Task, Delivery
from address_app.models import Location, RouteSheet, Address, Beneficiar
from feedback_app.models import Feedback, PhotoReport


User = get_user_model()


class CombinedResource(resources.ModelResource):
    category = Field(attribute='category', column_name='Категория доброго дела')
    name = Field(attribute='name', column_name='Название доброго дела')
    volunteer_price = Field(attribute='volunteer_price', column_name='Кол-во волонтёрских часов')
    description = Field(attribute='description', column_name='Описание доброго дела')
    start_date = Field(attribute='start_date', column_name='Дата начала', widget=DateTimeWidget(format='%d.%m.%Y'))
    start_time = Field(attribute='start_date', column_name='Время начала', widget=DateTimeWidget(format='%H:%M'))
    end_date = Field(attribute='end_date', column_name='Дата окончания', widget=DateTimeWidget(format='%d.%m.%Y'))
    end_time = Field(attribute='end_date', column_name='Время окончания', widget=DateTimeWidget(format='%H:%M'))
    volunteers_needed = Field(attribute='volunteers_needed', column_name='Сколько волонтёров требуется')
    volunteers_taken = Field(attribute='volunteers_taken', column_name='Сколько волонтёров записалось')
    is_active = Field(attribute='is_active', dehydrate_method='clean_status', column_name='Статус доброго дела',
                      widget=BooleanWidget())
    city = Field(attribute='city', column_name='Город')
    curator = Field(attribute='curator', column_name='Куратор')
    volunteers = Field(attribute='volunteers', column_name='Волонтёры')

    class Meta:
        model = Task
        fields = ('category', 'name', 'volunteer_price', 'description', 'start_date', 'start_time', 'end_date',
                  'end_time', 'volunteers_needed', 'volunteers_taken', 'is_active', 'city', 'curator', 'volunteers')
        export_order = fields

    def dehydrate_volunteers(self, task):
        return ', '.join([str(volunteer) for volunteer in task.volunteers.all()])

    def clean_status(self, task):
        if task.is_active:
            return 'Активная'
        return 'Завершена'


class CombinedResourceDelivery(resources.ModelResource):
    status = Field(attribute='status', column_name='Статус доставки')
    date = Field(attribute='date', column_name='Дата доставки', widget=DateTimeWidget(format='%d.%m.%Y'))
    date_time = Field(attribute='date_time', column_name='Время начала доставки', widget=DateTimeWidget(format='%H:%M'))
    city = Field(attribute='city', column_name='Город доставки', widget=ForeignKeyWidget(Location, 'city'))
    subway = Field(attribute='subway', column_name='Метро локации', widget=ForeignKeyWidget(Location, 'subway'))
    address = Field(attribute='address', column_name='Адрес локации', widget=ForeignKeyWidget(Location, 'address'))
    link = Field(attribute='link', column_name='Ссылка на локацию на карте', widget=ForeignKeyWidget(Location, 'link'))
    curator = Field(attribute='curator', column_name='Имя куратора локации в Telegram',
                    widget=ForeignKeyWidget(Location, 'curator'))
    price = Field(attribute='price', column_name='Кол-во волонтёрских часов')
    volunteers_needed = Field(attribute='volunteers_needed', column_name='Волонтёров требуется')
    volunteers_taken = Field(attribute='volunteers_taken', column_name='Волонтёров записалось')
    route = Field(attribute='route', column_name='Маршрут №', widget=ForeignKeyWidget(RouteSheet, 'name'))
    route_link = Field(attribute='route_link', column_name='Ссылка на маршрут на карте',
                       widget=ForeignKeyWidget(RouteSheet, 'map'))
    user = Field(attribute='user', column_name='ФИО благополучателя', widget=ForeignKeyWidget(Beneficiar, 'full_name'))
    address_user = Field(attribute='address_user', column_name='Адрес благополучателя',
                         widget=ForeignKeyWidget(Address, 'address'))
    phone_user = Field(attribute='phone_user', column_name='Телефон благополучателя')
    photo = Field(attribute='photo', column_name='Фотоотчёт', widget=ForeignKeyWidget(PhotoReport, 'photo'))
    comment = Field(attribute='comment', column_name='Комментарий от благополучателя',
                    widget=ForeignKeyWidget(Beneficiar, 'comment'))
    volunteer_link = Field(attribute='volunteer_link', column_name='Волонтер на маршруте', widget=ForeignKeyWidget(
        User, 'name'))
    volunteer_feedback = Field(attribute='volunteer_feedback', column_name='Обратная связь от волонтёра после доставки',
                               widget=ForeignKeyWidget(Feedback, 'delivery'))

    def dehydrate_status(self, delivery):
        if delivery.is_active:
            return 'Активная'
        if delivery.in_execution:
            return 'В работе'
        if delivery.is_active and delivery.in_execution:
            return 'Активная/В работе'
        return 'Завершена'

    def dehydrate_date_time(self, delivery):
        if delivery.date:
            return delivery.date.strftime('%H:%M')
        return ''

    def dehydrate_city(self, delivery):
        if delivery.location:
            return delivery.location.city.city
        return ''

    def dehydrate_subway(self, delivery):
        if delivery.location:
            return delivery.location.subway
        return ''

    def dehydrate_address(self, delivery):
        if delivery.location:
            return delivery.location.address
        return ''

    def dehydrate_link(self, delivery):
        if delivery.location:
            print(delivery.location.link)
            return delivery.location.link
        return ''

    def dehydrate_curator(self, delivery):
        if delivery.location:
            curator = delivery.location.curator
            if curator:
                return f'{curator.last_name} {curator.name}'
        return ''

    def dehydrate_route(self, delivery):
        if delivery.location:
            route = [route.name for route in delivery.location.route_sheets.all()]
            return route
        return ''

    def dehydrate_route_link(self, delivery):
        if delivery.location:
            maps = [route.map for route in delivery.location.route_sheets.all() if route.map]
            return ' ;  '.join(maps) if maps else 'Нет доступных карт'
        return ''

    def dehydrate_user(self, delivery):
        routes = delivery.location.route_sheets.all()
        beneficiaries_list = []
        for route in routes:
            addresses = route.address.all()
            for address in addresses:
                beneficiaries = address.beneficiar.all()  # Получаем благополучателей для каждого адреса
                beneficiaryes = [beneficiary.full_name for beneficiary in beneficiaries]
                beneficiaries_list.extend([str(beneficiary) for beneficiary in beneficiaryes])
        return '; '.join(beneficiaries_list) if beneficiaries_list else 'Нет благополучателей'

    def dehydrate_volunteer_link(self, delivery):
        if delivery.location.route_sheets:
            route = delivery.location.route_sheets.first()
            return f'{route.user.last_name} {route.user.name}'
        return ''

    def dehydrate_address_user(self, delivery):
        routes = delivery.location.route_sheets.all()
        address_list = []
        for route in routes:
            addresses = route.address.all()
            for address in addresses:
                beneficiaries = address.beneficiar.all()
                address_list.extend([str(beneficiary.address) for beneficiary in beneficiaries])
        return '; '.join(address_list) if address_list else 'Нет адресов'

    def dehydrate_phone_user(self, delivery):
        routes = delivery.location.route_sheets.all()
        phone_list = []
        for route in routes:
            addresses = route.address.all()
            for address in addresses:
                beneficiaries = address.beneficiar.all()
                phone_list.extend([str(beneficiary.phone) for beneficiary in beneficiaries])
        return '; '.join(phone_list) if phone_list else 'Нет телефонов'

    def dehydrate_volunteer_feedback(self, delivery):
        feedbacks = Feedback.objects.filter(delivery=delivery)
        if feedbacks:
            return '\n'.join([feedback.text for feedback in feedbacks])
        return 'not'

    def dehydrate_photo(self, delivery):
        photos = delivery.location.route_sheets.all()
        for route in photos:
            addresses = route.address.all()
            for address in addresses:
                photos = address.photoreport_set.all()
                photo = [photo.photo_view for photo in photos]
                if photo:
                    return 'Да'
        return 'Нет'

    def dehydrate_comment(self, delivery):
        routes = delivery.location.route_sheets.all()
        comment_list = []
        for route in routes:
            addresses = route.address.all()
            for address in addresses:
                beneficiaries = address.beneficiar.all()
                comment_list.extend([str(beneficiary.comment) for beneficiary in beneficiaries])
        return '; '.join(comment_list) if comment_list else 'Нет комментариев'

    class Meta:
        model = Delivery
        fields = ('status', 'date', 'date_time', 'city', 'subway', 'address', 'link', 'curator', 'price',
                  'volunteers_needed', 'volunteers_taken', 'route', 'route_link', 'user', 'address_user',
                  'phone_user', 'photo', 'comment', 'volunteer_link', 'volunteer_feedback')
        export_order = fields
