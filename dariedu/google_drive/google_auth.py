import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleAuthCustom:
    CREDENTIAL_NAME = 'client_secrets.json'
    FILE_NAME = 'token.json'

    def __init__(self):
        self.google_auth: GoogleAuth = GoogleAuth()
        self.drive: GoogleDrive = GoogleDrive()

    def settings(self):
        self.google_auth.settings['client_config_file'] = self.CREDENTIAL_NAME
        self.google_auth.settings['get_refresh_token'] = True
        self.google_auth.settings['oauth_scope'] = ['https://www.googleapis.com/auth/drive']

    def auth(self):
        self.settings()
        self.change_dir()
        self.google_auth.LoadCredentialsFile(self.FILE_NAME)

        if self.google_auth.credentials is None:
            raise 'Error'
        elif self.google_auth.access_token_expired:
            self.google_auth.Refresh()
        else:
            self.google_auth.Authorize()

        self.google_auth.SaveCredentialsFile(self.FILE_NAME)

        return self.google_auth

    def first_auth(self):
        self.settings()
        self.google_auth.LocalWebserverAuth()
        self.change_dir()
        self.google_auth.SaveCredentialsFile(self.FILE_NAME)

    @staticmethod
    def change_dir():
        path = os.path.abspath(__file__).split(os.path.sep)
        index = path.index('app') + 1  # index = path.index('dariedu') + 1 - Для локального запуска
        os.chdir(os.path.sep.join(path[:index]))


if __name__ == '__main__':
    first_auth = GoogleAuthCustom()
    first_auth.first_auth()
