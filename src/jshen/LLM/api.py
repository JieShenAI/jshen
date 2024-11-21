"""
pip install langchain tqdm aiolimiter python-dotenv
"""

import asyncio
from tqdm import tqdm
from dataclasses import dataclass, field
from typing import List
from aiolimiter import AsyncLimiter
from langchain_openai import ChatOpenAI


import asyncio
from tqdm import tqdm
from dataclasses import dataclass, field
from typing import List
from aiolimiter import AsyncLimiter
from langchain_openai import ChatOpenAI


@dataclass
class AsyncLLMAPI:
    """
    大模型API的调用类
    """

    base_url: str
    api_key: str  # 每个API的key不一样
    uid: int
    cnt: int = 0  # 统计每个API被调用了多少次
    llm: ChatOpenAI = field(init=False)  # 自动创建的对象，不需要用户传入
    num_per_second: int = 6  # 限速每秒调用6次

    def __post_init__(self):
        # 初始化 llm 对象
        self.llm = self.create_llm()
        # 创建限速器，每秒最多发出 5 个请求
        self.limiter = AsyncLimiter(self.num_per_second, 1)

    def create_llm(self):
        # 创建 llm 对象
        return ChatOpenAI(
            model="gpt-4o-mini",
            base_url=self.base_url,
            api_key=self.api_key,
        )

    async def __call__(self, text):
        # 异步协程 限速
        self.cnt += 1
        async with self.limiter:
            return await self.llm.agenerate([text])

    @staticmethod
    async def _run_task_with_progress(task, pbar):
        """包装任务以更新进度条"""
        result = await task
        pbar.update(1)
        return result

    @staticmethod
    def run_data_async(llms: List["AsyncLLMAPI"], data: List[str]):
        async def _sync_run(llms, data):
            results = [llms[i % len(llms)](text) for i, text in enumerate(data)]
            # 使用 tqdm 创建一个进度条
            with tqdm(total=len(results)) as pbar:
                # asyncio.gather 并行执行任务
                results = await asyncio.gather(
                    *[
                        AsyncLLMAPI._run_task_with_progress(task, pbar)
                        for task in results
                    ]
                )
            return results, llms

        return asyncio.run(_sync_run(llms, data))


if __name__ == "__main__":
    pass
