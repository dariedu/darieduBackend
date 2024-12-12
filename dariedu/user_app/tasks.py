import os
from celery import shared_task
import subprocess
from datetime import datetime, timedelta
import time
from gspread.exceptions import GSpreadException
from django.core.cache import cache
from requests.exceptions import SSLError

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
    user = User.objects.get(id=user_id)

    data_to_append = [{
        'Рейтинг': user.rating.level if user.rating else '',
        'Волонтёрский часов за всё время': user.volunteer_hour,
        'Баллов на счету': user.point,
        'Фамилия': user.last_name if user.last_name else '',
        'Имя': user.name if user.name else '',
        'Отчество': user.surname if user.surname else '',
        'Telegram ID': user.tg_id,
        'Город проживания': user.city.city if user.city else '',
        'Дата рождения': user.birthday.strftime('%d.%m.%Y') if user.birthday else '',
        'Никнэйм': user.tg_username if user.tg_username else '',
        'Номер телефона': user.phone if user.phone else '',
        'Электронная почта': user.email if user.email else '',
        'Род деятельности': dict(METIERS).get(user.metier, '') if user.metier else '',
        'Интересы': user.interests if user.interests else 'Нет интересов',
    }]

    if data_to_append:
        first_row_values = cache.get(settings.FIRST_ROW_VALUES_CACHE_KEY)
        print("First row values is from cache:", first_row_values)
        if first_row_values is None:
            first_row_values = worksheet.row_values(1)
            print("First row values is from worksheet:", first_row_values)
            cache.set(settings.FIRST_ROW_VALUES_CACHE_KEY, first_row_values,
                      timeout=int(timedelta(days=1).total_seconds()))

        empty_row_index = len(worksheet.get_all_records()) + 1
        data_to_append_list = [[row.get(key, '') for key in first_row_values] for row in data_to_append]

        print("Data to append:", data_to_append)
        print("Data to append list:", data_to_append_list)
        print("Empty row index:", empty_row_index)

        try:
            worksheet.append_rows(data_to_append_list, table_range=f'A{empty_row_index}')
        except Exception as e:
            print("Error while appending rows:", e)


@shared_task
def update_google_sheet(user_id):
    first_row_values = cache.get(settings.FIRST_ROW_VALUES_CACHE_KEY)
    if first_row_values is None:
        first_row_values = worksheet.row_values(1)
        cache.set(settings.FIRST_ROW_VALUES_CACHE_KEY, first_row_values, timeout=int(timedelta(days=1).total_seconds()))

    existing_datas = None
    retries = 3
    for attempt in range(retries):
        try:
            existing_datas = worksheet.get_all_records()
            break
        except SSLError as e:
            print(f"Attempt {attempt + 1} failed with SSLError: {e}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                raise

    user = User.objects.get(id=user_id)
    tg_id = user.tg_id
    user_row_index = None
    for index, row in enumerate(existing_datas):
        if row.get('Telegram ID') == tg_id:
            user_row_index = index + 2
            break

    user_data = [
        user.rating.level if user.rating else '',
        user.volunteer_hour,
        user.point,
        user.last_name,
        user.name,
        user.surname,
        user.tg_id,
        user.city.city if user.city else '',
        user.birthday.strftime('%d.%m.%Y') if user.birthday else '',
        user.tg_username,
        user.phone,
        user.email,
        dict(METIERS).get(user.metier, ''),
        user.interests if user.interests else 'Нет интересов'
    ]

    if user_row_index is not None:
        try:
            worksheet.update(f'A{user_row_index}:N{user_row_index}', [user_data])
        except GSpreadException as e:
            if e.response.status_code == 429:
                print("Quota exceeded, retrying after a delay")
                time.sleep(60)
                update_google_sheet(user_id)
            else:
                raise
    else:
        empty_row_index = len(existing_datas) + 2
        worksheet.update(f'A{empty_row_index}:N{empty_row_index}', [user_data])


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


@shared_task
def delete_cached_gsheets():
    cache.delete(settings.FIRST_ROW_VALUES_CACHE_KEY)
    time.sleep(1)
    cache.delete(settings.FIRST_ROW_VALUES_CACHE_KEY_2)
    time.sleep(1)
    cache.delete(settings.FIRST_ROW_VALUES_CACHE_KEY_3)
    time.sleep(1)
    cache.delete(settings.FIRST_ROW_VALUES_CACHE_KEY_4)


@shared_task
def update_ratings():
    users = User.objects.all()
    for user in users:
        user.update_rating()
        user.save(update_fields=['rating'])
