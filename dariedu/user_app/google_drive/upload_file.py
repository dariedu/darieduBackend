from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


FOLDER_NAME = 'Users'


def authenticate():

    google_auth = GoogleAuth()
    google_auth.LoadCredentialsFile('token.json')

    return google_auth


def upload_file(file):
    drive = GoogleDrive(authenticate())

    folder_id = get_folder_id(drive)

    file_drive = drive.CreateFile({'title': f'{file.name[8:]}', 'parents': [{'id': f'{folder_id}'}]})
    file_drive.SetContentFile(f'{file}')
    file_drive.Upload()
    file_drive.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })

    return file_drive


def get_folder_id(drive: GoogleDrive):

    query = f'title="{FOLDER_NAME}" and mimeType="application/vnd.google-apps.folder" and trashed=false'
    folder_lists = drive.ListFile({'q': query}).GetList()

    if not folder_lists:
        folder_metadata = {
            'title': f'{FOLDER_NAME}',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder_file = drive.CreateFile(folder_metadata)
        folder_file.Upload()

        folder_lists.append(folder_file)

    return folder_lists[0]['id']


def get_link_view(file):
    google_file = upload_file(file)

    return google_file['embedLink']
