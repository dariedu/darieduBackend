import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class GoogleAuthCustom:
    CREDENTIAL_NAME = 'credentials.json'
    SETTINGS = {
        'client_config_backend': 'service',
        'service_config': {
            'client_json_file_path': CREDENTIAL_NAME
        }
    }

    def __init__(self):
        self.google_auth: GoogleAuth = GoogleAuth(settings=self.SETTINGS)
        self.drive: GoogleDrive = GoogleDrive()

    def auth(self):
        self.google_auth.ServiceAuth()

        return self.google_auth

    def update_file(self, file_id, file):
        self.drive.auth = self.auth()

        up_file = self.drive.CreateFile({'id': file_id})
        up_file.SetContentFile(f'media/{file}')
        up_file.Upload()


if __name__ == '__main__':
    test_auth = GoogleAuthCustom()

    try:
        test_auth.auth()
    except Exception as e:
        print(f'Ошибка с авторизацией - {e}')
