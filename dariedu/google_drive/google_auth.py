import logging
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


logger = logging.getLogger('google.photo')

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
        logger.info('Авторизация прошла успешно')

    def auth(self):
        try:
            self.google_auth.ServiceAuth()
            logger.info("Successfully authenticated with Google Drive.")
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            raise

        return self.google_auth

    def update_file(self, file_id, file):
        self.drive.auth = self.auth()

        try:
            up_file = self.drive.CreateFile({'id': file_id})
            up_file.SetContentFile(f'media/{file}')
            up_file.Upload()

            logger.info(f"File '{file}' uploaded successfully to Google Drive with ID: {file_id}.")
        except Exception as e:
            logger.error(f"Error uploading file '{file}': {e}")


if __name__ == '__main__':
    test_auth = GoogleAuthCustom()

    try:
        test_auth.auth()
    except Exception as e:
        logger.error(f'Ошибка с авторизацией - {e}')
