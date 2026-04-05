# LightRAG Architecture

LightRAG(Retrieval-Augmented Generation) 시스템의 전체적인 구조, 핵심 개념 및 모듈별 파일 구성에 대한 문서입니다.

## 🏗️ Architecture (How It Works)

| Document | Description |
|----------|-------------|
| [Overview](overview.md) | System design and components (시스템 설계 및 컴포넌트) |
| [Data Flow](overview.md#data-flow) | How documents flow through the system (문서 데이터 흐름) |
| [Modules Reference](modules/index.md) | Python 파일 및 모듈 설명 (EdgeQuake의 Crate Reference에 해당) |

## 💡 Core Concepts (Theory)

| Concept | Description |
|---------|-------------|
| [Graph-RAG](core-concepts.md#graph-rag) | Why knowledge graphs enhance RAG (지식 그래프가 RAG를 향상시키는 이유) |
| [Entity Extraction](core-concepts.md#entity-extraction) | LLM-based entity recognition (LLM 기반 엔티티 및 관계 추출) |
| [Knowledge Graph](core-concepts.md#knowledge-graph) | Nodes, edges, and communities (노드, 엣지, 커뮤니티 구조) |
| [Hybrid Retrieval](core-concepts.md#hybrid-retrieval) | Combining vector and graph search (벡터 검색과 그래프 검색의 결합) |

## 🔬 Deep Dives (Advanced)

| Article | Description |
|---------|-------------|
| [Query Modes](deep-dives.md#query-modes) | Local, Global, Hybrid, Mix, Naive 모드 설명 및 장단점 |
| [Community Detection](deep-dives.md#community-detection) | 클러스터링을 통한 커뮤니티 요약 (Global 모드용) |
| [Storage Layer](deep-dives.md#storage-layer) | KV, Vector, Graph, Doc Status 저장소 설계 |

---

### Global Mode Overview

LightRAG에서 전체적인 주제나 커뮤니티(Community) 단위의 요약을 생성하는 **Global Mode**의 구조입니다.

```text
+-------------------------------------------------------------+
|                        GLOBAL MODE                          |
|                                                             |
|  Query: "Summarize early 20th century physics"              |
|                                                             |
|  1. Find entities matching query                            |
|  2. Identify community clusters (via Graph clustering)      |
|  3. Aggregate community-level summaries                     |
|                                                             |
|  +-------------------------------------------------------+  |
|  |             Community: Physics Pioneers               |  |
|  |                                                       |  |
|  |  +-------+   +----------+   +--------+                |  |
|  |  | CURIE |---| EINSTEIN |---| PLANCK |                |  |
|  |  +-------+   +----------+   +--------+                |  |
|  |      |            |             |                     |  |
|  |      v            v             v                     |  |
|  |  +-------------------------------------------------+  |  |
|  |  | Community Summary: "Early 20th century          |  |  |
|  |  | physics was defined by discoveries in           |  |  |
|  |  | radioactivity, relativity, and quantum          |  |  |
|  |  | mechanics..."                                   |  |  |
|  |  +-------------------------------------------------+  |  |
|  +-------------------------------------------------------+  |
|                                                             |
|  Pro: Big picture, thematic understanding                   |
|  Con: May miss specific details                             |
+-------------------------------------------------------------+
```
