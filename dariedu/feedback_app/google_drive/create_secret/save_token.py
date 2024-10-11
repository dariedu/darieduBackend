import os

from pydrive.auth import GoogleAuth


def change_dir():
    """Смена директории для сохранения токена в нужной директории"""
    os.chdir('../../../')


def create_token():
    """Создание access токена для не интерактивной авторизации в google"""

    google_auth = GoogleAuth()
    google_auth.LocalWebserverAuth()

    change_dir()

    google_auth.SaveCredentialsFile('token.json')


if __name__ == '__main__':
    create_token()
