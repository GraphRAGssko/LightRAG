# Chunking Strategies

> **How LightRAG Splits Documents for Processing**

Chunking(청킹)은 긴 문서를 LLM과 임베딩 모델이 처리할 수 있는 크기로 자르는 과정입니다. LightRAG의 청킹 전략은 토큰 기반의 분할과 오버랩(Overlap)을 통해 정보의 손실을 방지합니다.

---

## Why Chunking Matters

```text
┌─────────────────────────────────────────────────────────────────┐
│                 THE CHUNKING PROBLEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  100페이지 짜리 PDF 문서 (약 50,000 토큰)                         │
│                                                                 │
│  ❌ 전체 문서를 한 번에 임베딩 모델에 넣을 수 없음 (Max ~8K)      │
│  ❌ 문맥이 너무 길어 LLM이 중간의 중요 엔티티를 놓침 (Lost in Middle)│
│  ❌ 질문과 무관한 내용이 너무 많이 섞여 검색 품질(Relevance) 하락 │
│                                                                 │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Solution: 적절한 크기로 분할 (Chunking)                    │   │
│  │                                                          │   │
│  │ [Chunk 1: 1000 tokens] [Chunk 2: 1000 tokens] ...        │   │
│  │                                                          │   │
│  │ ✅ 각 청크가 임베딩 모델의 허용치 내에 들어옴                 │
│  │ ✅ 검색 시 정확히 연관된 부분(청크)만 추출 가능               │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Token-Based Chunking with Overlap

LightRAG의 기본 청킹 방식은 지정된 토큰 수를 기준으로 텍스트를 자르되, 경계면에 있는 문맥이 끊기지 않도록 **Overlap(겹침)** 구간을 두는 것입니다.

### Overlap: Why It Matters

```text
WITHOUT OVERLAP (Bad):
[Chunk 1]: "Sarah Chen은 Microsoft에서 일합니다. 그녀는 Azure"
                                              ↑ (Cut)
[Chunk 2]: "플랫폼을 개발했습니다."

-> 문제: 2번 청크만 검색되었을 때 "그녀"가 누구인지 알 수 없고, "Azure 플랫폼"이라는 단어가 쪼개집니다.

WITH OVERLAP (Good):
[Chunk 1]: "Sarah Chen은 Microsoft에서 일합니다. 그녀는 Azure"
[Chunk 2]: "그녀는 Azure 플랫폼을 개발했습니다."

-> 해결: Overlap 구간 덕분에 2번 청크에서도 "그녀"와 "Azure"의 맥락이 보존됩니다.
```

### Configuration in LightRAG

청킹 사이즈는 LightRAG 클래스를 초기화하거나 텍스트를 삽입(`ainsert`)할 때 설정할 수 있습니다.

```python
from lightrag import LightRAG

rag = LightRAG(
    working_dir="./storage",
    chunk_token_size=1200,   # 기본 청크 크기 (토큰)
    chunk_overlap_token_size=100, # 오버랩 크기 (토큰)
    # ... 기타 설정
)
```

**가이드라인:**
- **1200 토큰**: LLM이 엔티티와 관계를 온전히 파악할 수 있으면서도 임베딩 품질이 유지되는 최적의 균형점입니다.
- **100 토큰 오버랩**: 약 8% 수준의 오버랩으로, 청크 경계에 걸친 핵심 단어나 지시어가 잘려나가는 것을 방지합니다.

## Best Practices

1. **문서의 종류에 따른 조정**: 
   - 긴 소설이나 산문: 청크 크기를 1500~2000 수준으로 늘려 넓은 문맥을 담는 것이 좋습니다.
   - FAQ, 로그, 짧은 기사: 청크 크기를 500~800 수준으로 줄여 검색의 정밀도(Precision)를 높이는 것이 유리합니다.
2. **임베딩 모델 한계 확인**: 사용하는 임베딩 모델(예: OpenAI의 `text-embedding-3-large`의 경우 최대 8191 토큰)의 최대 컨텍스트 창을 넘지 않도록 설정해야 합니다.