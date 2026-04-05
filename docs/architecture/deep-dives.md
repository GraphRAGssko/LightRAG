# Deep Dives

## Query Modes
LightRAG는 질문의 특성에 따라 5가지 검색 모드를 제공합니다:

- **local**: 특정 엔티티나 세부적인 맥락에 초점을 맞춘 검색 모드. 지식 그래프의 구체적인 노드와 이웃 노드를 탐색합니다.
- **global**: 커뮤니티/요약 기반의 광범위한 지식 검색. "전체적인 요약"이나 "큰 그림"을 물어보는 질문에 적합합니다. (Community Summary 활용)
- **hybrid**: `local`과 `global` 모드의 결과를 결합하여 세부 정보와 거시적 정보를 모두 제공합니다.
- **naive**: 지식 그래프를 배제하고 전통적인 Vector RAG 방식으로 텍스트 청크만 검색합니다.
- **mix**: 지식 그래프 검색 결과와 벡터 기반 텍스트 청크 검색 결과를 모두 결합합니다 (Reranker 사용 시 가장 권장됨).

## Community Detection
그래프 내에서 밀접하게 관련된 엔티티(노드) 그룹을 찾는 과정입니다. 주로 Louvain clustering과 같은 알고리즘을 사용해 커뮤니티를 식별합니다. 식별된 각 커뮤니티는 사전에 LLM을 통해 요약(Community Summary)되며, **global** 모드 쿼리 시 이 요약본들을 모아서 최종 답변의 재료로 활용합니다.

## Storage Layer
LightRAG는 데이터의 성격에 따라 4가지의 분리된 저장소를 추상화하여 관리합니다. 운영 환경에 따라 JSON 파일부터 분산 데이터베이스까지 유연하게 교체할 수 있습니다.

1. **KV_STORAGE**: 텍스트 청크 원문, 문서 메타데이터 및 LLM 응답 캐시 저장 (JSON, Redis, MongoDB 등)
2. **VECTOR_STORAGE**: 엔티티, 관계, 텍스트 청크의 벡터 임베딩 저장 (NanoVectorDB, Milvus, Qdrant, Faiss 등)
3. **GRAPH_STORAGE**: 노드와 엣지로 이루어진 지식 그래프 구조 저장 (NetworkX, Neo4j, PostgreSQL(AGE), Memgraph 등)
4. **DOC_STATUS_STORAGE**: 문서의 인덱싱 진행 상태(성공, 실패 등) 트래킹을 위한 저장소.
