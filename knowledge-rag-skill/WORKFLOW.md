# Knowledge-RAG 工作流程图

## 整体架构

```mermaid
graph TB
    subgraph "用户层"
        User[用户]
    end

    subgraph "OpenClaw层"
        OC[OpenClaw AI]
        Intent[意图识别]
        Skill[RAG Skill]
        Response[响应生成]
    end

    subgraph "RAG服务层"
        API[FastAPI Server]
        Auth[认证中间件]
        Router[路由处理]
    end

    subgraph "核心服务层"
        Search[语义搜索服务]
        Chat[问答服务]
        BGE[向量化服务]
    end

    subgraph "数据层"
        Ollama[Ollama API<br/>bge-m3模型]
        DB[(PostgreSQL<br/>+ pgvector)]
        LLM[LLM服务<br/>可选]
    end

    User -->|提问| OC
    OC --> Intent
    Intent -->|需要知识库| Skill
    Intent -->|不需要| Response

    Skill --> API
    API --> Auth
    Auth --> Router
    Router --> Search
    Router --> Chat

    Search --> BGE
    Chat --> BGE
    BGE --> Ollama

    Search --> DB
    Chat --> DB
    Chat -.->|可选| LLM

    DB --> Router
    Router --> Skill
    Skill --> Response
    Response --> User
```

## RAG 问答详细流程

```mermaid
sequenceDiagram
    participant User as 👤 用户
    participant OC as 🤖 OpenClaw
    participant Skill as 🔌 RAG Skill
    participant API as 🚀 FastAPI
    participant BGE as 🧠 Ollama<br/>(bge-m3)
    participant DB as 💾 PostgreSQL<br/>(pgvector)
    participant LLM as 🌟 LLM服务

    User->>OC: 提问
    Note over OC: 意图识别

    alt 需要专业知识
        OC->>Skill: 调用 RAG Skill

        Skill->>API: POST /api/v1/knowledge/chat
        Note over API: 认证 app_id + app_secret

        API->>BGE: 问题向量化
        BGE->>BGE: 编码为 1024维向量<br/>(~50-100ms)
        BGE-->>API: 返回查询向量

        API->>DB: 向量相似度搜索<br/>SELECT ... ORDER BY<br/>embedding <=> query_vector
        Note over DB: 使用 HNSW 索引<br/>加速检索
        DB-->>API: 返回 Top-K 相关文档块

        API->>API: 构造 Prompt<br/>问题 + 相关上下文

        opt 集成 LLM
            API->>LLM: 调用大模型生成答案
            LLM-->>API: 生成的答案
        end

        API->>DB: 保存对话历史<br/>INSERT INTO chat_messages
        DB-->>API: 保存成功

        API-->>Skill: 返回答案 + 来源
        Skill->>Skill: 格式化结果
        Skill-->>OC: 返回格式化答案

        OC-->>User: 📚 返回答案 + 来源引用

    else 一般对话
        OC->>OC: 基于自身知识回答
        OC-->>User: 💬 直接回答
    end
```

## 语义搜索流程

```mermaid
sequenceDiagram
    participant OC as 🤖 OpenClaw
    participant Skill as 🔌 RAG Skill
    participant API as 🚀 FastAPI
    participant BGE as 🧠 Ollama
    participant DB as 💾 pgvector

    OC->>Skill: search(query, top_k=5)
    Skill->>API: POST /api/v1/knowledge/search

    API->>BGE: encode_query(query)
    BGE-->>API: query_vector [1024维]

    API->>DB: 向量相似度检索
    Note over DB: 计算余弦相似度<br/>1 - (embedding <=> query_vector)

    DB-->>API: Top-5 相关文档块
    Note over API: 每个结果包含:<br/>- chunk_text<br/>- document_title<br/>- similarity_score

    API-->>Skill: JSON 结果
    Skill->>Skill: 过滤低分结果<br/>(score < 0.7)
    Skill-->>OC: 格式化的搜索结果

    OC->>OC: 基于检索结果生成答案
    OC-->>User: 答案 + 参考来源
```

## 决策树：何时使用 RAG

```mermaid
graph TD
    Start([用户提问]) --> Q1{包含触发关键词?}

    Q1 -->|是| UseRAG[使用 RAG]
    Q1 -->|否| Q2{是专业知识问题?}

    Q2 -->|是| UseRAG
    Q2 -->|否| Q3{需要引用来源?}

    Q3 -->|是| UseRAG
    Q3 -->|否| Q4{知识库有相关内容?}

    Q4 -->|是| UseRAG
    Q4 -->|否| DirectAnswer[OpenClaw 直接回答]

    UseRAG --> ChooseAPI{选择接口}

    ChooseAPI -->|只需检索| SearchAPI[/api/v1/knowledge/search]
    ChooseAPI -->|需要完整答案| ChatAPI[/api/v1/knowledge/chat]

    SearchAPI --> Format1[OpenClaw 生成答案]
    ChatAPI --> Format2[直接返回 RAG 答案]

    Format1 --> End([返回给用户])
    Format2 --> End
    DirectAnswer --> End
```

## 数据流图

```mermaid
graph LR
    subgraph Input[输入]
        Q[用户问题]
    end

    subgraph Processing[处理流程]
        V[向量化<br/>1024维]
        S[相似度检索<br/>pgvector]
        R[排序&过滤<br/>Top-K]
        F[格式化输出]
    end

    subgraph Output[输出]
        A[答案]
        C[上下文]
        L[来源链接]
    end

    Q --> V
    V --> S
    S --> R
    R --> F
    F --> A
    F --> C
    F --> L
```

## 性能优化流程

```mermaid
graph TB
    Request[用户请求] --> Cache{缓存命中?}

    Cache -->|是| ReturnCache[返回缓存结果<br/>~10ms]
    Cache -->|否| Encode[向量编码<br/>50-100ms]

    Encode --> Search[向量检索<br/>20-50ms]
    Search --> Dedup{启用去重?}

    Dedup -->|是| RemoveDup[移除重复文档]
    Dedup -->|否| Format[格式化结果]

    RemoveDup --> Format
    Format --> SaveCache[保存到缓存]
    SaveCache --> Return[返回结果]
    ReturnCache --> End([完成])
    Return --> End
```

## 错误处理流程

```mermaid
graph TD
    Start([开始请求]) --> Health{服务健康检查}

    Health -->|失败| Error1[返回: 服务不可用]
    Health -->|成功| Auth{认证检查}

    Auth -->|失败| Error2[返回: 401 认证失败]
    Auth -->|成功| Process[处理请求]

    Process --> Result{有结果?}

    Result -->|否| Fallback{启用降级?}
    Result -->|是| Success[返回成功结果]

    Fallback -->|是| UseDefault[OpenClaw 默认回答]
    Fallback -->|否| Error3[返回: 无相关结果]

    Error1 --> Retry{重试?}
    Retry -->|是| Start
    Retry -->|否| FinalError[最终失败]

    Success --> End([完成])
    UseDefault --> End
    Error2 --> End
    Error3 --> End
    FinalError --> End
```

## 多租户隔离架构

```mermaid
graph TB
    subgraph "主数据库"
        Master[(knowledge_master)]
        Apps[应用表 apps]
    end

    subgraph "应用数据库 - app_001"
        DB1[(knowledge_app_001)]
        Docs1[documents]
        Chunks1[document_chunks]
        Chat1[chat_sessions]
    end

    subgraph "应用数据库 - app_002"
        DB2[(knowledge_app_002)]
        Docs2[documents]
        Chunks2[document_chunks]
        Chat2[chat_sessions]
    end

    subgraph "OpenClaw A"
        OCA[OpenClaw Instance A<br/>app_id: app_001]
    end

    subgraph "OpenClaw B"
        OCB[OpenClaw Instance B<br/>app_id: app_002]
    end

    Master --> Apps
    Apps -.->|路由| DB1
    Apps -.->|路由| DB2

    OCA -->|认证 app_001| DB1
    OCB -->|认证 app_002| DB2

    DB1 --> Docs1
    DB1 --> Chunks1
    DB1 --> Chat1

    DB2 --> Docs2
    DB2 --> Chunks2
    DB2 --> Chat2
```

## 完整技术栈

```mermaid
graph TB
    subgraph "前端层"
        Frontend[React + Vite<br/>TypeScript]
    end

    subgraph "OpenClaw 集成层"
        Skill[RAG Skill<br/>Python]
    end

    subgraph "应用层"
        FastAPI[FastAPI 0.135.1+<br/>Python 3.11+]
    end

    subgraph "服务层"
        Doc[文档服务]
        Know[知识服务]
        File[文件服务]
        BGE[向量服务]
    end

    subgraph "模型层"
        Ollama[Ollama API<br/>bge-m3<br/>1024维向量]
    end

    subgraph "数据层"
        PG[(PostgreSQL 15+<br/>pgvector扩展)]
        Storage[文件存储]
    end

    Frontend --> FastAPI
    Skill --> FastAPI
    FastAPI --> Doc
    FastAPI --> Know
    FastAPI --> File

    Doc --> BGE
    Know --> BGE
    File --> BGE

    BGE --> Ollama

    Doc --> PG
    Know --> PG
    File --> PG
    File --> Storage
```
