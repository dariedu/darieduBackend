import datetime

from typing import Any

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from django.core.files import File


def authenticate() -> GoogleAuth:
    """Не интерактивная авторизация в Google"""
    google_auth = GoogleAuth()
    google_auth.LoadCredentialsFile('token.json')

    return google_auth


def upload_file_to_google_drive(file: File) -> Any:
    """Загрузка файлов в GoogleDrive"""
    try:
        drive = GoogleDrive(authenticate())

        today = str(datetime.date.today())

        query = f'title="{today}" and mimeType="application/vnd.google-apps.folder" and trashed=false'
        lists_folder = drive.ListFile({'q': query}).GetList()

        if not lists_folder:
            folder_metadata = {
                'title': f'{today}',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive.CreateFile(folder_metadata)
            folder.Upload()
            lists_folder.append(folder)

        folder_id = lists_folder[0]['id']

        file_drive = drive.CreateFile({'title': f'{file.name}', 'parents': [{'id': folder_id}]})
        file_drive.SetContentFile(f'photo_report/{file}')
        file_drive.Upload()
        file_drive.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })
        return file_drive
    except Exception as e:
        return f'Exception - {e}'


def get_google_links(file: File):
    """Получение ссылок для показа и скачивании фотографии"""
    uploaded = upload_file_to_google_drive(file)

    result = {
        'view': uploaded.get('embedLink'),
        'download': uploaded.get('webContentLink')
    }

    return result
