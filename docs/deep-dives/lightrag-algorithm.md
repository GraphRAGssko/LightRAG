# LightRAG Algorithm Deep-Dive

> **Understanding Graph-Augmented Retrieval: From First Principles to Implementation**

LightRAG은 기존의 RAG(Retrieval-Augmented Generation) 시스템이 갖는 한계를 극복하기 위해 그래프 기반의 문서 색인과 이중 검색(Dual-Level Retrieval) 모델을 도입한 최첨단 검색 알고리즘입니다. 본 문서는 시스템의 기반 원리부터 파이프라인의 각 단계별 동작 방식을 상세하게 설명합니다.

---

## Table of Contents

1. [Why Graph-RAG? First Principles](#why-graph-rag-first-principles)
2. [The LightRAG Innovation](#the-lightrag-innovation)
3. [Algorithm Walkthrough](#algorithm-walkthrough)
4. [Entity Extraction in Detail](#entity-extraction-in-detail)
5. [Dual-Level Retrieval](#dual-level-retrieval)
6. [Query Modes Explained](#query-modes-explained)
7. [References](#references)

---

## Why Graph-RAG? First Principles

### The Problem with Traditional RAG

전통적인 RAG(Naive RAG)는 단순한 구조를 따릅니다:

```text
┌─────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL RAG (Naive)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Documents ──> Chunks ──> Embeddings ──> Vector DB              │
│                                                                 │
│  Query ──> Embedding ──> Top-K Similar Chunks ──> LLM Answer    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

이러한 방식은 단순한 사실 확인에는 적합하지만, 복잡한 연결 고리를 묻는 질문에는 실패하기 쉽습니다:

**Example Query**: *"Sarah Chen의 신경망 연구가 Quantum Dynamics Lab 동료들에게 어떤 영향을 미쳤는가?"*

Naive RAG는 다음과 같은 흩어진 문맥의 청크들을 반환할 것입니다:
1. "Sarah Chen"이 언급된 청크
2. "신경망(neural networks)"에 관한 청크
3. "Quantum Dynamics Lab"을 언급한 청크

시스템은 조각난 청크들을 **논리적으로 연결(disconnect)** 하지 못하며 다음을 이해하지 못합니다:
- Sarah Chen이 Quantum Lab에서 **일한다는 사실**
- 그녀의 연구가 동료들과 **어떻게 이어지는지**
- 여러 문서를 관통하는 **영향의 흐름(influence chain)**

### Why Graphs Solve This

그래프(Graph)의 핵심은 **관계(Relationship)** 에 있습니다.

```text
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE GRAPH STRUCTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│           ┌─────────────┐                                       │
│           │ SARAH_CHEN  │                                       │
│           │   (PERSON)  │                                       │
│           └──────┬──────┘                                       │
│                  │                                              │
│      ┌───────────┼───────────┐                                  │
│      │           │           │                                  │
│      v           v           v                                  │
│  ┌───────┐  ┌─────────┐  ┌──────────────────┐                   │
│  │WORKS_AT  │RESEARCHES  │COLLABORATES_WITH                     │
│  └───┬───┘  └────┬────┘  └────────┬─────────┘                   │
│      │           │               │                              │
│      v           v               v                              │
│ ┌─────────────┐ ┌──────────────┐ ┌─────────┐                    │
│ │QUANTUM_LAB  │ │NEURAL_NETWORK│ │BOB_SMITH│                    │
│ │ (ORG)       │ │  (CONCEPT)   │ │ (PERSON)│                    │
│ └─────────────┘ └──────────────┘ └─────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

그래프를 활용하면 우리는:
1. **관계를 추적**할 수 있습니다: Sarah → works_at → Quantum Lab
2. **연결성을 발견**할 수 있습니다: Sarah → collaborates_with → Bob
3. **흐름을 파악**할 수 있습니다: Sarah의 연구 → used_by → Bob의 연구

### The Key Insight

> **Entities are the bridge between documents.** (엔티티는 문서 간의 다리 역할을 합니다)
>
> 동일한 엔티티("Sarah Chen")가 여러 문서에 걸쳐 등장할 때, 지식 그래프는 이 공유 노드를 통해 흩어진 문서들을 하나의 거대한 문맥으로 연결합니다.

---

## The LightRAG Innovation

LightRAG(arxiv:2410.05779) 논문에서 제시하는 3가지 핵심 혁신 포인트입니다:

### 1. Graph-Enhanced Text Indexing
텍스트 청크를 단순히 저장하는 대신, LightRAG는 다음을 수행합니다:
- 텍스트 내에서 **엔티티(Entities)** (사람, 조직, 개념) 추출
- 엔티티 간의 **관계(Relationships)** 추출
- 이 추출물들을 바탕으로 **지식 그래프(Knowledge Graph)** 구성

### 2. Dual-Level Retrieval
LightRAG는 두 가지 관점에서 정보를 탐색합니다:

| Level | Focus | Best For |
|---|---|---|
| **Low-Level (Local)** | 특정 엔티티와 주변의 직접적인 관계 | "Sarah Chen은 누구인가?" |
| **High-Level (Global)** | 광범위한 주제와 커뮤니티 흐름 | "인공지능 연구의 주요 트렌드는 무엇인가?" |

### 3. Incremental Updates
전체 그래프 커뮤니티 구조를 매번 다시 빌드해야 하는 방식(예: MS GraphRAG)과 달리, LightRAG는:
- 문서가 추가될 때마다 독립적으로 처리
- 새롭게 추출된 엔티티가 기존 그래프와 **병합(merge)**
- **전체 재색인(Full reindex) 불필요**

---

## Algorithm Walkthrough

### The Complete Pipeline

```text
┌─────────────────────────────────────────────────────────────────┐
│                 LIGHTRAG ALGORITHM PIPELINE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     INGESTION PHASE                      │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │   Document ──┬──> Preprocess ──> Chunk ──> Extract       │   │
│  │              │                      │                    │   │
│  │              │                      v                    │   │
│  │              │               ┌─────────────┐             │   │
│  │              │               │ LLM Entity  │             │   │
│  │              │               │ Extraction  │             │   │
│  │              │               └──────┬──────┘             │   │
│  │              │                      │                    │   │
│  │              │        ┌─────────────┼─────────────┐      │   │
│  │              │        │             │             │      │   │
│  │              │        v             v             v      │   │
│  │              │   ┌────────┐   ┌──────────┐   ┌────────┐  │   │
│  │              │   │Entities│   │Relations │   │Chunks  │  │   │
│  │              │   └───┬────┘   └────┬─────┘   └───┬────┘  │   │
│  │              │       │             │             │       │   │
│  │              v       v             v             v       │   │
│  │         ┌────────────────────────────────────────────┐   │   │
│  │         │   STORAGE LAYER (KV, Vector, Graph DBs)    │   │   │
│  │         └────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      QUERY PHASE                         │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │   Query ──> Keywords ──> Dual-Level Retrieval            │   │
│  │                               │                          │   │
│  │               ┌───────────────┼───────────────┐          │   │
│  │               │               │               │          │   │
│  │               v               v               v          │   │
│  │         ┌──────────┐   ┌──────────┐   ┌──────────┐       │   │
│  │         │ Entities │   │Relations │   │  Chunks  │       │   │
│  │         └────┬─────┘   └────┬─────┘   └────┬─────┘       │   │
│  │              │              │              │             │   │
│  │              └──────────────┼──────────────┘             │   │
│  │                             │                            │   │
│  │                             v                            │   │
│  │                    ┌────────────────┐                    │   │
│  │                    │ Context Fusion │                    │   │
│  │                    └───────┬────────┘                    │   │
│  │                            │                             │   │
│  │                            v                             │   │
│  │                    ┌────────────────┐                    │   │
│  │                    │  LLM Answer    │                    │   │
│  │                    └────────────────┘                    │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Document Chunking
입력 문서는 LLM이 처리할 수 있는 적절한 크기로 분할됩니다 (일반적으로 Token 단위 분할 및 Overlap 허용). `lightrag/operate.py` 에서 청킹 로직을 처리합니다.

### Step 2: Entity Extraction via LLM
LLM 프롬프트를 사용하여 텍스트에서 엔티티 및 관계를 추출합니다. 파싱하기 쉬운 특수 포맷을 사용하여 데이터의 누락 없이 그래프 요소를 식별합니다.

### Step 3: Entity Normalization
유사하거나 같은 엔티티가 여러 표현으로 추출되는 것을 막기 위해 병합 과정을 거칩니다 ("John Doe" == "JOHN_DOE").

### Step 4: Graph & Storage Construction
- **Graph Storage**: 노드(엔티티)와 엣지(관계)가 저장되며, 커뮤니티 계층 구조가 계산됩니다.
- **Vector Storage**: 의미론적(Semantic) 검색을 위해 추출된 내용의 임베딩 값이 저장됩니다.
- **KV Storage**: 원본 텍스트 매핑 및 상세 설명을 유지합니다.

---

## Dual-Level Retrieval

### Low-Level Retrieval (Entity-Centric / Local Mode)
질문에서 시작되는 구체적인 엔티티 노드와 인접한 이웃 노드(1-hop neighbors)를 중점적으로 탐색합니다.

```text
Query: "What is Sarah Chen's research about?"

Low-Level Retrieval:
┌──────────────────────────────────────────────────────────────┐
│     ┌───────────────┐                                        │
│     │  SARAH_CHEN   │ ← Direct entity match                  │
│     │   (PERSON)    │                                        │
│     └───────┬───────┘                                        │
│             │                                                │
│    ┌────────┼────────────┬─────────────────┐                 │
│    v        v            v                 v                 │
│ ┌──────┐ ┌────────┐ ┌─────────┐ ┌────────────────┐           │
│ │WORKS │ │RESEARCHES│ │PUBLISHED│ │COLLABORATES_WITH         │
│ └──┬───┘ └───┬────┘ └────┬────┘ └───────┬────────┘           │
│    v         v           v              v                    │
│ ┌──────┐ ┌────────────┐ ┌──────┐ ┌──────────┐                │
│ │ LAB  │ │NEURAL_NETS │ │PAPER │ │BOB_SMITH │                │
│ └──────┘ └────────────┘ └──────┘ └──────────┘                │
│                                                              │
│ Returns: Entity descriptions + 1-hop neighbors               │
└──────────────────────────────────────────────────────────────┘
```

### High-Level Retrieval (Topic-Centric / Global Mode)
커뮤니티(Community) 요약 기반의 거시적(High-Level) 주제를 파악합니다.

```text
Query: "What are the main AI research trends?"

High-Level Retrieval:
┌──────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              TOPIC CLUSTER: "AI RESEARCH"               │ │
│  │                                                         │ │
│  │  Key themes:                                            │ │
│  │  • Neural network architectures                         │ │
│  │  • Machine learning optimization                        │ │
│  │  • Deep learning applications                           │ │
│  │                                                         │ │
│  │  Related entities: 45                                   │ │
│  │  Related relationships: 128                             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  Uses global keywords to match relationship clusters         │
│  Returns: Aggregated summaries + theme keywords              │
└──────────────────────────────────────────────────────────────┘
```

---

## Query Modes Explained

LightRAG 시스템에서 지원하는 핵심 쿼리 모드들입니다:

| Mode       | Vector Search | Graph Traversal         | Best For               |
| ---------- | ------------- | ----------------------- | ---------------------- |
| **Naive**  | ✅ Yes        | ❌ No                   | 매우 직관적인 사실 확인 (전통적 RAG) |
| **Local**  | ✅ Yes        | ✅ Entities + neighbors | 특정 대상("Who/What is X?")의 주변 문맥 확인 |
| **Global** | ❌ No         | ✅ Community summaries  | "전체 주제나 트렌드가 무엇인가?" |
| **Hybrid** | ✅ Yes        | ✅ Both approaches      | 복합적인 컨텍스트 요구 질의 (Local + Global 결합) |
| **Mix**    | ✅ Weighted   | ✅ Weighted             | 텍스트 벡터 검색 결과와 그래프를 모두 섞어 프롬프트를 구성 |

`mix` 모드는 Reranker와 결합하여 사용 시 LightRAG에서 가장 강력하고 추천되는 검색 성능을 보여줍니다.

---

## References

1. **LightRAG Paper**: Guo et al., "LightRAG: Simple and Fast Retrieval-Augmented Generation", arXiv:2410.05779, 2024
2. **GraphRAG Paper**: Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization", arXiv:2404.16130, 2024
