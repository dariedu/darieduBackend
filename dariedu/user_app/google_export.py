import os
from pprint import pprint
from django.contrib.admin.actions import action
import logging

from dariedu.gspread_config import gs
from task_app.models import Delivery, Task

logger = logging.getLogger('google.sheets')


def get_volunteer_deliveries(volunteer):
    try:
        deliveries = Delivery.objects.filter(assignments__volunteer=volunteer)
        return deliveries
    except Exception as e:
        logger.error(f"Error fetching volunteer's deliveries: {e}")
        return []

def get_volunteer_tasks(volunteer):
    try:
        tasks = Task.objects.filter(volunteers=volunteer)
        return tasks
    except Exception as e:
        logger.error(f"Error fetching volunteer's tasks: {e}")
        return []


def get_volunteer_info(volunteer):
    logger.info('get_volunteer_info')
    try:
        deliveries = get_volunteer_deliveries(volunteer)
        tasks = get_volunteer_tasks(volunteer)

        delivery_info = []
        for delivery in deliveries:
            delivery_info.append({
                'date': delivery.date.strftime('%Y-%m-%d %H:%M:%S'),
                'subway': ', '.join(delivery.location.subway.split(', ')),
            })

        task_info = []
        for task in tasks:
            task_info.append({
                'date': task.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                'name': task.name,
            })

        return {
            'deliveries': delivery_info,
            'tasks': task_info,
        }
    except Exception as e:
        logger.error(f"Error fetching volunteer's info: {e}")
        return {}


METIERS = (
    ('schoolchild', 'Школьник'),
    ('student', 'Студент'),
    ('work_on_himself', 'Работаю на себя'),
    ('work_for_hire', 'Работаю по найму'),
    ('pensioner', 'Пенсионер'),
    ('other', 'Другое'),
)


@action(description='Экспорт в Google')
def export_to_gs(modeladmin, request, queryset):
    logger.info('export_to_gs')
    try:
        try:
            users = queryset.all()
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return
        gc = gs
        spreadsheet_url = os.getenv('SPREADSHEET_URL_ACTION')
        spreadsheet = gc.open_by_url(spreadsheet_url)
        worksheet_name = os.getenv('WORKSHEET_NAME_ACTION')
        worksheet = spreadsheet.worksheet(worksheet_name)
        first_row_values = worksheet.row_values(1)
        existing_datas = worksheet.get_all_records()
        column_mapping = {header: index + 1 for index, header in enumerate(first_row_values)}
        existing_user_ids = [row.get('Telegram ID') for row in existing_datas if row]
        logger.info(f"Existing user IDs: {existing_user_ids}")
        data_to_append = []
        for u in users:
            existing_row_index = None
            for i, row in enumerate(existing_datas):
                if row.get('Telegram ID') == u.tg_id:
                    existing_row_index = i + 2
                    break

            if existing_row_index:
                existing_row_values = worksheet.row_values(existing_row_index)
                logger.info(f"Existing row values: {existing_row_values}")
                info = get_volunteer_info(volunteer=u)
                logger.info(f"Info: {info}")
                delivery_info = [f"{delivery['date']} {delivery['subway']}" for delivery in
                                 info['deliveries']]
                logger.info(f"Delivery info: {delivery_info}")
                task_info = [f"{task['date']} {task['name']}" for task in info['tasks']]
                logger.info(f"Task info: {task_info}")

                new_data = {
                    'Рейтинг': u.rating.level if u.rating else '',
                    'Волонтёрский часов за всё время': u.volunteer_hour,
                    'Баллов на счету': u.point,
                    'Фамилия': u.last_name,
                    'Имя': u.name,
                    'Отчество': u.surname,
                    'Telegram ID': u.tg_id,
                    'Город проживания': u.city.city if u.city else '',
                    'Дата рождения': u.birthday.strftime('%Y-%m-%d') if u.birthday else '',
                    'Никнэйм ': u.tg_username,
                    'Номер телефона': u.phone,
                    'Электронная почта': u.email,
                    'Род деятельности': dict(METIERS).get(u.metier, ''),
                    'Интересы': u.interests,
                    'История доставок (дата, время и метро)': ';  '.join(delivery_info),
                    'История добрых дел': ';  '.join(task_info),
                }

                for key, new_value in new_data.items():
                    if key in column_mapping:
                        try:
                            existing_value = existing_row_values[column_mapping[key] - 1]
                        except IndexError:
                            existing_value = None
                            logger.error(f"Column {key} does not exist in the worksheet.")
                        if new_value != existing_value:
                            worksheet.update_cell(existing_row_index, column_mapping[key], new_value)
                    else:
                        logger.error(f"Column {key} does not exist in the worksheet.")

                for key, new_value in new_data.items():
                    if key in column_mapping:
                        index = column_mapping[key] - 1
                        if index < len(existing_row_values):
                            existing_value = existing_row_values[index]
                            logger.info(f"Existing value: {existing_value}")
                        else:
                            existing_value = None
                            logger.error(f"Column {key} does not exist in the worksheet.")
                        if new_value != existing_value:
                            worksheet.update_cell(existing_row_index, column_mapping[key], new_value)
                            logger.info(f"Updated value: {new_value}")
                    else:
                        logger.error(f"Column {key} does not exist in the worksheet.")

            else:
                info = get_volunteer_info(volunteer=u)

                delivery_info = [f"{delivery['date']} {delivery['subway']}" for delivery in
                                 info['deliveries']]
                task_info = [f"{task['date']} {task['name']}" for task in info['tasks']]
                logger.info(f"Delivery info: {delivery_info}")
                logger.info(f"Task info: {task_info}")

                data_to_append.append({
                    'Рейтинг': u.rating.level if u.rating else '',
                    'Волонтёрский часов за всё время': u.volunteer_hour,
                    'Баллов на счету': u.point,
                    'Фамилия': u.last_name,
                    'Имя': u.name,
                    'Отчество': u.surname,
                    'Telegram ID': u.tg_id,
                    'Город проживания': u.city.city if u.city else '',
                    'Дата рождения': u.birthday.strftime('%Y-%m-%d') if u.birthday else '',
                    'Никнэйм ': u.tg_username,
                    'Номер телефона': u.phone,
                    'Электронная почта': u.email,
                    'Род деятельности': dict(METIERS).get(u.metier, ''),
                    'Интересы': u.interests,
                    'История доставок (дата, время и метро)': ', '.join(delivery_info),
                    'История добрых дел': ', '.join(task_info),
                })
                logger.info(f"Data to append: {data_to_append}")

        if data_to_append:
            empty_row_index = len(worksheet.get_all_records()) + 1
            data_to_append_list = [[row.get(key, '') for key in column_mapping.keys()] for row in data_to_append]
            logger.info(f"Data to append list: {data_to_append_list}")
            worksheet.append_rows(data_to_append_list, table_range=f'A{empty_row_index}')
            logger.info(f"Data appended to Google Sheets")

    except Exception as e:
        logger.error(f"Error exporting to Google Sheets: {e}")
