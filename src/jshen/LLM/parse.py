import re
import json
from typing import Union, Dict


def re_parse_json(text) -> Union[Dict, None]:
    """
    从大模型的返回结果里面，提取json数据，并转换为字典
    """
    # 提取 JSON 内容
    json_match = re.search(r"\{.*?\}", text, re.DOTALL)
    if json_match:
        json_data = json_match.group(0)
        response_data = json.loads(json_data)
        return response_data
    print(f"异常:\n{text}")
    return None


