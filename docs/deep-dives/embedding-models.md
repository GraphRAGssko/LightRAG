# Embedding Models

> **Translating Text and Knowledge into Vector Space**

임베딩(Embedding) 모델은 텍스트(단어, 문장, 문서 등)를 고차원 벡터(Vector) 배열로 변환하는 역할을 합니다. LightRAG는 텍스트 청크, 엔티티, 관계 설명 등 모든 주요 데이터를 임베딩하여 Vector Storage에 저장합니다.

---

## Role of Embeddings in LightRAG

Graph-RAG 구조에서도 벡터 임베딩은 필수적입니다.
1. **시작점 찾기 (Entry Point)**: 사용자가 질문을 던졌을 때, 지식 그래프의 어느 노드(엔티티)부터 탐색을 시작할지 결정하기 위해 질문과 가장 의미적으로 유사한 노드를 벡터 유사도(Cosine Similarity 등)로 찾습니다.
2. **청크 매칭**: Naive 모드나 Hybrid/Mix 모드에서 텍스트 원문을 직접 검색할 때 사용됩니다.
3. **커뮤니티 매칭**: Global 모드에서 질문과 가장 잘 맞는 커뮤니티 요약본을 찾을 때 사용됩니다.

---

## Configuration

LightRAG에서 임베딩 함수는 `@wrap_embedding_func_with_attrs` 데코레이터를 사용하여 차원(Dimension) 수와 최대 토큰 한도를 명시해야 합니다.

```python
from lightrag.utils import wrap_embedding_func_with_attrs
from lightrag.llm.openai import openai_embed

# 차원수와 최대 토큰 사이즈 지정
@wrap_embedding_func_with_attrs(embedding_dim=1536, max_token_size=8192)
async def custom_embed(texts: list[str]) -> np.ndarray:
    return await openai_embed.func(texts, model="text-embedding-3-large")

rag = LightRAG(
    working_dir="./storage",
    embedding_func=custom_embed,
    # ...
)
```

**⚠️ 주의사항**: 임베딩 모델을 중간에 변경하면 차원 수가 달라져 Vector Storage의 기존 데이터와 호환되지 않습니다. 모델을 변경하려면 기존 벡터 저장소를 초기화해야 합니다.

---

## Recommended Models

| Provider | Model | Dimension | Best For |
|---|---|---|---|
| **OpenAI** | `text-embedding-3-large` | 3072 (또는 1536) | 클라우드 기반의 최상위 성능, 다국어 지원 |
| **OpenAI** | `text-embedding-3-small` | 1536 | 비용 효율적이고 빠른 클라우드 임베딩 |
| **BAAI** | `bge-m3` | 1024 | 오프라인/로컬 환경 최고의 다국어 모델 |
| **Nomic** | `nomic-embed-text` | 768 | 완전히 열린 가중치를 가진 고성능 로컬 모델 |

## Embedding and Reranking

질문과 임베딩 간의 거리(유사도)는 대략적인 관련성만을 측정합니다. LightRAG의 **Mix 모드** 등에서는 검색의 정확도를 극대화하기 위해 검색된 Top-K 결과를 다시 평가하는 **Reranker(재정렬 모델)**의 사용을 적극 권장합니다 (예: `BAAI/bge-reranker-v2-m3`). Reranker는 두 텍스트를 동시에 입력받아 실제 의미적 연관성 점수를 다시 계산합니다.