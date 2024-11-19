from google_drive.google_auth import GoogleAuthCustom


class GoogleUser(GoogleAuthCustom):
    FOLDER_NAME = 'Users'

    def get_link_view(self, file):  # file: File

        google_file = self.upload_file(file)

        return google_file['embedLink']

    def upload_file(self, file):  # file: File
        self.drive.auth = self.auth()
        folder_id = self.get_folder_id()

        file_to_google = self.drive.CreateFile(
            {
                'title': f'{file.name[8:]}',
                'parents': [{'id': f'{folder_id}'}]
            }
        )

        file_to_google.SetContentFile(f'media/{file}')
        file_to_google.Upload()

        file_to_google.InsertPermission(
            {
                'type': 'anyone',
                'withLink': True,
                'role': 'reader'
            }
        )

        return file_to_google

    def get_folder_id(self):
        query = f'title="{self.FOLDER_NAME}" and mimeType="application/vnd.google-apps.folder" and trashed=false'
        list_folders = self.drive.ListFile({'q': query}).GetList()

        if not list_folders:
            list_folders.append(self.create_folder())

        return list_folders[0]['id']

    def create_folder(self):

        folder_metadata = {
            'title': self.FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()

        return folder
