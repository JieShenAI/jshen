import json
import pathlib
from typing import Union


def json2dict(file_data: Union[str, pathlib.Path]) -> dict:
    """json文件/字符串 转dict
    :return:
    :param file_data: str: [文件路径， json字符串]
    :return:
    """

    if isinstance(file_data, str):
        # 确保是文件
        if pathlib.Path(file_data).is_file():
            with open(file_data, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return json.loads(file_data)
    else:
        data = json.load(file_data)
    return data


def dict2json(obj: dict, file: Union[str, pathlib.Path]):
    if isinstance(file, str):
        json.dump(obj, open(file, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    else:
        json.dump(obj, file, indent=2, ensure_ascii=False)


def load_yaml(file: str, use_dot=False) -> dict:
    """

    :param file:
    :param use_dot: True: 使用点语法访问 data.attribute
    :return: dict or list
    :install: pip install PyYAML
    """
    import yaml

    class DotDict:
        def __init__(self, data):
            self.data = data

        def __getattr__(self, key):
            if key in self.data:
                return self.data[key]
            return getattr(self.data, key)

        def __len__(self):
            return len(self.data)

        def __repr__(self):
            return repr(self.data)

    data = yaml.load(open(file), Loader=yaml.FullLoader)
    if not use_dot:
        return data
    return DotDict(data)


def yaml2json(yaml_file: str, json_file: str):
    """yaml文件转json文件
    :param yaml_file:
    :param json_file:
    :return:
    """
    data = load_yaml(yaml_file)
    dict2json(data, json_file)
