import random


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
