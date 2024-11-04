import os
from pprint import pprint
from celery import shared_task

from dariedu.gspread_config import gs
from task_app.models import Delivery, Task
from user_app.models import User


METIERS = (
    ('schoolchild', 'Школьник'),
    ('student', 'Студент'),
    ('work_on_himself', 'Работаю на себя'),
    ('work_for_hire', 'Работаю по найму'),
    ('pensioner', 'Пенсионер'),
    ('other', 'Другое'),
)

gc = gs
spreadsheet_url = os.getenv('SPREADSHEET_URL')
spreadsheet = gc.open_by_url(spreadsheet_url)
worksheet_name = os.getenv('WORKSHEET_NAME')
worksheet = spreadsheet.worksheet(worksheet_name)
worksheet_name_2 = os.getenv('WORKSHEET_NAME2')
worksheet2 = spreadsheet.worksheet(worksheet_name_2)
worksheet_name_3 = os.getenv('WORKSHEET_NAME3')
worksheet3 = spreadsheet.worksheet(worksheet_name_3)

@shared_task
def export_to_google(user_id):

    first_row_values = worksheet.row_values(1)

    user = User.objects.get(id=user_id)
    tg_username = user.tg_username

    link_delivery = worksheet_history_delivery(tg_username)

    link_task = worksheet_history_task(tg_username)

    data_to_append = [{
        'Рейтинг': user.rating.level if user.rating else '',
        'Волонтёрский часов за всё время': user.volunteer_hour,
        'Баллов на счету': user.point,
        'Фамилия': user.last_name,
        'Имя': user.name,
        'Отчество': user.surname,
        'Telegram ID': user.tg_id,
        'Город проживания': user.city.city if user.city else '',
        'Дата рождения': user.birthday.strftime('%Y-%m-%d') if user.birthday else '',
        'Никнэйм': user.tg_username,
        'Номер телефона': user.phone,
        'Электронная почта': user.email,
        'Род деятельности': dict(METIERS).get(user.metier, ''),
        'Интересы': user.interests if user.interests else 'Нет интересов',
        'История доставок ': link_delivery if link_delivery else 'Нет данных',
        'История добрых дел': link_task if link_task else 'Нет данных',
    }]

    if data_to_append:
        empty_row_index = len(worksheet.get_all_records()) + 1
        data_to_append_list = [[row.get(key, '') for key in first_row_values] for row in data_to_append]
        pprint(data_to_append_list)
        worksheet.append_rows(data_to_append_list, table_range=f'A{empty_row_index}')


def worksheet_history_delivery(tg_username):
    values_list = worksheet2.row_values(1)
    print('First row', values_list)
    first_empty_index = next((i for i, value in enumerate(values_list) if value == ''), None)

    if first_empty_index is None:
        next_column = len(values_list) + 1
        worksheet2.update_cell(1, next_column, tg_username)
    else:
        worksheet2.update_cell(1, first_empty_index + 1, tg_username)

    spreadsheet_id = spreadsheet.id
    worksheet_id = worksheet2.id
    cell_address = f"{chr(65 + (first_empty_index + 1 if first_empty_index is not None else len(values_list)))}1"
    cell_link = (f"https://docs.google.com/spreadsheets/d/"
                 f"{spreadsheet_id}/edit#gid={worksheet_id}&range={cell_address}")
    print("Ссылка на ячейку:", cell_link)
    return cell_link

def worksheet_history_task(tg_username):
    values_list = worksheet3.row_values(1)
    print('First row', values_list)
    first_empty_index = next((i for i, value in enumerate(values_list) if value == ''), None)

    if first_empty_index is None:
        next_column = len(values_list) + 1
        worksheet3.update_cell(1, next_column, tg_username)
    else:
        worksheet3.update_cell(1, first_empty_index + 1, tg_username)

    spreadsheet_id = spreadsheet.id
    worksheet_id = worksheet3.id
    cell_address = f"{chr(65 + (first_empty_index + 1 if first_empty_index is not None else len(values_list)))}1"
    cell_link = (f"https://docs.google.com/spreadsheets/d/"
                 f"{spreadsheet_id}/edit#gid={worksheet_id}&range={cell_address}")
    print("Ссылка на ячейку:", cell_link)
    return cell_link


@shared_task
def update_google_sheet(user_id):
    first_row_values = worksheet.row_values(1)
    existing_datas = worksheet.get_all_records()
    column_mapping = {header: index + 1 for index, header in enumerate(first_row_values)}

    user = User.objects.get(id=user_id)
    tg_id = user.tg_id
    print('tg_id', tg_id)
    user_row_index = None
    for index, row in enumerate(existing_datas):
        if row.get('Telegram ID') == tg_id:
            user_row_index = index + 2
            break

    if user_row_index is not None:
        worksheet.update_cell(user_row_index, column_mapping['Рейтинг'], user.rating.level if user.rating else '')
        worksheet.update_cell(user_row_index, column_mapping['Волонтёрский часов за всё время'], user.volunteer_hour)
        worksheet.update_cell(user_row_index, column_mapping['Баллов на счету'], user.point)
        worksheet.update_cell(user_row_index, column_mapping['Фамилия'], user.last_name)
        worksheet.update_cell(user_row_index, column_mapping['Имя'], user.name)
        worksheet.update_cell(user_row_index, column_mapping['Отчество'], user.surname)
        worksheet.update_cell(user_row_index, column_mapping['Telegram ID'], user.tg_id)
        worksheet.update_cell(user_row_index, column_mapping['Город проживания'], user.city.city if user.city else '')
        worksheet.update_cell(user_row_index, column_mapping['Дата рождения'],
                              user.birthday.strftime('%Y-%m-%d') if user.birthday else '')
        worksheet.update_cell(user_row_index, column_mapping['Никнэйм'], user.tg_username)
        worksheet.update_cell(user_row_index, column_mapping['Номер телефона'], user.phone)
        worksheet.update_cell(user_row_index, column_mapping['Электронная почта'], user.email)
        worksheet.update_cell(user_row_index, column_mapping['Род деятельности'], dict(METIERS).get(user.metier, ''))
        worksheet.update_cell(user_row_index, column_mapping['Интересы'],
                              user.interests if user.interests else 'Нет интересов')
    else:
        export_to_google.delay(user_id)
