import datetime

from google_drive.google_auth import GoogleAuthCustom


class GoogleFeedback(GoogleAuthCustom):

    def feedback_upload(self, file):  # : File

        self.drive.auth = self.auth()

        today = str(datetime.date.today())
        query = f'title="{today}" and trashed=false'
        folders_list = self.drive.ListFile({'q': query}).GetList()

        if not folders_list:
            folder_metadata = {
                'title': today,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
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
