from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, BooleanWidget

from .models import Task, Delivery, User

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
    is_active = Field(attribute='is_active', dehydrate_method='clean_status', column_name='Статус доброго дела', widget=BooleanWidget())
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
