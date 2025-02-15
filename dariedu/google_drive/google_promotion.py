from google_drive.google_auth import GoogleAuthCustom
import logging


logger = logging.getLogger('google.photo')


class GooglePromotion(GoogleAuthCustom):
    FOLDER_NAME = 'tickets'

    def get_links(self, link: str = None):
        logger.info('Получение ссылок на фото отчётов')
        try:
            folder_id = self.get_folder_id(link)
            query = f'"{folder_id}" in parents and trashed=false'
            self.drive.auth = self.auth()
            files = self.drive.ListFile({'q': query}).GetList()
            logger.info(f'Ссылки на фото отчётов получены')

            return [file['embedLink'] for file in files]

        except Exception as e:
            logger.error(f'Ошибка получения ссылок на фото отчётов: {e}', exc_info=True)

    def get_folder_id(self, link: str = None):
        logger.info('Получение ID папки с фото отчётами')

        try:
            if not link:
                query = f'title="{self.FOLDER_NAME}" and trashed=false'
                list_folders = self.drive.ListFile({'q': query}).GetList()
                logger.info(f'Папка с фото отчётами получена')
                if not list_folders:
                    list_folders.append(self.create_folder)
                    logger.info(f'Папка с фото отчётами создана')
                folder_id = list_folders[0]['id']
                logger.info(f'ID папки с фото отчётами: {folder_id}')
            else:
                folder_id = link.split('/')[-1]
                logger.info(f'ID папки с фото отчётами: {folder_id}')
            return folder_id

        except Exception as e:
            logger.error(f'Ошибка получения ID папки с фото отчётами: {e}', exc_info=True)

    def create_folder(self):
        logger.info('Создание папки с фото отчётами')

        try:
            folder_metadata = {
                'title': self.FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
            logger.info(f'Папка с фото отчётами создана')

            return folder

        except Exception as e:
            logger.error(f'Ошибка создания папки с фото отчётами: {e}', exc_info=True)
