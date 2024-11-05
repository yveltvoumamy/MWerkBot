from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pathlib import Path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def login_with_service_account():
    settings = {
                "client_config_backend": "service",
                "service_config": {
                    "client_json_file_path": "creds.json",
                }
            }
    gauth = GoogleAuth(settings=settings)
    gauth.ServiceAuth()
    return gauth


gauth = login_with_service_account()
gauth.ServiceAuth()
# gauth.LocalWebserverAuth()
folder_name = 'MWerkBotContest'


def upload_photo_to_gdrive(file_name: str, file_path: Path) -> bool:
    try:
        drive = GoogleDrive(gauth)
        # Загрузить файл на Google Drive
        file_list = drive.ListFile({'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and 'root' in parents"}).GetList()
        print(file_list)
        folder_id = '13p0voiELaeuGorzcgzD-byuNclG0hqs2'
        gdrive_file = drive.CreateFile({'title': f'{file_name}.jpg', 'parents': [{'id': folder_id}]})
        # drive.CreateFile({'title': f'{file_name}.jpg'}, 'parents': [{'id': folder_name['id']}])
        gdrive_file.SetContentFile(file_path)
        gdrive_file.Upload()
        return True
    except Exception as _ex:
        print(_ex)
        return False