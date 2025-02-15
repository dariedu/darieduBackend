from django.contrib.auth import get_user_model
import logging
from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, BooleanWidget, ForeignKeyWidget

from .models import Task, Delivery
from address_app.models import Location, RouteSheet, Address, Beneficiar, RouteAssignment
from feedback_app.models import Feedback, PhotoReport


User = get_user_model()

logger = logging.getLogger('google.sheets')


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
        logger.info(f'Volunteers: {task.volunteers.all()}')
        try:
            return ', '.join([str(volunteer) for volunteer in task.volunteers.all()])
        except Exception as e:
            logger.error(f'Error fetching volunteers: {e}')
            return ''

    def clean_status(self, task):
        logger.info(f'Status: {task.is_active}')
        try:
            if task.is_active:
                return 'Активная'
            return 'Завершена'
        except Exception as e:
            logger.error(f'Error fetching status: {e}')
            return ''


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
        logger.info(f'Status: {delivery.is_active} {delivery.in_execution}')
        try:
            if delivery.is_active:
                return 'Активная'
            if delivery.in_execution:
                return 'В работе'
            if delivery.is_active and delivery.in_execution:
                return 'Активная/В работе'
            return 'Завершена'
        except Exception as e:
            logger.error(f'Error fetching status: {e}')
            return ''

    def dehydrate_date_time(self, delivery):
        logger.info(f'Date: {delivery.date}')
        try:
            if delivery.date:
                return delivery.date.strftime('%H:%M')
            return ''
        except Exception as e:
            logger.error(f'Error fetching date: {e}')
            return ''

    def dehydrate_city(self, delivery):
        logger.info(f'City: {delivery.location}')
        try:
            if delivery.location:
                return delivery.location.city.city
            return ''
        except Exception as e:
            logger.error(f'Error fetching city: {e}')
            return ''

    def dehydrate_subway(self, delivery):
        logger.info(f'Subway: {delivery.location}')
        try:
            if delivery.location:
                return delivery.location.subway
            return ''
        except Exception as e:
            logger.error(f'Error fetching subway: {e}')

    def dehydrate_address(self, delivery):
        logger.info(f'Address: {delivery.location}')
        try:
            if delivery.location:
                return delivery.location.address
            return ''
        except Exception as e:
            logger.error(f'Error fetching address: {e}')

    def dehydrate_link(self, delivery):
        logger.info(f'Link: {delivery.location}')
        try:
            if delivery.location:
                print(delivery.location.link)
                return delivery.location.link
            return ''
        except Exception as e:
            logger.error(f'Error fetching link: {e}')

    def dehydrate_curator(self, delivery):
        logger.info(f'Curator: {delivery.location}')
        try:
            if delivery.location:
                curator = delivery.location.curator
                if curator:
                    return f'{curator.last_name} {curator.name}'
            return ''
        except Exception as e:
            logger.error(f'Error fetching curator: {e}')

    def dehydrate_route(self, delivery):
        logger.info(f'Route: {delivery.location}')
        try:
            if delivery.location:
                route = [route.name for route in delivery.location.route_sheets.all()]
                return '; '.join(route) if route else ''
            return ''
        except Exception as e:
            logger.error(f'Error fetching route: {e}')

    def dehydrate_route_link(self, delivery):
        logger.info(f'Route link: {delivery.location}')
        try:
            if delivery.location:
                maps = [route.map for route in delivery.location.route_sheets.all() if route.map]
                return ' ;  '.join(maps) if maps else 'Нет доступных карт'
            return ''
        except Exception as e:
            logger.error(f'Error fetching route link: {e}')

    def dehydrate_user(self, delivery):
        logger.info(f'User: {delivery.location}')
        try:
            routes = delivery.location.route_sheets.all()
            logger.debug(f'Routes: {routes}')

            beneficiaries_list = []
            for route in routes:
                addresses = route.address.all()
                for address in addresses:
                    beneficiaries = address.beneficiar.all()  # Получаем благополучателей для каждого адреса
                    beneficiaryes = [beneficiary.full_name for beneficiary in beneficiaries]
                    beneficiaries_list.extend([str(beneficiary) for beneficiary in beneficiaryes])
                    logger.debug(f'Beneficiaries: {beneficiaryes}')
            return '; '.join(beneficiaries_list) if beneficiaries_list else 'Нет благополучателей'
        except Exception as e:
            logger.error(f'Error fetching user: {e}')

    def dehydrate_volunteer_link(self, delivery):
        logger.info(f'Volunteer link: {delivery.location}')
        try:
            if delivery.route_sheet:
                try:
                    route_assignment = (RouteAssignment.objects.filter(delivery=delivery).values_list
                                        ('volunteer', flat=True).distinct())
                    return '; '.join([str(User.objects.get(id=user)) for user in route_assignment])
                except Exception as e:
                    logger.error(f'Error fetching route assignment: {e}')
            return ''
        except Exception as e:
            logger.error(f'Error fetching volunteer link: {e}')

    def dehydrate_address_user(self, delivery):
        logger.info(f'Address user: {delivery.location}')
        try:
            routes = delivery.location.route_sheets.all()
            logger.debug(f'Routes: {routes}')

            address_list = []
            for route in routes:
                addresses = route.address.all()
                for address in addresses:
                    beneficiaries = address.beneficiar.all()
                    logger.debug(f'Beneficiaries: {beneficiaries}')
                    address_list.extend([str(beneficiary.address) for beneficiary in beneficiaries])
            return '; '.join(address_list) if address_list else 'Нет адресов'
        except Exception as e:
            logger.error(f'Error fetching address user: {e}')

    def dehydrate_phone_user(self, delivery):
        logger.info(f'Phone user: {delivery.location}')
        try:
            routes = delivery.location.route_sheets.all()
            logger.debug(f'Routes: {routes}')
            phone_list = []
            for route in routes:
                addresses = route.address.all()
                logger.debug(f'Addresses: {addresses}')
                for address in addresses:
                    beneficiaries = address.beneficiar.all()
                    logger.debug(f'Beneficiaries: {beneficiaries}')
                    phone_list.extend([str(beneficiary.phone) for beneficiary in beneficiaries])
            return '; '.join(phone_list) if phone_list else 'Нет телефонов'
        except Exception as e:
            logger.error(f'Error fetching phone user: {e}')

    def dehydrate_volunteer_feedback(self, delivery):
        logger.info(f'Volunteer feedback: {delivery.location}')
        try:
            feedbacks = Feedback.objects.filter(delivery=delivery)
            if feedbacks:
                return '\n'.join([feedback.text for feedback in feedbacks])
            return 'not'
        except Exception as e:
            logger.error(f'Error fetching volunteer feedback: {e}')

    def dehydrate_photo(self, delivery):
        logger.info(f'Photo: {delivery.location}')
        try:
            photos = delivery.location.route_sheets.all()
            logger.debug(f'Photos: {photos}')
            for route in photos:
                addresses = route.address.all()
                for address in addresses:
                    photos = address.photoreport_set.all()
                    photo = [photo.photo_view for photo in photos]
                    logger.debug(f'Photo: {photo}')
                    if photo:
                        return 'Да'
            return 'Нет'
        except Exception as e:
            logger.error(f'Error fetching photo: {e}')

    def dehydrate_comment(self, delivery):
        logger.info(f'Comment: {delivery.location}')
        try:
            routes = delivery.location.route_sheets.all()
            logger.debug(f'Routes: {routes}')
            comment_list = []
            for route in routes:
                addresses = route.address.all()
                logger.debug(f'Addresses: {addresses}')
                for address in addresses:
                    beneficiaries = address.beneficiar.all()
                    logger.debug(f'Beneficiaries: {beneficiaries}')
                    comment_list.extend([str(beneficiary.comment) for beneficiary in beneficiaries])
            return '; '.join(comment_list) if comment_list else 'Нет комментариев'
        except Exception as e:
            logger.error(f'Error fetching comment: {e}')

    class Meta:
        model = Delivery
        fields = ('status', 'date', 'date_time', 'city', 'subway', 'address', 'link', 'curator', 'price',
                  'volunteers_needed', 'volunteers_taken', 'route', 'route_link', 'user', 'address_user',
                  'phone_user', 'photo', 'comment', 'volunteer_link', 'volunteer_feedback')
        export_order = fields
