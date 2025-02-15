import os
import datetime
import logging
from dotenv import load_dotenv

from google_drive.google_auth import GoogleAuthCustom


load_dotenv()

logger = logging.getLogger('google.photo')


class GoogleFeedback(GoogleAuthCustom):
    FOLDER_ID = os.getenv('FOLDER_ID_PHOTO_REPORT')  # TODO в эту папку будут загружаться фото отчёты
    EMAIL = os.getenv('GOOGLE_EMAIL')  # TODO необходим для назначения доступа к папке

    def feedback_upload(self, file):  # : File
        logger.info(f'Загрузка фото отчёта {file}')
        try:
            self.drive.auth = self.auth()

            today = str(datetime.date.today())
            query = f'title="{today}" and trashed=false'
            folders_list = self.drive.ListFile({'q': query}).GetList()
            if not folders_list:
                logger.info(f'Создание папки {today}')

                folder_metadata = {
                    'title': today,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [{'id': self.FOLDER_ID}]
                }
                folder_permission = {
                    'type': 'user',
                    'role': 'writer',
                    'value': self.EMAIL
                }
                folder = self.drive.CreateFile(folder_metadata)
                folder.Upload()
                folder.InsertPermission(folder_permission)
                folders_list.append(folder)
                logger.info(f'Папка {today} создана')

            logger.info(f'Загрузка фото в папку {folders_list[0]["title"]}')

            folder_id = folders_list[0]['id']

            file_drive = self.drive.CreateFile(
                {
                    'title': f'{file.name}',
                    'parents': [{'id': folder_id}]
                }
            )

            file_drive.SetContentFile(f'photo_report/{file}')
            file_drive.Upload()
            logger.info(f'Фото загружено в папку {folders_list[0]["title"]}')

            file_drive.InsertPermission(
                {
                    'type': 'anyone',
                    'value': 'anyone',
                    'role': 'reader'
                }
            )
            logger.info(f'Доступ к фото отчёта открыт')

            return file_drive

        except Exception as e:
            logger.error(f'Ошибка загрузки фото отчёта {file}: {e}')

    def feedback_links(self, file):  # :File
        logger.info(f'Создание ссылок на фото отчёта {file}')
        try:
            file = self.feedback_upload(file)

            result = {
                'view': file.get('embedLink'),
                'download': file.get('webContentLink')
            }
            logger.info(f'Ссылки на фото отчёта {file} созданы')

            return result

        except Exception as e:
            logger.error(f'Ошибка создания ссылок на фото отчёта {file}: {e}')

    def test(self):
        logger.info('Получение списка фото отчётов')
        try:
            self.drive.auth = self.auth()

            query = 'trashed=false'
            files = self.drive.ListFile({'q': query}).GetList()
            for file in files:
                logger.info(f'Фото отчёта {file["title"]} загружено')

        except Exception as e:
            logger.error(f'Ошибка получения списка фото отчётов: {e}', exc_info=True)


if __name__ == '__main__':
    auth = GoogleFeedback()
    auth.test()
