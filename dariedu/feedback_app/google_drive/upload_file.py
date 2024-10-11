from typing import Any
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from django.core.files import File


def authenticate() -> GoogleAuth:
    """Не интерактивная авторизация в Google"""
    google_auth = GoogleAuth()
    google_auth.LoadCredentialsFile('secret_token.json')

    return google_auth


def upload_file_to_google_drive(file: File) -> Any:
    """Загрузка файлов в GoogleDrive"""
    try:
        drive = GoogleDrive(authenticate())

        file_drive = drive.CreateFile({'title': f'{file.name}'})
        file_drive.SetContentFile(f'report_photo/{file}')
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
