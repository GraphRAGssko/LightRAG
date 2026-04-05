# Core Concepts

## Graph-RAG
기존의 RAG는 텍스트 청크를 단순히 Vector로 변환하여 의미(유사도) 기반으로만 검색합니다(Naive RAG). 반면 Graph-RAG는 텍스트에 등장하는 개념(엔티티)과 그 관계를 지식 그래프(Knowledge Graph)로 구성하여, 엔티티 간의 맥락과 구조적 의미까지 검색에 반영함으로써 복잡한 추론 및 넓은 범위의 질문에 높은 품질의 답변을 제공합니다.

## Entity Extraction
문서가 들어오면 LLM을 사용하여 텍스트 내의 주요 엔티티(사람, 개념, 조직, 이벤트 등)와 그 엔티티 간의 관계를 추출합니다. 
예: "Einstein worked at Princeton" -> `(Einstein) -[worked_at]-> (Princeton)`

## Knowledge Graph
추출된 데이터는 그래프 형태를 이룹니다:
- **Nodes (노드)**: 추출된 엔티티. 각 노드는 이름과 상세 설명을 가집니다.
- **Edges (엣지)**: 엔티티 간의 관계. 각 엣지 역시 어떻게 연결되어 있는지에 대한 설명을 가집니다.
- **Communities (커뮤니티)**: 그래프 상에서 촘촘하게 연결된 노드들의 군집(Cluster). LightRAG는 이 커뮤니티 단위로 요약을 생성해 두어, 거시적인 질문에 빠르게 답할 수 있게 합니다.

## Hybrid Retrieval
Graph-RAG의 강력함은 여러 방식을 섞어 쓰는 데에 있습니다. 벡터 기반의 유사도 검색(Vector Search)을 통해 시작점 엔티티를 찾고, 지식 그래프 검색(Graph Search)을 통해 그 주변 문맥과 이웃 엔티티를 함께 가져와 결합(Hybrid)하여 LLM에 제공합니다.
