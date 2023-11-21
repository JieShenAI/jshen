from aligo import Aligo
from . import ali


def init_aligo(refresh_token):
    Aligo(refresh_token=refresh_token)


def ali_upload(
        local_path,
        remote_path
):
    from pathlib import Path
    is_file = Path(local_path).is_file()  # 判断本地路径是文本还是文件夹
    remote_folder = ali.get_folder_by_path(remote_path)

    if is_file:
        ali.upload_file(
            local_path,
            parent_file_id=remote_folder.file_id)
    else:
        ali.upload_folder(
            local_path,
            parent_file_id=remote_folder.file_id)


def ali_download(
        remote_path,
        local_path='.'
):
    file_folder = (
            ali.get_folder_by_path(remote_path)
            or
            ali.get_file_by_path(remote_path)
    )

    if file_folder.type == 'file':
        ali.download_file(
            file=file_folder,
            local_folder=local_path)
    else:
        ali.download_folder(
            folder_file_id=file_folder.file_id,
            local_folder=local_path)
