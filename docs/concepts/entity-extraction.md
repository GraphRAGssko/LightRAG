# Entity Extraction

> **Entity extraction uses LLMs to identify people, organizations, concepts, and
> their relationships from unstructured text.**

엔티티 추출(Entity Extraction) 과정은 LightRAG 파이프라인에서 텍스트를 구조화된 지식 그래프로 변환하는 가장 핵심적이고 기초적인 단계입니다.

---

## What is Entity Extraction?

엔티티 추출 프로세스는 다음과 같은 절차로 이루어집니다:

1. **Identifying (식별)**: 문서 내에서 유의미한 엔티티(인물, 장소, 개념 등) 찾기
2. **Classifying (분류)**: 추출된 엔티티의 범주/타입 분류 (예: PERSON, ORGANIZATION, CONCEPT)
3. **Describing (설명)**: 텍스트 문맥을 기반으로 해당 엔티티의 상세 속성 묘사
4. **Connecting (연결)**: 명시적인 관계(Relationship)를 통해 서로 다른 엔티티 잇기

LightRAG는 대규모 언어 모델(LLM)을 일종의 **지식 엔지니어(Knowledge Engineer)**로 활용하여 이 복잡한 과정을 자동화합니다.

---

## The Role of LLMs

전통적인 NLP 파이프라인은 정규식 등 룰(Rule) 기반 추출기나 특수목적에 맞게 학습된 NER(Named Entity Recognition) 모델을 사용했습니다. LightRAG는 여기서 LLM을 활용함으로써 엄청난 이점을 얻습니다:

| Approach        | Pros                               | Cons                     |
| --------------- | ---------------------------------- | ------------------------ |
| **Rules (규칙)** | 매우 빠르고 예측 가능한 결과       | 깨지기 쉽고 범용성 떨어짐 |
| **Trained NER** | 학습된 특정 데이터 카테고리 내 정확함 | 대규모 학습 데이터셋 필요 |
| **LLM-based**   | 도메인 무관 적용, 매우 풍부한 설명(Context) 생성 | 상대적으로 느리며 API 비용 발생 |

LLM 추출이 제공하는 강력한 장점:
- **Zero-shot extraction**: 학습 파이프라인 없이 완전히 새로운 도메인의 문서도 즉시 분석합니다.
- **Rich descriptions**: "단순한 라벨"이 아니라, 그 엔티티가 문맥상에서 가지는 "의미와 상태"를 설명으로 함께 남깁니다.
- **Relationship inference**: 명시적 단어가 없더라도, 문맥상 존재하는 엔티티 간의 관계를 추론합니다.

---

## Entity Types

LightRAG는 기본적으로 문서에서 범용적인 엔티티들을 추출하도록 설계되어 있습니다. LLM 프롬프트에 의해 유연하게 추출됩니다:

```text
┌─────────────────────────────────────────────────────────────────┐
│                    COMMON ENTITY TYPES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PERSON        │ 사람, 개인, 캐릭터, 저자                        │
│  ORGANIZATION  │ 회사, 연구소, 단체, 소속 기관                   │
│  LOCATION      │ 장소, 지역, 좌표                                │
│  EVENT         │ 사건, 미팅, 컨퍼런스, 프로젝트 마일스톤         │
│  CONCEPT       │ 아이디어, 이론, 사상, 방법론                    │
│  TECHNOLOGY    │ 도구, 시스템 아키텍처, 플랫폼, 기술 스택        │
│  PRODUCT       │ 상품, 서비스, 출시 품목                         │
│  OTHER         │ 그 외 포괄적 범주                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

(사용자 프롬프트 구성을 통해 특정 도메인 - 의료, 법률 등 - 에 맞는 고유한 타입 추출로 유도할 수도 있습니다.)

---

## The Extraction Process

```text
┌─────────────────────────────────────────────────────────────────┐
│                EXTRACTION PIPELINE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐                                                    │
│  │   TEXT   │  "Dr. Sarah Chen leads the AI team at Quantum      │
│  │  CHUNK   │   Dynamics Lab. Her research on neural networks    │
│  │          │   has been cited 500 times."                       │
│  └────┬─────┘                                                    │
│       │                                                          │
│       v                                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    LLM EXTRACTION                         │   │
│  │  System: "You are a Knowledge Graph Specialist..."       │   │
│  │  User: "Extract entities and relationships from..."      │   │
│  └──────────────────────────────────────────────────────────┘   │
│       │                                                          │
│       v                                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    RAW OUTPUT (JSON/Strings)              │   │
│  │  ("SARAH_CHEN", "PERSON", "Lead researcher...")           │   │
│  │  ("QUANTUM_LAB", "ORGANIZATION", "Research institution")  │   │
│  │  ("NEURAL_NETWORKS", "CONCEPT", "ML approach")            │   │
│  │  ("SARAH_CHEN", "QUANTUM_LAB", "works_at", "...", ...)    │   │
│  └──────────────────────────────────────────────────────────┘   │
│       │                                                          │
│       v                                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    PARSED RESULT                          │   │
│  │  Entities: 3 nodes added                                  │   │
│  │  Relationships: 3 edges connected                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Relationship Extraction

관계 추출은 엔티티 노드들 사이를 Edge(엣지)로 연결하는 작업입니다:

```text
┌───────────────┐        WORKS_AT         ┌───────────────┐
│  SARAH_CHEN   │────────────────────────▶│  QUANTUM_LAB  │
│   (PERSON)    │                         │ (ORGANIZATION)│
└───────────────┘                         └───────────────┘
        │
        │ RESEARCHES
        │
        v
┌───────────────┐
│NEURAL_NETWORKS│
│   (CONCEPT)   │
└───────────────┘
```

LLM을 통해 구성된 각각의 관계 Edge는 다음 정보를 필수로 포함합니다:
- **Source Entity (시작 노드)**: 주체가 되는 노드
- **Target Entity (도착 노드)**: 대상이 되는 노드
- **Keywords/Type**: 관계를 축약하는 범주 (예: `WORKS_AT`, `RESEARCHES`)
- **Description**: 텍스트 원문에 기재된 뉘앙스를 반영하는 상세한 관계 설명

---

## Entity Normalization & Merging

추출 이후엔 그래프 내에서 일관성을 유지하기 위해 **정규화(Normalization)** 와 **병합(Merging)** 과정이 수반됩니다.

| Raw Input | Normalized Behavior |
|---|---|
| `"John Doe"` vs `"john doe"` | 같은 노드로 식별 |
| `"Quantum Lab"` vs `"Quantum Dynamics Lab"` | 프로파일링 단계를 거쳐 필요 시 설명 보강/병합 |

**Why normalize?**
- 노드 중복과 파편화를 방지합니다.
- 여러 문서에서 "John Doe"가 언급되었을 때, 이를 단일 노드로 합침으로써 **문서와 문서 사이의 맥락을 연결(Cross-document linkage)** 할 수 있게 됩니다.

---

## Learn More
- 전체 파이프라인 아키텍처: [LightRAG Algorithm](lightrag-algorithm.md)
- 추출된 지식 그래프를 활용한 검색 구조: [Deep Dives](../architecture/deep-dives.md)
