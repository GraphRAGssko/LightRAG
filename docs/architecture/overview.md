# Overview

LightRAG는 정보 검색과 생성을 향상시키기 위해 그래프 기반 지식 표현(Knowledge Graph)을 사용하는 RAG(Retrieval-Augmented Generation) 프레임워크입니다. 

## System Design and Components

LightRAG의 시스템은 크게 4가지 레이어로 나뉩니다:

1. **Orchestration Layer**: 사용자 입력을 받아 전체 파이프라인(문서 삽입, 쿼리 처리)을 제어합니다.
2. **Operation Layer**: 청킹(Chunking), 엔티티(Entity) 및 관계(Relation) 추출, 다중 모드(Multi-mode) 검색을 수행합니다.
3. **Storage Layer**: 추출된 데이터들을 4가지 목적(KV, Vector, Graph, Doc Status)에 맞게 백엔드에 저장합니다.
4. **LLM/Embedding Layer**: 외부 언어 모델 및 임베딩 모델(OpenAI, Ollama, Jina 등)과 통신합니다.

## Data Flow

### 1. Indexing (문서 삽입)
- **문서 청킹 (Chunking)**: 긴 문서를 토큰 단위로 나누어 Overlap(겹침)을 두어 자릅니다.
- **LLM 추출 (Extraction)**: 각 청크에서 엔티티(Entity)와 이들 간의 관계(Relationship)를 추출합니다.
- **저장 (Storage)**:
  - 원본 청크 텍스트와 메타데이터는 **KV Storage**에 저장됩니다.
  - 엔티티와 관계 정보는 **Graph Storage** (Neo4j, NetworkX 등)에 노드와 엣지로 구축됩니다.
  - 엔티티와 청크의 벡터 임베딩은 **Vector Storage**에 저장되어 의미론적 검색을 대비합니다.

### 2. Retrieval (쿼리 및 검색)
- **질의 분석**: 사용자의 질문과 설정된 Query Mode(local, global, hybrid 등)에 따라 검색 전략을 결정합니다.
- **매칭 (Matching)**: 질문의 임베딩을 통해 Vector Storage에서 관련 엔티티 및 텍스트 청크를 찾습니다.
- **그래프 확장 (Graph Expansion)**: 매칭된 엔티티를 Graph Storage에서 조회하고 연결된 이웃 엔티티나 커뮤니티(Community) 정보를 가져옵니다.
- **프롬프트 구성 및 답변 생성 (Generation)**: 검색된 텍스트 청크, 엔티티 설명, 관계 설명, 커뮤니티 요약을 하나의 컨텍스트로 묶어 LLM에 전달하여 최종 답변을 생성합니다.
