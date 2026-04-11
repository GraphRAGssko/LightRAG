import os
import json
import time
import asyncio
import numpy as np

from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.utils import wrap_embedding_func_with_attrs

@wrap_embedding_func_with_attrs(embedding_dim=3072, max_token_size=8192)
async def custom_embed(texts: list[str]) -> np.ndarray:
    # 래핑된 함수가 아닌 원본 함수(.func)를 호출하면서 model 파라미터 전달
    return await openai_embed.func(texts, model="text-embedding-3-large")


def insert_text(rag, file_path):
    with open(file_path, mode="r") as f:
        unique_contexts = json.load(f)

    retries = 0
    max_retries = 3
    while retries < max_retries:
        try:
            rag.insert(unique_contexts)
            break
        except Exception as e:
            retries += 1
            print(f"Insertion failed, retrying ({retries}/{max_retries}), error: {e}")
            time.sleep(10)
    if retries == max_retries:
        print("Insertion failed after exceeding the maximum number of retries")


cls = "agriculture"
WORKING_DIR = f"../{cls}"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        embedding_func=custom_embed,
    )

    await rag.initialize_storages()  # Auto-initializes pipeline_status
    return rag


def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())
    insert_text(rag, f"../datasets/unique_contexts/{cls}_unique_contexts.json")


if __name__ == "__main__":
    main()
