# Graph Storage

> **Backends for Knowledge Graph Representation**

LightRAG에서 **Graph Storage**는 LLM이 텍스트로부터 추출한 노드(엔티티)와 엣지(관계)를 저장하고 쿼리하는 데 사용됩니다. 이 레이어는 시스템의 확장성(Scalability)과 성능(Performance)을 결정짓는 핵심 요소입니다.

---

## Abstract Base Class

모든 그래프 스토리지 백엔드는 `BaseGraphStorage` 추상 클래스를 상속받아 구현됩니다. 주요 인터페이스는 다음과 같습니다:
- `upsert_node(node_id, node_data)`: 엔티티 저장/업데이트
- `upsert_edge(source, target, edge_data)`: 관계 저장/업데이트
- `get_node(node_id)`, `get_edge(source, target)`: 조회
- `get_node_edges(source_node)`: 특정 엔티티의 이웃 탐색 (Local 모드에서 사용)

---

## Supported Backends

운영 환경(프로토타이핑 vs 프로덕션)에 따라 알맞은 백엔드를 선택할 수 있습니다.

### 1. NetworkX (Default / In-Memory)
- **특징**: 외부 데이터베이스 설치가 필요 없는 순수 Python 메모리 기반 그래프 라이브러리입니다.
- **저장 방식**: 시스템이 종료될 때 GraphML 포맷의 파일(`graph_chunk_entity_relation.graphml`)로 로컬 디스크에 저장됩니다.
- **Best For**: 로컬 개발, 프로토타이핑, 소규모 문서 셋 (수천 개 이하의 노드).

### 2. Neo4j
- **특징**: 전 세계적으로 가장 널리 쓰이는 강력한 Property Graph Database입니다.
- **장점**: 수백만 개 이상의 노드와 엣지를 효율적으로 처리하며, Cypher 쿼리를 통해 복잡한 탐색이 가능합니다. 시각화 도구(Neo4j Bloom, Browser)를 기본 제공합니다.
- **Best For**: 엔터프라이즈 환경의 대규모 데이터 프로덕션.

### 3. PostgreSQL (with Apache AGE)
- **특징**: 기존 관계형 데이터베이스인 PostgreSQL에 Apache AGE 익스텐션을 설치하여 그래프 기능을 추가한 형태입니다.
- **장점**: LightRAG는 PostgreSQL 하나로 Graph, Vector(pgvector), KV, DocStatus 스토리지를 **모두 통합(All-in-one)** 하여 사용할 수 있습니다. 아키텍처가 단순해집니다.
- **Best For**: 이미 PostgreSQL을 운영 중이며, 인프라 복잡도를 낮추고 싶은 팀.

### 4. Memgraph
- **특징**: Neo4j와 호환(Cypher 및 Bolt 프로토콜 지원)되면서도 C++로 작성되어 In-Memory 기반으로 매우 빠른 속도를 자랑하는 그래프 DB입니다.
- **Best For**: 실시간 그래프 분석 및 극단적인 성능이 요구되는 환경.

---

## Setup Example (Neo4j)

```python
import os
from lightrag import LightRAG

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"

rag = LightRAG(
    working_dir="./storage",
    graph_storage="Neo4JStorage", # NetworkX 대신 Neo4j 지정
    # ...
)
```

## Workspace Isolation

동일한 DB 내에서 여러 프로젝트나 사용자의 데이터를 격리(Isolation)해야 할 때, LightRAG는 `workspace` 파라미터를 사용합니다.
- **Neo4j**: 노드의 Label이나 속성에 workspace 접두사를 추가하여 논리적으로 분리합니다.
- **NetworkX**: `working_dir` 하위에 별도의 폴더나 파일로 물리적으로 분리됩니다.