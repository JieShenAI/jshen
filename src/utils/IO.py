import json
import pathlib
from typing import Union


def read_json_file(filename: Union[str, pathlib.Path]) -> dict:
    """
    读取json文件
    :return:
    """
    if isinstance(filename, str):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif isinstance(filename, pathlib.Path):
        f = filename.open()
        data = json.load(f)
    else:
        data = {}
    return data


if __name__ == '__main__':
    read_json_file('settings.json')
