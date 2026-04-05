# Python Modules Reference

EdgeQuake의 Rust Crate 구조처럼, LightRAG 시스템을 구성하는 주요 Python 파일 및 모듈(.py)들의 역할을 설명합니다.

## Core Modules

| Module / File | Description |
|--------------|-------------|
| **`lightrag.py`** | 메인 오케스트레이터 클래스인 `LightRAG`가 정의된 진입점(Entry point) 파일입니다. 문서 삽입(`ainsert`), 쿼리(`aquery`), 스토리지 초기화(`initialize_storages`) 등 최상위 API를 제공합니다. |
| **`operate.py`** | 핵심 로직(Extraction, Chunking, Retrieval)이 구현된 파일입니다. 텍스트를 자르고, LLM을 호출해 엔티티를 추출하며, 각 Query Mode (local, global, hybrid 등)에 대한 실제 검색(Retrieval) 동작을 수행합니다. |
| **`base.py`** | 스토리지 백엔드 및 주요 컴포넌트들의 **추상 기본 클래스(Abstract Base Classes)** 가 정의되어 있습니다. (`BaseKVStorage`, `BaseVectorStorage`, `BaseGraphStorage` 등) |
| **`types.py`**, **`constants.py`** | 시스템 전반에서 사용되는 데이터 구조(Type)와 상수, 환경 변수 기본값 등이 정의되어 있습니다. |
| **`prompt.py`** | 시스템에서 사용되는 핵심 LLM 프롬프트(엔티티 추출용, 로컬 검색용, 글로벌 검색용 등)가 문자열로 정리되어 있습니다. |
| **`rerank.py`** | 검색 결과의 순위를 재조정(Re-ranking)하기 위한 로직(BGE Reranker 모델 지원 등)을 담고 있습니다. |

## Storage Submodules (`kg/`)

지식 그래프 및 데이터를 저장하는 다양한 백엔드 구현체들입니다.

| File | Storage Backend |
|------|-----------------|
| **`networkx_impl.py`** | 로컬 메모리 및 파일 기반의 Graph Storage (NetworkX 사용) |
| **`neo4j_impl.py`** | Neo4j 데이터베이스 기반의 Graph Storage |
| **`postgres_impl.py`** | PostgreSQL 기반 통합 스토리지 (Graph, Vector, KV 지원) |
| **`qdrant_impl.py`** | Qdrant 기반 Vector Storage |
| **`milvus_impl.py`** | Milvus 기반 Vector Storage |
| **`redis_impl.py`**, **`mongo_impl.py`** | Redis 및 MongoDB 기반 KV / Doc Status Storage |
| **`json_kv_impl.py`** | 가장 기본적인 로컬 JSON 파일 기반 KV Storage |
| **`nano_vector_db_impl.py`** | 외부 의존성 없는 로컬 파일 기반 Vector Storage |

## LLM Submodules (`llm/`)

외부 대규모 언어 모델(LLM) 공급자들과의 비동기 통신(Binding) 구현체들입니다.

| File | LLM Provider |
|------|--------------|
| **`openai.py`** | OpenAI (GPT-4, 4o-mini 등) 및 Text Embedding 모델 바인딩 |
| **`ollama.py`** | Ollama를 통한 로컬 오픈소스 모델 바인딩 |
| **`azure_openai.py`** | Azure에 배포된 OpenAI 엔드포인트 바인딩 |
| **`gemini.py`**, **`bedrock.py`**, **`anthropic.py`** | Google Gemini, AWS Bedrock, Anthropic Claude 연동 |
| **`hf.py`**, **`zhipu.py`** | Hugging Face Inference API 및 Zhipu(GLM) 모델 지원 |

## API Server (`api/`)

외부 애플리케이션이나 Web UI가 LightRAG와 통신할 수 있게 해주는 서버 애플리케이션입니다.

| File | Description |
|------|-------------|
| **`lightrag_server.py`** | FastAPI 메인 애플리케이션 객체 및 진입점 |
| **`routers/`** | `query_routes.py`(검색), `document_routes.py`(문서 삽입), `graph_routes.py`(그래프 시각화 API) 등 엔드포인트 집합 |
| **`routers/ollama_api.py`** | 다른 툴(Web UI 등)과 호환되기 위해 제공하는 Ollama 호환 API 엔드포인트 |
| **`auth.py`**, **`passwords.py`** | API 호출에 대한 인증(Authentication) 및 보안 로직 |

## Helpers (`utils`)

| File | Description |
|------|-------------|
| **`utils.py`** | 로깅(logger), 텍스트 해싱, 캐시 키 생성 등 공통 유틸리티 함수 |
| **`utils_graph.py`** | 그래프 탐색 및 구조화, 서브그래프(Subgraph) 처리 관련 유틸리티 |
