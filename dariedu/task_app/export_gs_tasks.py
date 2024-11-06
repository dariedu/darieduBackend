import logging
import os
from celery import shared_task
import requests
import pytz

from dariedu.gspread_config import gs
from .models import Delivery, Task
from user_app.models import User


gc = gs
spreadsheet_url = os.getenv('SPREADSHEET_URL')
spreadsheet = gc.open_by_url(spreadsheet_url)
worksheet_name = os.getenv('WORKSHEET_NAME')
worksheet = spreadsheet.worksheet(worksheet_name)
worksheet_name_3 = os.getenv('WORKSHEET_NAME3')
worksheet3 = spreadsheet.worksheet(worksheet_name_3)
worksheet_name_2 = os.getenv('WORKSHEET_NAME2')
worksheet2 = spreadsheet.worksheet(worksheet_name_2)


@shared_task
def export_to_google_tasks(user_id, task_id):
    user = User.objects.get(id=user_id)
    tg_username = user.tg_username
    tg_id = user.tg_id
    task_name = Task.objects.get(id=task_id).name
    task_date = Task.objects.get(id=task_id).end_date.strftime('%Y-%m-%d')
    first_row_values = worksheet.row_values(1)
    values_list = worksheet3.row_values(1)
    if tg_username in values_list:
        tg_username_index = values_list.index(
            tg_username) + 1
        first_empty_row = next(
            (i for i, row in enumerate(worksheet3.get_all_values()) if row[tg_username_index - 1] == ''), None)
        if first_empty_row is None:
            worksheet3.append_row([None] * tg_username_index)
            first_empty_row = len(worksheet3.get_all_values())
        current_value = worksheet3.cell(first_empty_row + 1, tg_username_index).value
        new_value = f"{current_value}, '{task_name}' {task_date}" if current_value else f"'{task_name}' {task_date}"
        worksheet3.update_cell(first_empty_row + 1, tg_username_index, new_value)
    else:
        next_column = len(values_list) + 1
        worksheet3.update_cell(1, next_column, tg_username)
        worksheet3.append_row([None] * next_column)
        worksheet3.update_cell(2, next_column,
                               f"'{task_name}' {task_date}")
        spreadsheet_id = spreadsheet.id
        worksheet_id = worksheet3.id
        cell_address = f"{chr(65 + (next_column - 1))}1"
        cell_link = (f"https://docs.google.com/spreadsheets/d/"
                     f"{spreadsheet_id}/edit#gid={worksheet_id}&range={cell_address}")
        existing_datas = worksheet.get_all_records()
        column_mapping = {header: index + 1 for index, header in enumerate(first_row_values)}
        user_row_index = None
        for index, row in enumerate(existing_datas):
            if row.get('Telegram ID') == tg_id:
                user_row_index = index + 2
                break
        if user_row_index is not None:
            worksheet.update_cell(user_row_index, column_mapping['История добрых дел'], cell_link)

@shared_task
def cancel_task_in_google_tasks(user_id, task_id):
    user = User.objects.get(id=user_id)
    tg_username = user.tg_username
    task_name = Task.objects.get(id=task_id).name
    task_date = Task.objects.get(id=task_id).end_date.strftime('%Y-%m-%d')
    name = f"{task_name} {task_date}"
    try:
        values_list = worksheet3.row_values(1)
    except requests.exceptions.SSLError as e:
        logging.error(f"SSL error occurred: {e}")
        return

    if tg_username in values_list:
        tg_username_index = values_list.index(tg_username) + 1
        task_row_index = None
        for i, row in enumerate(worksheet3.get_all_values()):
            if row[tg_username_index - 1] == name:
                task_row_index = i + 1
                break

        if task_row_index is not None:
            current_value = worksheet3.cell(task_row_index, tg_username_index).value
            new_value = f"{current_value}, (отменил)" if current_value else "(отменил)"
            worksheet3.update_cell(task_row_index, tg_username_index, new_value)
        else:
            logging.warning(f"Задача '{task_name}' не найдена для пользователя '{tg_username}'.")
    else:
        logging.warning(f"Пользователь '{tg_username}' не найден в заголовках.")


@shared_task
def export_to_google_delivery(user_id, delivery_id):
    user = User.objects.get(id=user_id)
    tg_username = user.tg_username
    tg_id = user.tg_id
    moscow_tz = pytz.timezone('Europe/Moscow')
    local_time = Delivery.objects.get(id=delivery_id).date.astimezone(moscow_tz)
    date_str = local_time.strftime('%Y-%m-%d')
    time_str = local_time.strftime('%H:%M')
    subway = Delivery.objects.get(id=delivery_id).location.subway

    first_row_values = worksheet.row_values(1)
    values_list = worksheet2.row_values(1)

    if tg_username in values_list:
        tg_username_index = values_list.index(
            tg_username) + 1
        first_empty_row = next(
            (i for i, row in enumerate(worksheet2.get_all_values()) if row[tg_username_index - 1] == ''), None)

        if first_empty_row is None:
            worksheet2.append_row([None] * tg_username_index)
            first_empty_row = len(worksheet2.get_all_values())

        current_value = worksheet2.cell(first_empty_row + 1, tg_username_index).value
        new_value = f"{current_value}, {date_str}, {time_str}, '{subway}'" \
            if current_value else f"'{date_str}, {time_str}, '{subway}'"

        worksheet2.update_cell(first_empty_row + 1, tg_username_index, new_value)
    else:
        next_column = len(values_list) + 1
        worksheet2.update_cell(1, next_column, tg_username)
        worksheet2.append_row([None] * next_column)
        worksheet2.update_cell(2, next_column,
                               f"{date_str}, {time_str}, '{subway}'")
        spreadsheet_id = spreadsheet.id
        worksheet_id = worksheet2.id
        cell_address = f"{chr(65 + (next_column - 1))}1"
        cell_link = (f"https://docs.google.com/spreadsheets/d/"
                     f"{spreadsheet_id}/edit#gid={worksheet_id}&range={cell_address}")
        existing_datas = worksheet.get_all_records()
        column_mapping = {header: index + 1 for index, header in enumerate(first_row_values)}
        user_row_index = None
        for index, row in enumerate(existing_datas):
            if row.get('Telegram ID') == tg_id:
                user_row_index = index + 2
                break
        if user_row_index is not None:
            worksheet.update_cell(user_row_index, column_mapping['История доставок '], cell_link)


@shared_task
def cancel_task_in_google_delivery(user_id, delivery_id):
    user = User.objects.get(id=user_id)
    tg_username = user.tg_username
    date_str = Delivery.objects.get(id=delivery_id).date.strftime('%Y-%m-%d')
    time_str = Delivery.objects.get(id=delivery_id).date.strftime('%H:%M')
    subway = Delivery.objects.get(id=delivery_id).location.subway
    list_data = f"{date_str}, {time_str}, '{subway}'"

    try:
        values_list = worksheet2.row_values(1)
    except requests.exceptions.SSLError as e:
        logging.error(f"SSL error occurred: {e}")
        return

    if tg_username in values_list:
        tg_username_index = values_list.index(tg_username) + 1
        task_row_index = None
        for i, row in enumerate(worksheet2.get_all_values()):
            if row[tg_username_index - 1] == list_data:
                task_row_index = i + 1
                break

        if task_row_index is not None:
            current_value = worksheet2.cell(task_row_index, tg_username_index).value
            new_value = f"{current_value}, (отменил)" if current_value else "(отменил)"
            worksheet2.update_cell(task_row_index, tg_username_index, new_value)
        else:
            logging.warning(f"Доставка '{list_data}' не найдена для пользователя '{tg_username}'.")
    else:
        logging.warning(f"Пользователь '{tg_username}' не найден в заголовках.")
