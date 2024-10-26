from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


FOLDER_NAME = 'Users'  # Название папки в google drive - менять можно, всё автоматизировано


def authenticate():
    """Авторизация в google"""
    google_auth = GoogleAuth()
    google_auth.LoadCredentialsFile('token.json')

    return google_auth


def upload_file(file):
    """Загрузка фотографии в google drive"""
    drive = GoogleDrive(authenticate())

    folder_id = get_folder_id(drive)

    file_drive = drive.CreateFile({'title': f'{file.name[8:]}', 'parents': [{'id': f'{folder_id}'}]})
    file_drive.SetContentFile(f'media/{file}')
    file_drive.Upload()
    file_drive.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })

    return file_drive


def get_folder_id(drive: GoogleDrive):
    """Создание папки в google drive, если её нет"""
    query = f'title="{FOLDER_NAME}" and mimeType="application/vnd.google-apps.folder" and trashed=false'
    folder_lists = drive.ListFile({'q': query}).GetList()

    if not folder_lists:
        folder_metadata = {
            'title': f'{FOLDER_NAME}',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder_file = drive.CreateFile(folder_metadata)
        folder_file.Upload()

        folder_lists.append(folder_file)

    return folder_lists[0]['id']


def get_link_view(file):
    """Получение ссылки - view на фотографию"""
    try:
        google_file = upload_file(file)
        return google_file['embedLink']
    except Exception as e:
        return f'Exception - {e}'

