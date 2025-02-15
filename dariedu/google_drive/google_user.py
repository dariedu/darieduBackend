from google_drive.google_auth import GoogleAuthCustom
import logging


logger = logging.getLogger('google.photo')


class GoogleUser(GoogleAuthCustom):
    FOLDER_NAME = 'Users'

    def get_link_view(self, file):  # file: File
        logger.info(f'Загрузка фото {file}')
        try:
            google_file = self.upload_file(file)
            logger.info(f'Фото {file} загружено')

            return google_file['embedLink']

        except Exception as e:
            logger.error(f'Ошибка загрузки фото {file}: {e}')

    def upload_file(self, file):  # file: File
        logger.info(f'Загрузка фото {file}')
        try:
            self.drive.auth = self.auth()
            folder_id = self.get_folder_id()
            logger.info(f'Загрузка фото в папку {folder_id}')

            file_to_google = self.drive.CreateFile(
                {
                    'title': f'{file.name[8:]}',
                    'parents': [{'id': f'{folder_id}'}]
                }
            )

            file_to_google.SetContentFile(f'media/{file}')
            file_to_google.Upload()
            logger.info(f'Фото {file} загружено')

            file_to_google.InsertPermission(
                {
                    'type': 'anyone',
                    'withLink': True,
                    'role': 'reader'
                }
            )
            logger.info(f'Ссылка на фото {file} создана')

            return file_to_google

        except Exception as e:
            logger.error(f'Ошибка загрузки фото {file}: {e}')

    def get_folder_id(self):
        logger.info(f'Получение папки {self.FOLDER_NAME}')
        try:
            query = f'title="{self.FOLDER_NAME}" and mimeType="application/vnd.google-apps.folder" and trashed=false'
            list_folders = self.drive.ListFile({'q': query}).GetList()
            logger.info(f'Папка {self.FOLDER_NAME} получена')

            if not list_folders:
                list_folders.append(self.create_folder())
                logger.info(f'Папка {self.FOLDER_NAME} создана')

            return list_folders[0]['id']

        except Exception as e:
            logger.error(f'Ошибка получения папки {self.FOLDER_NAME}: {e}')

    def create_folder(self):
        logger.info(f'Создание папки {self.FOLDER_NAME}')
        try:
            folder_metadata = {
                'title': self.FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
            logger.info(f'Папка {self.FOLDER_NAME} создана')

            return folder

        except Exception as e:
            logger.error(f'Ошибка создания папки {self.FOLDER_NAME}: {e}')
