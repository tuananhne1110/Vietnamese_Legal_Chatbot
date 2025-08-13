# 🔄 Workflow Hệ Thống Vietnamese Legal Chatbot

## 📋 Tổng Quan Workflow

Hệ thống Vietnamese Legal Chatbot sử dụng **LangGraph** để orchestrate một workflow phức tạp với 8 bước chính, từ việc nhận câu hỏi đến việc trả về câu trả lời cuối cùng.

## Full Pipeline Workflow

```mermaid
graph TD
    %% User Interface
    A[User Input 
    Text/Voice/File] --> B[React Frontend]
    B --> C[FastAPI Backend]
    
    %% Initial Processing
    C --> D[Create Chat State]
    D --> E[Detect Intent]
    
    %% Cache Check
    E --> F[Check Cache]
    F --> G{Cache Hit?}
    
    %% Cache Hit Path
    G -->|Yes| H[Return Cached Answer]
    H --> I[Update Memory]
    I --> J[Stream Response]
    
    %% Cache Miss Path
    G -->|No| K[Input Guardrails]
    K --> L{Input Valid?}
    
    %% Invalid Input Path
    L -->|No| M[Safe Message]
    M --> I
    
    %% Valid Input Path
    L -->|Yes| N[Rewrite Query]
    N --> O[Retrieve Docs]
    O --> P[Rerank Docs]
    
    %% Answer Generation
    P --> R[Generate Answer]
    R --> S[Output Guardrails]
    S --> T{Output Valid?}
    
    %% Output Validation
    T -->|No| U[Safe Content]
    T -->|Yes| V[Original Answer]
    
    U --> W[Final Answer]
    V --> W
    
    %% Memory Update
    W --> X[Update Memory]
    X --> Y[Update History]
    Y --> Z[Cache Answer]
    Z --> J
    
    %% External Services
    subgraph "External Services"
        AA[AWS Bedrock]
        BB[Qdrant]
        CC[Redis]
        DD[Supabase]
    end
    
    %% Service Connections
    K -.-> AA
    R -.-> AA
    S -.-> AA
    O -.-> BB
    F -.-> CC
    Z -.-> CC
    I -.-> DD
    Y -.-> DD
    
    %% Styling
    classDef userLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef backendLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef cacheLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef processingLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef serviceLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef decisionLayer fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    
    class A,B userLayer
    class C,D,E,N,O,P,Q,R,S,T,U,V,W,X,Y,Z backendLayer
    class F,G,H,K,L,M cacheLayer
    class J processingLayer
    class AA,BB,CC,DD serviceLayer
    class G,L,T decisionLayer
```

## Alternative View: System Architecture Flow

```mermaid
flowchart LR
    subgraph "User Interface"
        A1[Web Browser]
        A2[Mobile App]
        A3[Voice Input]
    end
    
    subgraph "Application Layer"
        B1[React Frontend]
        B2[FastAPI Backend]
        B3[WebSocket/SSE]
    end
    
    subgraph "AI Processing Pipeline"
        C1[Intent Detection]
        C2[Semantic Cache]
        C3[Guardrails Input]
        C4[Query Rewriting]
        C5[Vector Retrieval]
        C6[LLM Generation]
        C7[Output Validation]
        C8[Memory Update]
    end
    
    subgraph "Data Layer"
        D1[Qdrant Vector DB]
        D2[Redis Cache]
        D3[Supabase PostgreSQL]
        D4[Supabase Storage]
    end
    
    subgraph "Cloud Services"
        E1[AWS Bedrock LLM]
        E2[AWS Guardrails]
        E3[PhoWhisper Voice]
    end
    
    %% Connections
    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> C1
    
    C1 --> C2 --> C3 --> C4 --> C5 --> C6 --> C7 --> C8
    
    C2 --> D2
    C5 --> D1
    C6 --> E1
    C3 --> E2
    C7 --> E2
    C8 --> D3
    C8 --> D2
    
    A3 --> E3
    E3 --> B2
    
    %% CT01 Form Flow
    subgraph "CT01 Form Processing"
        F1[CCCD Scanning]
        F2[Form Filling]
        F3[Document Generation]
        F4[Online Submission]
    end
    
    B1 --> F1
    F1 --> F2 --> F3 --> F4
    F4 --> D3
    F3 --> D4
```

## 🔄 Chi Tiết Workflow LangGraph

### 1. Intent Detection (Phân Loại Ý Định)

```mermaid
flowchart TD
    A[User Question] --> B[Keyword Analysis]
    B --> C[Intent Scoring]
    C --> D{Primary Intent}
    
    D -->|LAW| E[Legal Documents]
    D -->|FORM| F[Form Templates]
    D -->|PROCEDURE| G[Procedural Info]
    D -->|TEMPLATE| H[Document Templates]
    D -->|GENERAL| I[General Info]
    
    E --> K[Collection Mapping]
    F --> K
    G --> K
    H --> K
    I --> K
    
    K --> L[Intent State]
```

**Mô tả:**
- Phân tích từ khóa trong câu hỏi
- Tính điểm confidence cho từng loại intent
- Map intent đến collections tương ứng:
  - **LAW** → `legal_chunks`
  - **FORM** → `form_chunks`, `template_chunks`
  - **PROCEDURE** → `procedure_chunks`, `legal_chunks`
  - **TERM** → `legal_chunks`
  - **TEMPLATE** → `template_chunks`
  - **GENERAL** → `general_chunks`

### 2. Semantic Cache (Kiểm Tra Cache)

```mermaid
flowchart TD
    A[Intent State] --> B[Generate Embedding]
    B --> C[Search Cache]
    C --> D{Similarity >= 0.85?}
    
    D -->|Yes| E[Cache Hit]
    D -->|No| F[Cache Miss]
    
    E --> G[Return Cached Answer]
    F --> H[Continue Processing]
    
    G --> I[Update Memory]
    H --> J[Next Step]
```

**Mô tả:**
- Tạo embedding của câu hỏi gốc
- So sánh với cache entries trong Redis
- Threshold: 0.85 similarity score
- Nếu cache hit: trả ngay kết quả, bỏ qua các bước sau

### 3. Guardrails Input (Kiểm Duyệt Đầu Vào)

```mermaid
flowchart TD
    A[Cache Miss] --> B[AWS Bedrock Guardrails]
    B --> C[Policy Check]
    C --> D{Violation?}
    
    D -->|Yes| E[Block Request]
    D -->|No| F[Continue]
    
    E --> G[Safe Response]
    F --> H[Next Step]
    
    G --> I[Update Memory]
    H --> J[Query Rewriting]
```

**Mô tả:**
- Sử dụng AWS Bedrock Guardrails
- Kiểm tra theo policy từ `policy_input.yaml`
- Chặn câu hỏi vi phạm chính sách an toàn
- Trả thông báo an toàn nếu vi phạm

### 4. Query Rewriting (Làm Sạch Câu Hỏi)

```mermaid
flowchart TD
    A[Valid Input] --> B[Rule-based Cleaning]
    B --> C[Context Extraction]
    C --> D[Conversation History]
    D --> E[LLM Paraphrase]
    E --> F[Optimized Query]
    F --> G[Context String]
    
    G --> H[Next Step]
```

**Mô tả:**
- Làm sạch câu hỏi với rule-based cleaning
- Trích xuất context từ lịch sử hội thoại
- Sử dụng LLM để paraphrase nếu cần
- Tạo câu hỏi tối ưu cho tìm kiếm

### 5. Semantic Retrieval (Truy Xuất Thông Tin)

```mermaid
flowchart TD
    A[Optimized Query] --> B[Multi-Collection Search]
    B --> C[Vector Search]
    C --> D[Top Candidates]
    D --> E[BGE Reranker]
    E --> F[Filter by Score]
    F --> G{Score >= 0.3?}
    
    G -->|Yes| H[Keep Document]
    G -->|No| I[Discard Document]
    
    H --> J[Limit to 12 Docs]
    I --> J
    J --> K[Context Documents]
    
    K --> L[Next Step]
```

**Mô tả:**
- Tìm kiếm trong collections tương ứng với intent
- Lấy candidates từ mỗi collection (6-15 docs)
- Sử dụng BGE reranker để sắp xếp lại
- Lọc theo rerank_score >= 0.3
- Giới hạn final 12 documents

### 6. Answer Generation (Sinh Câu Trả Lời)

```mermaid
flowchart TD
    A[Context Documents] --> B[Prompt Template Selection]
    B --> C[Context Formatting]
    C --> D[Metadata Injection]
    D --> E[AWS Bedrock LLM]
    E --> F[Streaming Response]
    F --> G[Post-processing]
    G --> H{Length > 1500?}
    
    H -->|Yes| I[Truncate Answer]
    H -->|No| J[Keep Answer]
    
    I --> K[Final Answer]
    J --> K
    
    K --> L[Next Step]
```

**Mô tả:**
- Chọn prompt template theo intent
- Tạo context trực tiếp từ documents và metadata
- Gọi AWS Bedrock (Llama 4 Scout 17B)
- Stream kết quả về frontend
- Post-processing: cắt bớt nếu quá dài

### 7. Output Validation (Kiểm Duyệt Đầu Ra)

```mermaid
flowchart TD
    A[Generated Answer] --> B[AWS Bedrock Guardrails]
    B --> C[Output Policy Check]
    C --> D{Violation?}
    
    D -->|Yes| E[Replace with Safe Content]
    D -->|No| F[Keep Original]
    
    E --> G[Validated Answer]
    F --> G
    
    G --> H[Next Step]
```

**Mô tả:**
- Sử dụng AWS Bedrock Guardrails
- Kiểm tra theo policy từ `policy_output.yaml`
- Thay thế nội dung vi phạm bằng thông báo an toàn

### 8. Memory Update (Cập Nhật Bộ Nhớ)

```mermaid
flowchart TD
    A[Validated Answer] --> B[Conversation History]
    B --> C[Context Summary]
    C --> D[Metadata Storage]
    D --> E[Supabase Update]
    E --> F[Semantic Cache]
    F --> G[Redis Cache]
    G --> H[Processing Time Log]
    H --> I[Final Response]
    
    I --> J[Return to User]
```

**Mô tả:**
- Cập nhật conversation history
- Tạo context summary cho lần sau
- Lưu metadata và processing time
- Cache kết quả mới cho semantic cache

## 🔄 Parallel Processing Workflow

```mermaid
flowchart TD
    A[Generate Answer] --> B[Parallel Processing]
    
    subgraph "Parallel Execution"
        B --> C[Answer Generation]
        B --> D[Output Guardrails]
    end
    
    C --> E[Merge Results]
    D --> E
    
    E --> F{Guardrails Validated?}
    F -->|Yes| G[Use Validated Answer]
    F -->|No| H[Use Original Answer]
    
    G --> I[Final Answer]
    H --> I
    
    I --> J[Memory Update]
```

## 📊 Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant L as LangGraph
    participant Q as Qdrant
    participant R as Redis
    participant S as Supabase
    participant A as AWS Bedrock
    
    U->>F: Ask Question
    F->>B: POST /chat/stream
    B->>L: Create Initial State
    
    L->>L: Intent Detection
    L->>R: Check Semantic Cache
    
    alt Cache Hit
        R-->>L: Cached Answer
        L->>S: Update Memory
        L-->>B: Return Cached Response
        B-->>F: Stream Response
        F-->>U: Display Answer
    else Cache Miss
        L->>A: Guardrails Input Check
        A-->>L: Validation Result
        
        L->>L: Query Rewriting
        L->>Q: Semantic Search
        Q-->>L: Top Documents
        
        L->>A: Generate Answer
        A-->>L: Streaming Response
        
        L->>A: Output Validation
        A-->>L: Validation Result
        
        L->>S: Update Memory
        L->>R: Cache New Result
        
        L-->>B: Final Response
        B-->>F: Stream Response
        F-->>U: Display Answer
    end
```

## 🎯 Decision Points & Error Handling

```mermaid
flowchart TD
    A[Start] --> B{Intent Detected?}
    B -->|No| C[Default to GENERAL]
    B -->|Yes| D[Continue]
    C --> D
    
    D --> E{Cache Hit?}
    E -->|Yes| F[Return Cached]
    E -->|No| G[Continue Processing]
    
    G --> H{Input Valid?}
    H -->|No| I[Return Safe Message]
    H -->|Yes| J[Continue]
    
    J --> K{Context Found?}
    K -->|No| L[Generate General Answer]
    K -->|Yes| M[Continue]
    
    M --> N{Answer Generated?}
    N -->|No| O[Return Error Message]
    N -->|Yes| P[Continue]
    
    P --> Q{Output Valid?}
    Q -->|No| R[Replace with Safe Content]
    Q -->|Yes| S[Keep Original]
    
    R --> T[Final Response]
    S --> T
    
    T --> U[Update Memory]
    U --> V[End]
```

## 🔧 Configuration & State Management

### State Structure
```python
@dataclass
class ChatState:
    question: str
    messages: List[Dict]
    session_id: str
    intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    all_intents: Optional[List[str]] = None
    cache_hit: Optional[bool] = None
    cache_answer: Optional[str] = None
    cache_sources: Optional[List] = None
    error: Optional[str] = None
    rewritten_query: Optional[str] = None
    context: Optional[str] = None
    sources: Optional[List] = None
    prompt: Optional[str] = None
    answer: Optional[str] = None
    final_answer: Optional[str] = None
    processing_time: Optional[float] = None
    guardrails_validated: Optional[bool] = None
    parallel_guardrails_completed: Optional[bool] = None
    generation_completed: Optional[bool] = None
```

### Workflow Configuration
```python
def create_rag_workflow():
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("set_intent", set_intent)
    workflow.add_node("semantic_cache", semantic_cache)
    workflow.add_node("guardrails_input", guardrails_input)
    workflow.add_node("rewrite", rewrite_query_with_context)
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("parallel_guardrails", parallel_guardrails_output)
    workflow.add_node("merge_results", merge_parallel_results)
    workflow.add_node("validate", validate_output)
    workflow.add_node("update_memory", update_memory)
    
    # Add edges
    workflow.add_edge(START, "set_intent")
    workflow.add_edge("set_intent", "semantic_cache")
    workflow.add_edge("semantic_cache", "guardrails_input")
    workflow.add_edge("guardrails_input", "rewrite")
    workflow.add_edge("rewrite", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", "parallel_guardrails")
    workflow.add_edge("parallel_guardrails", "merge_results")
    workflow.add_edge("generate", "merge_results")
    workflow.add_edge("merge_results", "validate")
    workflow.add_edge("validate", "update_memory")
    workflow.add_edge("update_memory", END)
    
    return workflow.compile()
```

## 📈 Performance Metrics

### Timing Breakdown
- **Intent Detection**: ~50ms
- **Semantic Cache**: ~100ms
- **Guardrails Input**: ~200ms
- **Query Rewriting**: ~150ms
- **Semantic Retrieval**: ~500ms
- **Answer Generation**: ~2000-5000ms
- **Output Validation**: ~200ms
- **Memory Update**: ~100ms

### Total Response Time
- **Cache Hit**: ~300ms
- **Cache Miss**: ~3-8 seconds

### Optimization Strategies
- **Semantic Caching**: Reduces response time by 80%
- **Parallel Processing**: Reduces validation time by 50%
- **Lazy Loading**: Reduces startup time
- **Connection Pooling**: Improves database performance

## 🔍 Monitoring & Logging

### Key Metrics
- Response time per step
- Cache hit/miss ratio
- Intent distribution
- Error rates
- User satisfaction scores

### Logging Strategy
- Structured logging with correlation IDs
- Performance metrics collection
- Error tracking and alerting
- User interaction analytics

---

**Lưu ý**: Workflow này được thiết kế để xử lý các câu hỏi pháp luật Việt Nam một cách hiệu quả và an toàn, với khả năng mở rộng và tùy chỉnh cao.
