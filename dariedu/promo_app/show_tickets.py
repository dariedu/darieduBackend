"""Данный скрипт показывает ссылки с Google Drive"""

from pydrive.auth import GoogleAuth, AuthenticationError
from pydrive.drive import GoogleDrive


FOLDER_NAME = 'tickets'  # Название папки, в которой находятся билеты, по умолчанию


def authenticate() -> GoogleAuth:
    """Авторизация в Google"""
    google_auth = GoogleAuth()
    google_auth.LoadCredentialsFile('token.json')  # В случае, если файл с токеном назван иначе изменить название файла

    if google_auth.credentials is None:
        raise AuthenticationError('File token.json not found')  # Если файла нет, возбуждаем исключение
    elif google_auth.access_token_expired:
        google_auth.Refresh()  # Обновляем токен, если время токена истекло
    else:
        google_auth.Authorize()  # Авторизуемся в Google

    return google_auth


def google_drive(google_auth: GoogleAuth) -> GoogleDrive:
    """Подключение к сервису Google Drive"""
    drive = GoogleDrive(google_auth)  # Класс для подключения к сервису Google Drive

    return drive


def create_folder(drive: GoogleDrive) -> list:
    """Создание папки (под вопросом необходимости данного действия)"""
    folder_metadata = {
        'title': FOLDER_NAME,
        'mimeType': 'application/vnd.google-apps.folder'
    }  # Основные настройки для создания папки
    folder = drive.CreateFile(folder_metadata)  # Создание папки
    folder.Upload()  # Загрузка папки в сервис Google Drive

    return folder


def get_folder_id(drive: GoogleDrive, link: str = None) -> str:
    """Получение id папки"""
    if not link:
        query = {'q': f'title="{FOLDER_NAME}" and trashed=false'}  # Формирование запроса к Google Drive

        folder = drive.ListFile(query).GetList()  # Получаем список папок, соответствующих названию FOLDER_NAME

        if not folder:  # В случае, если папка не найдена, создаётся эта папка с названием по умолчанию
            folder = create_folder(drive)

        folder_id = folder[0].get('id')  # Получаем id папки

        if not folder_id:  # Если папки по какой бы то ни было причины нет, возбуждаем исключение
            raise 'Folder does not found'
    else:
        folder_id = link.split('/')[-1]

    return folder_id


def get_links(folder_id: str, drive: GoogleDrive) -> list:
    """Получение билетов"""
    query = {'q': f'"{folder_id}" in parents and trashed=false'}  # Формирование запроса к Google Drive
    files = drive.ListFile(query).GetList()  # Получаем список файлов (билетов), которые находятся в папке FOLDER_NAME

    links = []  # Список ссылок на билеты
    for file in files:
        links.append(file.get('embedLink'))  # Добавление ссылки из полученных файлов в список

    return links


def show_tickets(link: str = None):
    """Получение списка ссылок"""
    try:  # В случае возбуждения какого-либо исключения обрабатываем и возвращаем строку для дальнейшей обработки
        google_auth = authenticate()  # Авторизация в Google
        drive = google_drive(google_auth)  # Подключение к сервису Google Drive
        folder_id = get_folder_id(drive, link)  # Получение id папки
        links = get_links(folder_id, drive)  # Получение списка ссылок
    except Exception as e:  # Обрабатываем исключение с соответствующих комментарием
        return f'Exception with folders (tickets) - {e}'
    else:  # Если исключений не были возбуждены возвращаем список ссылок
        return links


if __name__ == '__main__':
    """При необходимости скрипт будем запускать в данном файле"""
    show_tickets()


"""Для импорта используем функцию show_tickets: from tickets.show_tickets import show_tickets"""
