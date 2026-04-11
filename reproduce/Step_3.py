import re
import json
from lightrag import LightRAG, QueryParam
from lightrag.utils import always_get_an_event_loop


def extract_queries(file_path):
    with open(file_path, "r") as f:
        data = f.read()

    data = data.replace("**", "")

    queries = re.findall(r"- Question \d+: (.+)", data)

    return queries


async def process_query(query_text, rag_instance, query_param):
    try:
        result = await rag_instance.aquery(query_text, param=query_param)
        return {"query": query_text, "result": result}, None
    except Exception as e:
        return None, {"query": query_text, "error": str(e)}


def run_queries_and_save_to_json(
    queries, rag_instance, query_param, output_file, error_file
):
    loop = always_get_an_event_loop()

    with (
        open(output_file, "a", encoding="utf-8") as result_file,
        open(error_file, "a", encoding="utf-8") as err_file,
    ):
        result_file.write("[\n")
        first_entry = True

        for query_text in queries:
            result, error = loop.run_until_complete(
                process_query(query_text, rag_instance, query_param)
            )

            if result:
                if not first_entry:
                    result_file.write(",\n")
                json.dump(result, result_file, ensure_ascii=False, indent=4)
                first_entry = False
            elif error:
                json.dump(error, err_file, ensure_ascii=False, indent=4)
                err_file.write("\n")

        result_file.write("\n]")


if __name__ == "__main__":
    import numpy as np
    from lightrag.utils import wrap_embedding_func_with_attrs
    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

    @wrap_embedding_func_with_attrs(embedding_dim=3072, max_token_size=8192)
    async def custom_embed(texts: list[str]) -> np.ndarray:
        return await openai_embed.func(texts, model="text-embedding-3-large")

    cls = "agriculture"
    mode = "hybrid"
    WORKING_DIR = f"../{cls}"

    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        embedding_func=custom_embed,
    )
    
    # Storage 초기화 (비동기 함수이므로 event loop를 통해 실행해야 함)
    loop = always_get_an_event_loop()
    loop.run_until_complete(rag.initialize_storages())

    query_param = QueryParam(mode=mode)

    queries = extract_queries(f"../datasets/questions/{cls}_questions.txt")
    run_queries_and_save_to_json(
        queries, rag, query_param, f"{cls}_result.json", f"{cls}_errors.json"
    )
