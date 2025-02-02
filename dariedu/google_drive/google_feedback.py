import os
import datetime

from dotenv import load_dotenv

from google_drive.google_auth import GoogleAuthCustom


load_dotenv()


class GoogleFeedback(GoogleAuthCustom):
    FOLDER_ID = os.getenv('FOLDER_ID_PHOTO_REPORT')  # TODO в эту папку будут загружаться фото отчёты
    EMAIL = os.getenv('GOOGLE_EMAIL')  # TODO необходим для назначения доступа к папке

    def feedback_upload(self, file):  # : File

        self.drive.auth = self.auth()

        today = str(datetime.date.today())
        query = f'title="{today}" and trashed=false'
        folders_list = self.drive.ListFile({'q': query}).GetList()
        if not folders_list:
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

        folder_id = folders_list[0]['id']

        file_drive = self.drive.CreateFile(
            {
                'title': f'{file.name}',
                'parents': [{'id': folder_id}]
            }
        )

        file_drive.SetContentFile(f'photo_report/{file}')
        file_drive.Upload()

        file_drive.InsertPermission(
            {
                'type': 'anyone',
                'value': 'anyone',
                'role': 'reader'
            }
        )

        return file_drive

    def feedback_links(self, file):  # :File
        file = self.feedback_upload(file)

        result = {
            'view': file.get('embedLink'),
            'download': file.get('webContentLink')
        }

        return result

    def test(self):
        self.drive.auth = self.auth()

        query = 'trashed=false'
        files = self.drive.ListFile({'q': query}).GetList()
        for file in files:
            print(f'Title: {file["title"]}, ID: {file["id"]}')


if __name__ == '__main__':
    auth = GoogleFeedback()
    auth.test()
