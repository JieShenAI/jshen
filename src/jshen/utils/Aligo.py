from aligo import Aligo

ali = Aligo()


# quick branch
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


import hashlib
import os
from dataclasses import dataclass

from aligo import CreateFileRequest
from aligo.core.Config import ADRIVE_V2_FILE_CREATEWITHFOLDERS
from jshen import ali


# ali.upload_file(
#     '/Users/jshen/Downloads/pdfs/大语言模型融合知识图谱的问答系统研究_张鹤译.pdf'
# )


@dataclass
class QuickUpload:

    def get_quick_upload_data(self, filename):
        file_size = os.path.getsize(filename)
        content_hash = self.content_hash(filename)
        proof_code = ali._get_proof_code(filename, file_size)
        return content_hash, file_size, proof_code

    def quick_upload_by_file(self, filename, rename=''):
        drive_id = ali.default_drive_id
        name = rename if rename else os.path.basename(filename)
        content_hash, file_size, proof_code = self.get_quick_upload_data(filename)
        body = CreateFileRequest(
            drive_id=drive_id,
            part_info_list=ali._get_part_info_list(file_size),
            name=name,
            type='file',
            size=file_size,
            content_hash=content_hash,
            content_hash_name="sha1",
            proof_code=proof_code,
            proof_version='v1'
        )

        return (
            ali.post(ADRIVE_V2_FILE_CREATEWITHFOLDERS, body=body),
            (
                content_hash,
                file_size,
                proof_code
            )
        )

    @staticmethod
    def quick_upload(
            name,
            content_hash,
            file_size,
            proof_code
    ):
        body = CreateFileRequest(
            drive_id=ali.default_drive_id,
            part_info_list=ali._get_part_info_list(file_size),
            name=name,
            type='file',
            size=file_size,
            content_hash=content_hash,
            content_hash_name="sha1",
            proof_code=proof_code,
            proof_version='v1'
        )

        return ali.post(ADRIVE_V2_FILE_CREATEWITHFOLDERS, body=body)

    @staticmethod
    def content_hash(filename):
        __UPLOAD_CHUNK_SIZE: int = 10485760  # 10 MB
        content_hash = hashlib.sha1()

        with open(filename, 'rb') as f:
            while True:
                segment = f.read(__UPLOAD_CHUNK_SIZE)
                if not segment:
                    break
                content_hash.update(segment)

        return content_hash.hexdigest().upper()


if __name__ == '__main__':
    ql = QuickUpload()
    filename = '/Users/jshen/Downloads/pdfs/大语言模型融合知识图谱的问答系统研究_张鹤译.pdf'
    data = ql.get_quick_upload_data(filename)
    print(data)
    print(ql.quick_upload('快传测试.pdf', *data))
    print(ql.quick_upload_by_file(
        '/Users/jshen/Downloads/pdfs/大语言模型融合知识图谱的问答系统研究_张鹤译.pdf',
        '文件上传.pdf'
    ))
