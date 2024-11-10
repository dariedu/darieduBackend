import os
from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings
from django.core.cache import cache

from dariedu.gspread_config import gs
from .models import RequestMessage, Feedback
from user_app.models import User


gc = gs
spreadsheet_url = os.getenv('SPREADSHEET_URL')
spreadsheet = gc.open_by_url(spreadsheet_url)
worksheet_name = os.getenv('WORKSHEET_NAME')
worksheet = spreadsheet.worksheet(worksheet_name)
worksheet_name_4 = os.getenv('WORKSHEET_NAME4')
worksheet4 = spreadsheet.worksheet(worksheet_name_4)

@shared_task
def export_to_google_feedback_user(feedback_id, user_id):
    feedback = Feedback.objects.get(id=feedback_id)
    type_mapping = dict(Feedback.TYPE_CHOICES)
    typ = type_mapping.get(feedback.type, '')
    text = feedback.text
    created_at = feedback.created_at
    data_str = created_at.strftime('%d.%m.%Y')
    time_str = created_at.strftime('%H:%M')
    tg_id = User.objects.get(id=user_id).tg_id
    tg_username = User.objects.get(id=user_id).tg_username
    last_name = User.objects.get(id=user_id).last_name
    name = User.objects.get(id=user_id).name[0]
    surname = User.objects.get(id=user_id).surname[0]
    data_user = f"{last_name} {name}.{surname}. ({tg_username})"

    values_list = cache.get(settings.FIRST_ROW_VALUES_CACHE_KEY_4)
    if values_list is None:
        values_list = worksheet4.row_values(1)
        cache.set(settings.FIRST_ROW_VALUES_CACHE_KEY_4, values_list,
                  timeout=int(timedelta(days=1).total_seconds()))

    if data_user in values_list:
        tg_username_index = values_list.index(
            data_user) + 1
        first_empty_row = next(
            (i for i, row in enumerate(worksheet4.get_all_values()) if row[tg_username_index - 1] == ''), None)
        if first_empty_row is None:
            worksheet4.append_row([None] * tg_username_index)
            first_empty_row = len(worksheet4.get_all_values())
        current_value = worksheet4.cell(first_empty_row + 1, tg_username_index).value
        new_value = f"{current_value}, {typ}: '{text}',  {data_str} {time_str}" \
            if current_value else f"{typ}: '{text}',  {data_str} {time_str}"
        worksheet4.update_cell(first_empty_row + 1, tg_username_index, new_value)
    else:
        next_column = len(values_list) + 1
        worksheet4.update_cell(1, next_column, data_user)
        worksheet4.append_row([None] * next_column)
        worksheet4.update_cell(2, next_column,
                               f"{typ}: '{text}',  {data_str} {time_str}")
        spreadsheet_id = spreadsheet.id
        worksheet_id = worksheet4.id
        cell_address = f"{chr(65 + (next_column - 1))}1"
        cell_link = (f"https://docs.google.com/spreadsheets/d/"
                     f"{spreadsheet_id}/edit#gid={worksheet_id}&range={cell_address}")

        first_row_values = cache.get(settings.FIRST_ROW_VALUES_CACHE_KEY)

        if first_row_values is None:
            first_row_values = worksheet.row_values(1)
            cache.set(settings.FIRST_ROW_VALUES_CACHE_KEY, first_row_values,
                      timeout=int(timedelta(days=1).total_seconds()))

        existing_datas = worksheet.get_all_records()
        column_mapping = {header: index + 1 for index, header in enumerate(first_row_values)}
        user_row_index = None
        for index, row in enumerate(existing_datas):
            if row.get('Telegram ID') == tg_id:
                user_row_index = index + 2
                break
        if user_row_index is not None:
            worksheet.update_cell(user_row_index, column_mapping['Обратная связь'],
                                  cell_link)


@shared_task
def export_to_google_request_message(request_id, user_id):
    tg_id = User.objects.get(id=user_id).tg_id
    about_location = RequestMessage.objects.get(id=request_id).about_location
    about_presence = RequestMessage.objects.get(id=request_id).about_presence
    about_worktime = RequestMessage.objects.get(id=request_id).about_worktime
    date = RequestMessage.objects.get(id=request_id).date.strftime('%d.%m.%Y')

    existing_datas = worksheet.get_all_records()
    first_row_values = cache.get(settings.FIRST_ROW_VALUES_CACHE_KEY)

    if first_row_values is None:
        first_row_values = worksheet.row_values(1)
        cache.set(settings.FIRST_ROW_VALUES_CACHE_KEY, first_row_values,
                  timeout=int(timedelta(days=1).total_seconds()))

    column_mapping = {header: index + 1 for index, header in enumerate(first_row_values)}
    user_row_index = None
    for index, row in enumerate(existing_datas):
        if row.get('Telegram ID') == tg_id:
            user_row_index = index + 2
            break
    if user_row_index is not None:
        worksheet.update_cell(user_row_index, column_mapping['Заявка на кураторство'],
                              f'На какой локации: "{about_location}";  '
                              f'Присутствие: "{about_presence}";  '
                              f'График работы/учебы: "{about_worktime}";   Дата: {date}')
