"""
保护隐私的一些工具
"""
import json
import pathlib


def read_home_file(filename, home=None) -> dict:
    '''
    读取用户家目录下的文件
    :param home: 默认是用户家目录
    :param filename: xxx.json
    :return:
    '''
    if not home:
        home = str(pathlib.Path.home())
    file_path = pathlib.Path(home, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    pass
