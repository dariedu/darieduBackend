from google_drive.google_auth import GoogleAuthCustom


class GooglePromotion(GoogleAuthCustom):
    FOLDER_NAME = 'tickets'

    def get_links(self, link: str = None):
        folder_id = self.get_folder_id(link)
        query = f'"{folder_id}" in parents and trashed=false'
        self.drive.auth = self.auth()
        files = self.drive.ListFile({'q': query}).GetList()

        return [file['embedLink'] for file in files]

    def get_folder_id(self, link: str = None):

        if not link:
            query = f'title="{self.FOLDER_NAME}" and trashed=false'
            list_folders = self.drive.ListFile({'q': query}).GetList()
            if not list_folders:
                list_folders.append(self.create_folder)
            folder_id = list_folders[0]['id']
        else:
            folder_id = link.split('/')[-1]
        return folder_id

    def create_folder(self):

        folder_metadata = {
            'title': self.FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()

        return folder
