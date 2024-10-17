from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, ForeignKeyWidget, ManyToManyWidget

from .models import User, PromoCategory
from feedback_app.models import RequestMessage, Feedback


class CombineResourcePromo(resources.ModelResource):
    period = Field(attribute='period', column_name='Срок применения')
    start_date = Field(attribute='start_date', column_name='Дата начала', widget=DateTimeWidget(format='%d.%m.%Y'))
    start_time = Field(attribute='start_time', column_name='Время начала', widget=DateTimeWidget(format='%H:%M'))
    end_date = Field(attribute='end_date', column_name='Дата окончания', widget=DateTimeWidget(format='%d.%m.%Y'))
    end_time = Field(attribute='end_time', column_name='Время окончания', widget=DateTimeWidget(format='%H:%M'))
    is_active = Field(attribute='is_active', column_name='Статус')
    category = Field(attribute='category', column_name='Категория', widget=ForeignKeyWidget(PromoCategory, 'name'))
    city = Field(attribute='city', column_name='Город применения')
    name = Field(attribute='name', column_name='Название')
    description = Field(attribute='description', column_name='Описание')
    ticket_file = Field(attribute='ticket_file', column_name='Файл')
    for_curators_only = Field(attribute='for_curators_only', column_name='Доступно')
    price = Field(attribute='price', column_name=' «Стоимость» в баллах')
    quantity = Field(attribute='quantity', column_name='Общее количество')
    users = Field(attribute='users', column_name='Имя пользователя, воспользовавшегося поощрением',
                  widget=ManyToManyWidget(User, separator=', '))
    request = Field(attribute='request', column_name='Обратная связь от пользователя после использования поощрения')

    def dehydrate_start_time(self, promo):
        start_time = promo.start_date.time()
        return start_time.strftime('%H:%M')

    def dehydrate_end_time(self, promo):
        if promo.end_date is None:
            return ''
        end_time = promo.end_date.time()
        return end_time.strftime('%H:%M')

    def dehydrate_period(self, promo):
        if promo.is_permanent:
            return 'Бессрочное'
        return 'Срочное'

    def dehydrate_is_active(self, promo):
        if promo.is_active:
            return 'Доступно'
        return 'Завершено'

    def dehydrate_for_curators_only(self, promo):
        if promo.for_curators_only:
            return 'Всем, кроме волонтёров'
        return 'Всем'

    def dehydrate_users(self, promo):
        return ', '.join([f"{user.last_name} {user.name}" for user in promo.users.all()])

    def dehydrate_request(self, promo):
        feedback_data = []
        feedbacks = Feedback.objects.filter(promotion=promo)
        for feedback in feedbacks:
            feedback_info = f'{feedback.user.last_name} {feedback.user.name} - {feedback.text}; '
            feedback_data.append(feedback_info)
        return '\n'.join(feedback_data) if feedback_data else "Нет обратной связи"

    class Meta:
        model = User
        fields = ('period', 'start_date', 'start_time', 'end_date', 'end_time', 'is_active', 'category', 'city',
                  'name', 'description', 'ticket_file', 'for_curators_only', 'price', 'quantity', 'users', 'request')
        export_order = fields
