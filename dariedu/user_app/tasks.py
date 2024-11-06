import os
from pprint import pprint
from celery import shared_task
import subprocess
from datetime import datetime, timedelta

from dariedu.gspread_config import gs
from user_app.models import User
from django.conf import settings


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

@shared_task
def export_to_google(user_id):
    first_row_values = worksheet.row_values(1)
    user = User.objects.get(id=user_id)

    data_to_append = [{
        'Рейтинг': user.rating.level if user.rating else '',
        'Волонтёрский часов за всё время': user.volunteer_hour,
        'Баллов на счету': user.point,
        'Фамилия': user.last_name,
        'Имя': user.name,
        'Отчество': user.surname,
        'Telegram ID': user.tg_id,
        'Город проживания': user.city.city if user.city else '',
        'Дата рождения': user.birthday.strftime('%d.%m.%Y') if user.birthday else '',
        'Никнэйм': user.tg_username,
        'Номер телефона': user.phone,
        'Электронная почта': user.email,
        'Род деятельности': dict(METIERS).get(user.metier, ''),
        'Интересы': user.interests if user.interests else 'Нет интересов',
    }]

    if data_to_append:
        empty_row_index = len(worksheet.get_all_records()) + 1
        data_to_append_list = [[row.get(key, '') for key in first_row_values] for row in data_to_append]
        pprint(data_to_append_list)
        worksheet.append_rows(data_to_append_list, table_range=f'A{empty_row_index}')


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
                              user.birthday.strftime('%d.%m.%Y') if user.birthday else '')
        worksheet.update_cell(user_row_index, column_mapping['Никнэйм'], user.tg_username)
        worksheet.update_cell(user_row_index, column_mapping['Номер телефона'], user.phone)
        worksheet.update_cell(user_row_index, column_mapping['Электронная почта'], user.email)
        worksheet.update_cell(user_row_index, column_mapping['Род деятельности'], dict(METIERS).get(user.metier, ''))
        worksheet.update_cell(user_row_index, column_mapping['Интересы'],
                              user.interests if user.interests else 'Нет интересов')
    else:
        export_to_google.delay(user_id)


@shared_task
def backup_database():
    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_host = settings.DATABASES['default']['HOST']
    db_password = settings.DATABASES['default']['PASSWORD']
    backup_dir = settings.BACKUP_DIR

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f'Created backup directory: {backup_dir}')

    date = datetime.now().strftime('%Y%m%d%H%M')
    backup_file = os.path.join(backup_dir, f'backup_{date}.sql')
    os.environ['PGPASSWORD'] = db_password
    command = f'pg_dump -U {db_user} -h {db_host} -d {db_name} > {backup_file}'

    try:
        subprocess.run(command, shell=True, check=True)
        print(f'Successfully created backup: {backup_file}')
    except subprocess.CalledProcessError as e:
        print(f'Error occurred while creating backup: {e}')

    delete_old_backups(backup_dir)
    del os.environ['PGPASSWORD']


def delete_old_backups(backup_dir):
    expiration_time = datetime.now() - timedelta(days=7)

    for filename in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, filename)

        if os.path.isfile(file_path):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))

            if file_mod_time < expiration_time:
                os.remove(file_path)
                print(f'Deleted old backup: {file_path}')
