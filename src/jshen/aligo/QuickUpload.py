import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

from aligo import CreateFileRequest
from aligo.core.Config import ADRIVE_V2_FILE_CREATEWITHFOLDERS

from . import ali

"""
暂不支持上传文件功能，建议使用网盘自带的上传功能

# 文件快传示例：
    ql = QuickUpload()
    filename = '~/Downloads/pdfs/xxx.pdf'
    data = ql.get_quick_upload_data(filename)
    print(data)
    print(ql.quick_upload('快传测试.pdf', data))
    
# 本地保存文件夹的hash等信息，依据hash等信息在云端创建出文件：
    ql = QuickUpload()
    ql.save_quick_upload_info(
        "/Users/xxx/本地文件夹",
        "/Users/xxx/文件夹下所有文件的hash信息.jsonl",
        origin="文件夹来源",
        ...
        desc="文件夹描述可选" # 可选
        )

    file = "文件夹下所有文件的hash信息.jsonl"
    ql.create_cloud_folder_by_local_file(file, "云盘文件夹路径")
"""


@dataclass
class QuickUpload:

    def get_quick_upload_data(self, filename):
        file_size = os.path.getsize(filename)
        content_hash = self.content_hash(filename, file_size)
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
            ali_info: List,
            parent_path='',
            parent_file_id='root',
    ):
        """
        使用文件名、ali_info [hash、size、proof_code] 快传文件到 云端文件夹 parent_path下
        :param name: 文件名
        :param ali_info: [hash、size、proof_code]
        :param parent_path: 云盘文件夹绝对路径
        :param parent_file_id: 支持使用文件夹id
        :return:
        """
        assert parent_path or parent_file_id, "parent_path or parent_file_id must be specified"
        content_hash, file_size, proof_code = ali_info

        if parent_path:
            parent_file_id = ali.create_folder(
                parent_path,
                check_name_mode='refuse',  # 不要自动重命名文件夹
            ).file_id

        body = CreateFileRequest(
            drive_id=ali.default_drive_id,
            part_info_list=ali._get_part_info_list(file_size),
            name=name,
            type='file',
            size=file_size,
            content_hash=content_hash,
            content_hash_name="sha1",
            proof_code=proof_code,
            proof_version='v1',
            parent_file_id=parent_file_id,
        )
        return ali.post(ADRIVE_V2_FILE_CREATEWITHFOLDERS, body=body)

    def save_quick_upload_info(
            self,
            folder: str,
            output: str,
            origin: str = '',
            **kwargs,
    ):
        """
        计算folder文件夹下所有文件的hash、size、proof_code，并保存到output文件中
        :param folder: 文件夹路径
        :param output: 一般为jsonl文件
        :param origin: 文件来源
        :param kwargs: 其他属性
        :return:
        """
        while folder[-1] == '/':
            folder = folder[:-1]

        if os.path.exists(output):
            is_sure = input(f"文件 '{output}' 已存在是否覆盖？(y/n)")
            if is_sure not in "yY":
                return

        readme_content = ""
        # 查看那个文件夹下是否有readme.md文件，如果有则将readme.md文件内的所有文字添加入详情信息中
        if os.path.exists(os.path.join(folder, "readme.md")):
            with open(os.path.join(folder, "readme.md"), 'r') as f:
                readme_content = f.read()

        project_node = {
            "name": os.path.basename(folder),
            "type": "project_folder",
            "readme": readme_content,
            "origin": origin,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        project_node.update(kwargs)

        folder_data = self.walk_folder(folder)

        with open(output, 'w+', encoding='utf-8') as f:

            # 项目文件信息
            json_line = json.dumps(project_node) + "\n"
            f.write(json_line)

            for local_filename, cloud_filename in folder_data:
                ali_info = self.get_quick_upload_data(local_filename)
                data = {
                    "file_path": cloud_filename,
                    "ali_info": list(ali_info),
                    "filename": os.path.basename(local_filename),
                    "type": "file",
                }
                json_line = json.dumps(data) + "\n"
                f.write(json_line)

    def create_cloud_folder_by_local_file(
            self,
            local_file,
            remote_folder,
    ):
        """
        通过本地保存的jsonl文件，根据其中的hash、siz、文件名，秒传文件
        :param local_file: 本地的jsonl文件
        :param remote_folder: 阿里云盘该文件夹所处的文件
        :return:
        """
        with open(local_file, 'r', encoding='utf-8') as jsonl_file:
            # ali.parent_file_id = 'root'
            for line in jsonl_file:
                entry = json.loads(line)
                if entry['type'] == 'project_folder':
                    continue
                ali_info = entry['ali_info']
                file_path = entry['file_path']
                remote_folder_upload = os.path.join(
                    remote_folder,
                    os.path.dirname(file_path))

                self.quick_upload(
                    name=entry['filename'],
                    ali_info=ali_info,
                    parent_path=remote_folder_upload,
                )

    @staticmethod
    def walk_folder(folder) -> List[Tuple[str, str]]:
        # 遍历folder下的所有文件
        folder_name = os.path.basename(folder)
        res = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                # 打印文件路径
                local_filename = os.path.join(root, file)
                file_root_path = folder_name + root.split(folder)[1:][0]
                cloud_filename = os.path.join(file_root_path, file)
                # 实现根据文件夹路径在阿里云上创建文件，包括创建新文件夹
                res.append((
                    local_filename,
                    cloud_filename
                ))

        return res

    @staticmethod
    def content_hash(filename, file_size):
        """
        这里设置的10MB，不确定对大文件是否OK
        :param filename:
        :return:
        """
        # __UPLOAD_CHUNK_SIZE: int = 10485760  # 10 MB

        if file_size < 104857600000:  # (1024 * 1024 * 10) * 10000
            __UPLOAD_CHUNK_SIZE = 10485760  # (1024 * 1024 * 10) => 10 MB
        else:
            __UPLOAD_CHUNK_SIZE = 268435456  # 256 MB

        content_hash = hashlib.sha1()

        with open(filename, 'rb') as f:
            while True:
                segment = f.read(__UPLOAD_CHUNK_SIZE)
                if not segment:
                    break
                content_hash.update(segment)

        return content_hash.hexdigest().upper()
