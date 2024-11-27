import json
import random
from typing import List


def generate_arithmetic_expression(num: int):
    """
    num: 几个操作符

        prompt_template:
        你是一名擅长数学运算的助手，负责逐步推理并解决四则运算问题。请按照以下步骤进行：

        1. 阅读并理解问题。
        2. 分步计算，逐步解决问题。
        3. 给出最终的结果。
        4. 按照 JSON 格式输出结果，包括：
        - reason: 详细的推理过程。
        - infer: 最终的计算结果。

        问题：{question}
        请给出分析和结果。
    """
    # 定义操作符和数字范围，除法
    operators = ["+", "-", "*"]
    expression = (
        f"{random.randint(1, 100)} {random.choice(operators)} {random.randint(1, 100)}"
    )
    num -= 1
    for _ in range(num):
        expression = f"{expression} {random.choice(operators)} {random.randint(1, 100)}"
    result = eval(expression)
    expression = expression.replace("*", "x")
    return expression, result


def trans2llm_dataset(
    texts: List[str],
    labels: List[str],
    output_file,
    instruction="",
    prompt_template="",
    replace_kw="",
):

    data = []
    for text, label in zip(texts, labels):
        if replace_kw and prompt_template:
            text = prompt_template.replace(replace_kw, text)

        d = {
            "instruction": instruction,
            "input": text,
            "output": label,
        }
        data.append(d)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
