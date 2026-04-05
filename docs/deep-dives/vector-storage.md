# Vector Storage

> **High-Performance Similarity Search Backends**

**Vector Storage**는 LightRAG 파이프라인에서 추출된 텍스트 청크, 엔티티 이름, 커뮤니티 요약 등의 **임베딩(Embeddings)**을 저장하고 유사도 검색(Similarity Search)을 수행하는 레이어입니다.

---

## Role in LightRAG

벡터 저장소는 다음과 같은 질문에 답하기 위해 사용됩니다:
1. *"이 질문과 의미적으로 가장 가까운 엔티티(노드)는 무엇인가?"* (Graph 탐색의 진입점)
2. *"이 질문의 정답을 포함하고 있을 가능성이 가장 높은 원문 텍스트 청크는 무엇인가?"* (Naive RAG 및 Hybrid 검색)

모든 검색은 Cosine Similarity 등의 거리 지표를 기반으로 Top-K 결과를 반환합니다.

---

## Supported Backends

그래프 스토리지와 마찬가지로, 요구사항에 맞춰 다양한 Vector DB를 플러그인 형태로 교체할 수 있습니다.

### 1. NanoVectorDB (Default / Local)
- **특징**: 외부 종속성 없이 Python 내에서 동작하는 초경량 로컬 벡터 스토리지입니다. JSON 또는 바이너리 형태로 디스크에 데이터를 플러시합니다.
- **Best For**: 로컬 개발, 테스트, 수만 개 이하의 임베딩 처리.

### 2. Milvus
- **특징**: 클라우드 네이티브 아키텍처로 설계된 고성능, 고가용성의 분산 벡터 데이터베이스입니다.
- **장점**: 수십억 개의 벡터를 밀리초 단위로 검색할 수 있으며, 다양한 인덱스 타입(HNSW, IVF 등)을 지원합니다.
- **Best For**: 초대규모 프로덕션 환경.

### 3. Qdrant
- **특징**: Rust로 작성되어 빠르고 메모리 효율적인 벡터 검색 엔진입니다.
- **장점**: Payload(메타데이터) 필터링 능력이 매우 뛰어나며, LightRAG에서는 `workspace` 파라미터를 이 Payload 필터링으로 구현하여 완벽한 멀티테넌트(Multi-tenant) 데이터 격리를 제공합니다.
- **Best For**: 메타데이터 필터링이 자주 필요하거나, 멀티테넌트 아키텍처를 구성할 때.

### 4. PostgreSQL (pgvector)
- **특징**: PostgreSQL의 `pgvector` 익스텐션을 활용하여 벡터 유사도 검색을 수행합니다.
- **장점**: 별도의 Vector DB 인프라를 구축할 필요 없이, 기존 RDBMS 내에서 벡터 연산을 처리할 수 있습니다. IVFFlat, HNSW 인덱스를 지원합니다.
- **Best For**: All-in-one 인프라(그래프, KV 모두 Postgres로 통합)를 선호하는 팀.

### 5. Faiss / OpenSearch
- Meta의 Faiss 라이브러리 기반의 로컬 가속 검색이나, AWS OpenSearch 클러스터를 활용한 분산 검색 또한 지원합니다.

---

## Dimension Mismatch Alert

벡터 저장소 사용 시 가장 흔히 발생하는 에러는 **임베딩 차원 불일치(Dimension Mismatch)** 입니다. 
예를 들어 `text-embedding-3-small` (1536 차원)으로 데이터를 삽입한 후, `bge-m3` (1024 차원)으로 모델을 변경하여 쿼리하려 하면 데이터베이스에서 오류가 발생합니다.

**해결책**: 임베딩 모델을 변경할 때는 반드시 기존 Vector Storage 데이터(컬렉션 또는 로컬 파일)를 삭제하고 처음부터 다시 인덱싱해야 합니다.