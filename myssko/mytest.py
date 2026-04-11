# %%
# # LightRAG kg_query 분석용 노트북
# 이 코드는 WebUI의 "당뇨병의 유형을 간략히 알려주라" 질의를 그대로 파이썬 코드로 가져와,
# 내부의 kg_query가 어떤 값을 리턴하는지 뜯어보기 위한 코드입니다.

# %%
!pip install transformers
# %%
import transformers
import os
import asyncio
import numpy as np  
from dotenv import load_dotenv
# %%
# .env 파일에서 API Key 등을 로드합니다. (lightrag-hku 환경에서 사용하셨던 환경변수 설정)
load_dotenv()

# %%
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.utils import wrap_embedding_func_with_attrs
from lightrag.operate import kg_query
from dataclasses import asdict

# 기존에 데이터가 업로드된 경로(rag_storage)를 지정합니다.
WORKING_DIR = "./rag_storage"

# %% [markdown]
# ## 1. RAG 객체 초기화 및 스토리지 연결

# %%
@wrap_embedding_func_with_attrs(embedding_dim=3072, max_token_size=8192)
async def custom_embed(texts: list[str]) -> np.ndarray:
    # 래핑된 함수가 아닌 원본 함수(.func)를 호출하면서 model 파라미터 전달
    return await openai_embed.func(texts, model="text-embedding-3-large")

# RAG 객체 생성
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_name="gpt-4o-mini",          # LLM 모델명 명시
    llm_model_func=gpt_4o_mini_complete,   # gpt-4o-mini 호출 함수
    embedding_func=custom_embed,           # 새로 정의한 커스텀 임베딩 함수 적용
)

# 비동기로 스토리지 초기화 (Jupyter 환경이므로 await 사용)
await rag.initialize_storages()

# %% [markdown]
# ## 2. 직접 kg_query 호출해보기
# WebUI에서 입력했던 파라미터(Global 모드, 텍스트)를 동일하게 세팅합니다.

# %%
query_text = "당뇨병의 유형을 간략히 알려주라"
query_param = QueryParam(
    mode="global",
    top_k=40,
    chunk_top_k=20,
    max_entity_tokens=6000,
    max_relation_tokens=8000,
    max_total_tokens=30000,
    enable_rerank=True # WebUI 스샷에 체크되어 있지 않다면 False로 변경하세요.
)
# %%
# global_config는 rag 인스턴스의 설정값을 딕셔너리로 만듭니다.
global_config = asdict(rag) 

# %%
print(f"질의: {query_text}")
print(f"모드: {query_param.mode}")

# %% [markdown]
# ## 3. kg_query 실행 및 결과 구조 파악

# %%
# 실제 lightrag.py 내부에서 호출되는 방식과 동일하게 kg_query 호출
query_result = await kg_query(
    query=query_text,
    knowledge_graph_inst=rag.chunk_entity_relation_graph,
    entities_vdb=rag.entities_vdb,
    relationships_vdb=rag.relationships_vdb,
    text_chunks_db=rag.text_chunks,
    query_param=query_param,
    global_config=global_config,
    hashing_kv=rag.llm_response_cache,
    system_prompt=None,
    chunks_vdb=rag.chunks_vdb,
)

# %% [markdown]
# ## 4. 결과값(QueryResult) 뜯어보기

# %%
# QueryResult는 객체 형태이므로 내부 속성들을 확인합니다.
print("\n========== [1. 최종 답변 내용 (content)] ==========")
print(query_result.content)

print("\n========== [2. Raw Data 구조 확인 (raw_data)] ==========")
# raw_data는 딕셔너리로 반환되며, 검색에 사용된 Context와 메타데이터가 담겨 있습니다.
raw_data = query_result.raw_data
print(f"Keys in raw_data: {list(raw_data.keys())}")

# 메타데이터 출력 (추출된 키워드 등)
if "metadata" in raw_data:
    print("\n[Metadata]")
    import json
    print(json.dumps(raw_data["metadata"], indent=2, ensure_ascii=False))
# %%
# 검색된 관계(Relation) 데이터 개수 확인 (Global 모드의 핵심)
if "relationships" in raw_data:
    print(f"\n[검색된 Relations 개수]: {len(raw_data['relationships'])}")
    if len(raw_data['relationships']) > 0:
        print("첫 번째 Relation 샘플:")
        print(json.dumps(raw_data['relationships'][0], indent=2, ensure_ascii=False))

# LLM에게 실제로 전달된 Context (Prompt 내에 들어가는 배경지식 문자열)
if "context" in raw_data:
    print("\n========== [3. LLM에게 전달된 Context (요약)] ==========")
    context_str = raw_data["context"]
    # 너무 기니까 500자만 출력
    print(context_str[:500] + " ... (이하 생략)")

# %%
# 사용이 끝났으면 스토리지 정리
await rag.finalize_storages()
# %% [markdown]
# ## 5. 내부 함수(_build_query_context) 직접 호출해보기

# %%
from lightrag.operate import _build_query_context, get_keywords_from_query

# 1) 먼저 LLM을 통해 질문에서 High-level / Low-level 키워드를 추출합니다.
hl_keywords, ll_keywords = await get_keywords_from_query(
    query=query_text,
    query_param=query_param,
    global_config=global_config,
    hashing_kv=rag.llm_response_cache
)

print("\n========== [추출된 키워드] ==========")
print(f"High-level: {hl_keywords}")
print(f"Low-level: {ll_keywords}")

# 2) _build_query_context 함수는 문자열 형태의 키워드를 받으므로 변환해 줍니다.
hl_keywords_str = ", ".join(hl_keywords) if hl_keywords else ""
ll_keywords_str = ", ".join(ll_keywords) if ll_keywords else ""

# 3) _build_query_context 호출
context_result = await _build_query_context(
    query=query_text,
    ll_keywords=ll_keywords_str,
    hl_keywords=hl_keywords_str,
    knowledge_graph_inst=rag.chunk_entity_relation_graph,
    entities_vdb=rag.entities_vdb,
    relationships_vdb=rag.relationships_vdb,
    text_chunks_db=rag.text_chunks,
    query_param=query_param,
    chunks_vdb=rag.chunks_vdb
)

# %%
# 4) 결과 확인
if context_result:
    print("\n========== [_build_query_context 결과 확인] ==========")
    print(f"조립된 Context 텍스트 길이: {len(context_result.context)}")
    print(f"포함된 엔티티 수: {len(context_result.raw_data.get('data', {}).get('entities', []))}")
    print(f"포함된 관계 수: {len(context_result.raw_data.get('data', {}).get('relationships', []))}")
    print(f"포함된 청크 수: {len(context_result.raw_data.get('data', {}).get('chunks', []))}")
    
    # context 전문의 일부만 출력해보기
    print("\n[Context 미리보기]")
    print(context_result.context[:500] + "\n... (이하 생략)")
else:
    print("\n조건에 맞는 데이터를 찾지 못했습니다.")

# %%
# %% [markdown]
# ## 6. 내부 함수(_perform_kg_search) 직접 호출해보기
# 토큰 자르기(Truncation)나 프롬프트 텍스트 조립 없이, 순수하게 검색된 
# 엔티티, 관계, 벡터 청크 데이터 원본 구조를 확인하는 용도입니다.

# %%
from lightrag.operate import _perform_kg_search, get_keywords_from_query

# 혹시 앞에서 키워드 추출이 안되었다면 여기서 다시 추출
hl_keywords, ll_keywords = await get_keywords_from_query(
    query=query_text,
    query_param=query_param,
    global_config=global_config,
    hashing_kv=rag.llm_response_cache
)

hl_keywords_str = ", ".join(hl_keywords) if hl_keywords else ""
ll_keywords_str = ", ".join(ll_keywords) if ll_keywords else ""

# _perform_kg_search 호출 (인자는 _build_query_context와 거의 동일합니다)
search_result = await _perform_kg_search(
    query=query_text,
    ll_keywords=ll_keywords_str,
    hl_keywords=hl_keywords_str,
    knowledge_graph_inst=rag.chunk_entity_relation_graph,
    entities_vdb=rag.entities_vdb,
    relationships_vdb=rag.relationships_vdb,
    text_chunks_db=rag.text_chunks,
    query_param=query_param,
    chunks_vdb=rag.chunks_vdb
)

# %%
# 결과 확인
print("\n========== [_perform_kg_search 결과 확인 (Stage 1 Pure Search)] ==========")

# search_result는 딕셔너리 형태로 반환됩니다.
print(f"반환된 Key 목록: {list(search_result.keys())}")

# 각각의 데이터 개수 확인
final_entities = search_result.get("final_entities", [])
final_relations = search_result.get("final_relations", [])
vector_chunks = search_result.get("vector_chunks", [])
chunk_tracking = search_result.get("chunk_tracking", {})

print(f"\n1. 검색된 최종 엔티티(Entities) 개수: {len(final_entities)}")
print(f"2. 검색된 최종 관계(Relations) 개수: {len(final_relations)}")
print(f"3. 나이브 벡터 검색 청크(Vector Chunks) 개수: {len(vector_chunks)}")
print(f"4. 트래킹 중인 문서 청크(Chunk Tracking) 개수: {len(chunk_tracking)}")

# 구조 확인을 위해 각각 첫 번째 데이터만 샘플로 출력해보기
import json

if final_entities:
    print("\n[엔티티 샘플 (1개)]")
    # rank, weight 등 점수가 포함되어 있습니다.
    print(json.dumps(final_entities[0], indent=2, ensure_ascii=False))

if final_relations:
    print("\n[관계 샘플 (1개)]")
    print(json.dumps(final_relations[0], indent=2, ensure_ascii=False))

if vector_chunks:
    print("\n[벡터 청크 샘플 (1개)]")
    print(json.dumps(vector_chunks[0], indent=2, ensure_ascii=False))
