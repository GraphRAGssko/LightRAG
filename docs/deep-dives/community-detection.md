# Community Detection

> **How LightRAG Discovers Structure in Knowledge Graphs**

Community Detection(커뮤니티 탐지)은 지식 그래프 내에서 조밀하게 연결된 엔티티(노드)들의 군집을 찾아내는 과정입니다. LightRAG는 이를 통해 수많은 엔티티들을 그룹화하고, **Global Query** 모드에서 활용할 거시적인 주제 요약(Community Summaries)을 생성합니다.

---

## Why Community Detection?

개별 엔티티와 그들의 관계만으로는 숲을 보지 못하고 나무만 보게 될 수 있습니다.

| Purpose | Benefit |
|---|---|
| **Global Queries** | 수천 개의 노드를 다 보지 않고도, 군집별 요약을 통해 전체 테마 파악 가능 |
| **Noise Reduction** | 덜 중요한 연결고리를 배제하고 뚜렷한 주제를 형성하는 덩어리 식별 |
| **Hierarchical Understanding** | 문서가 내포하는 상위-하위 개념의 계층적 구조 파악 |

---

## How It Works in LightRAG

LightRAG는 기본적으로 Graph Storage 백엔드(예: NetworkX, Neo4j)를 통해 클러스터링 알고리즘을 실행합니다.

```text
┌─────────────────────────────────────────────────────────────────┐
│                    COMMUNITY DETECTION PIPELINE                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Graph Construction                                          │
│     문서에서 추출된 수많은 노드와 엣지들이 그래프를 이룸.          │
│                                                                 │
│  2. Partitioning (Louvain Method 등)                             │
│     알고리즘이 엣지의 가중치와 밀도를 계산하여 노드들을 묶음.      │
│                                                                 │
│  ┌─────────────────┐      ┌─────────────────┐                   │
│  │  Community 0    │      │  Community 1    │                   │
│  │                 │      │                 │                   │
│  │   A──────B      │      │   E──────F      │                   │
│  │   │ ╲    │      │      │   │ ╲    │      │                   │
│  │   C──────D      │      │   G──────H      │                   │
│  └─────────────────┘      └─────────────────┘                   │
│                                                                 │
│  3. Summary Generation (LLM)                                    │
│     각 커뮤니티에 속한 노드/엣지 설명을 모아 LLM에 전달.           │
│     -> "이 그룹은 [인공지능 모델의 성능 최적화]를 다룹니다..."       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### The Algorithm (Louvain)

주로 **Louvain Method**가 사용됩니다. 이 알고리즘은 네트워크의 Modularity(모듈성)를 최대화하는 방향으로 노드들을 병합해 나갑니다.
- **Phase 1**: 각 노드를 이웃 커뮤니티로 이동시키며 Modularity가 가장 크게 증가하는 곳으로 편입시킵니다.
- **Phase 2**: 형성된 커뮤니티를 하나의 슈퍼 노드(Super-node)로 취급하여 다시 Phase 1을 반복합니다.

이 방식을 통해 매우 빠르고 안정적으로 주제 그룹을 형성할 수 있습니다.

---

## Storage & Utilization

탐지된 커뮤니티와 그에 대한 LLM 요약본은 스토리지에 저장됩니다.

1. 사용자가 **Global Mode**로 질문을 던집니다.
2. LightRAG는 질문의 의미를 담은 임베딩이나 키워드를 통해 가장 관련성이 높은 커뮤니티(Community Summary)들을 찾습니다.
3. 해당 커뮤니티들의 텍스트 요약본들을 결합하여 최종 답변을 생성합니다.

이러한 구조 덕분에, 거대한 문서 집합에서도 "이 문서들의 주요 트렌드가 뭐야?" 같은 질문에 수초 내에 일관성 있는 거시적 답변을 내놓을 수 있습니다.