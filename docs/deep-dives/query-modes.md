# Query Modes Deep-Dive

> **Understanding LightRAG's Multi-Strategy Retrieval System**

LightRAG은 질문의 의도와 필요한 문맥의 범위에 따라 최적의 검색을 수행할 수 있도록 5가지의 쿼리 모드를 제공합니다. 이 문서는 각 모드가 어떻게 동작하며, 언제 어떤 모드를 선택해야 하는지 설명합니다.

---

## Table of Contents
1. [Why Multiple Modes?](#why-multiple-modes)
2. [Mode Overview](#mode-overview)
3. [Naive Mode](#naive-mode)
4. [Local Mode](#local-mode)
5. [Global Mode](#global-mode)
6. [Hybrid Mode](#hybrid-mode)
7. [Mix Mode](#mix-mode)

---

## Why Multiple Modes?

사용자의 질문은 그 성격에 따라 필요한 탐색 전략이 다릅니다.

| Question | Optimal Strategy |
|---|---|
| "LightRAG의 청킹 사이즈는 몇인가?" | **Vector search** - 특정 사실이나 수치를 포함한 청크를 바로 찾습니다. |
| "Sarah Chen의 연구가 AI 랩에 미친 영향은?" | **Graph traversal** - 엔티티(Sarah, AI Lab) 간의 관계를 추적합니다. |
| "이 문서들이 다루는 핵심 주제는 무엇인가?" | **Community detection** - 전체적인 토픽 클러스터를 요약합니다. |
| "그래프 검색의 원리와 전체적인 아키텍처를 설명해줘" | **Both** - 구체적 사실과 거시적 흐름을 모두 필요로 합니다. |

단일 검색 전략으로는 이 모든 질문에 완벽하게 대답할 수 없습니다. LightRAG는 질문의 스코프에 맞춰 가장 적절한 모드를 선택할 수 있게 합니다.

---

## Mode Overview

| Mode       | Vector Search | Graph Traversal | Best For                        |
| ---------- | :-----------: | :-------------: | ------------------------------- |
| **Naive**  |      ✅       |       ❌        | 단순한 사실 확인, 키워드 검색 |
| **Local**  |      ✅       |       ✅        | 특정 엔티티 중심의 심층 질문 |
| **Global** |      ❌       |       ✅        | 거시적인 테마나 주제 분석 |
| **Hybrid** |      ✅       |       ✅        | 복합적이고 다면적인 질문 |
| **Mix**    |      ✅       |       ✅        | (권장) Reranker를 활용한 최고 성능 검색 |

---

## Naive Mode

전통적인 RAG 방식과 동일하게, 지식 그래프를 배제하고 **문서 청크에 대한 벡터 유사도 검색(Vector Similarity Search)**만을 수행합니다.

- **장점**: 가장 빠르며 비용이 적게 듭니다. 구체적인 키워드가 있는 단순 사실 확인에 매우 강력합니다.
- **단점**: 여러 문서에 걸쳐 흩어진 논리적 연결고리를 파악하지 못합니다.

## Local Mode

질문과 관련된 특정 **엔티티(Entity)**들을 찾아내고, 해당 엔티티와 직접적으로 연결된 이웃 노드(1-hop neighbors)들을 그래프에서 가져옵니다.

- **어떻게 동작하는가**: 
  1. 쿼리에서 키워드 추출 후 Vector DB에서 관련 엔티티 검색
  2. Graph DB에서 해당 엔티티와 연결된 엣지(관계) 탐색
  3. 관련 텍스트 청크와 함께 LLM에 컨텍스트로 제공
- **언제 사용하는가**: "X는 누구인가?", "A와 B는 어떤 관계인가?"와 같이 타겟이 명확한 질문.

## Global Mode

그래프 전체의 **커뮤니티(Community)** 구조를 활용합니다. 각 커뮤니티는 미리 LLM을 통해 요약(Summary)되어 있습니다. 질문이 주어지면, 이 커뮤니티 요약본들을 검색하여 큰 그림을 그립니다.

- **어떻게 동작하는가**:
  1. 질문을 분석하여 넓은 범위의 키워드 식별
  2. 사전 생성된 커뮤니티 리포트(Community Summaries) 중 관련성 높은 것들 검색
  3. 세부 엔티티 대신 거시적인 요약본들을 모아 최종 답변 생성
- **언제 사용하는가**: "전체적인 주제가 뭐야?", "이 시스템의 핵심 흐름을 요약해줘"

## Hybrid Mode

`Local` 모드의 구체성과 `Global` 모드의 거시적 맥락을 **동시에 결합(Fusion)**합니다. 

- **장점**: 좁은 문맥과 넓은 문맥을 한 번에 LLM에 제공하여 가장 풍부한 답변을 생성할 수 있습니다.
- **단점**: 컨텍스트 토큰 소비량이 크고, 처리 속도가 비교적 느립니다.

## Mix Mode

LightRAG에서 가장 고도화된 모드로, 지식 그래프 검색 결과와 벡터 텍스트 청크 검색 결과를 가중치 기반으로 섞습니다. 

- **핵심 차별점**: **Reranker(재정렬 모델)** 와 결합할 때 최고의 성능을 발휘합니다. BAAI/bge-reranker-v2-m3 등과 함께 사용하여 수집된 모든 노드, 엣지, 청크들을 질문과의 관련성에 따라 랭킹을 매기고, Top-K만을 잘라내어 최적의 프롬프트를 구성합니다.
- **권장 사항**: 운영 환경에서 Reranker를 사용할 수 있다면 기본 모드로 설정하는 것을 권장합니다.