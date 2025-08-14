# 🤖 Vietnamese Legal Chatbot

Hệ thống chatbot thông minh hỗ trợ tư vấn pháp luật Việt Nam, được xây dựng với LangGraph workflow và công nghệ AI hiện đại.

## 🌟 Tính Năng Chính

### 💬 Chatbot AI
- **RAG (Retrieval-Augmented Generation)**: Tìm kiếm và trả lời dựa trên cơ sở dữ liệu pháp luật
- **Intent Detection**: Phân loại loại câu hỏi (law, procedure, form, term, template, general)
- **Semantic Cache**: Cache thông minh với Redis để tăng tốc độ phản hồi
- **Guardrails**: Kiểm duyệt nội dung đầu vào và đầu ra an toàn
- **Streaming Response**: Trả lời real-time từng chunk với Server-Sent Events

### 🎤 Voice-to-Text
- **PhoWhisper Model**: Chuyển đổi giọng nói tiếng Việt thành văn bản
- **Voice Recording**: Ghi âm và xử lý real-time
- **WebRTC VAD**: Voice Activity Detection

### 📋 CT01 Form Processing
- **Form Generation**: Tạo biểu mẫu CT01 từ template HTML
- **Document Export**: Xuất file PDF/DOCX từ form data
- **CCCD Scanner**: Quét và trích xuất thông tin từ CCCD

### 🔍 Semantic Search
- **Multi-collection Retrieval**: Tìm kiếm đa nguồn (legal, procedure, form, template, general)
- **BGE Reranker**: Sắp xếp lại kết quả với BAAI/bge-reranker-v2-m3
- **Source Citation**: Trích dẫn nguồn tham khảo chính xác

## 🏗️ Kiến Trúc Hệ Thống

### Backend Structure
```
backend/
├── agents/                 # LangGraph workflow
│   ├── nodes/             # Workflow nodes (8 nodes)
│   │   ├── intent_node.py        # Intent detection
│   │   ├── semantic_cache_node.py # Cache management
│   │   ├── guardrails_node.py    # Input validation
│   │   ├── rewrite_node.py       # Query rewriting
│   │   ├── retrieve_node.py      # Document retrieval
│   │   ├── generate_node.py      # Answer generation
│   │   ├── validate_node.py      # Output validation
│   │   └── memory_node.py        # Memory update
│   ├── guardrails/        # Guardrails service
│   ├── prompt/            # Prompt templates
│   └── workflow.py        # Main LangGraph workflow
├── services/              # Core services
│   ├── llm_service.py     # AWS Bedrock integration
│   ├── qdrant_service.py  # Vector database
│   ├── cache_service.py   # Redis cache
│   └── reranker_service.py # BGE reranker
├── routers/               # API endpoints
│   ├── langgraph_chat.py  # Chat API
│   ├── voice_to_text.py   # Voice processing
│   ├── ct01.py           # Form handling
│   └── health.py         # Health checks
├── configs/               # Configuration
│   ├── settings.py        # App settings
│   └── configs.yaml       # Model configs
└── embeddings/            # Embedding service
```

### Frontend Structure
```
frontend/src/
├── components/            # React components
│   ├── ChatInterface.js   # Main chat UI
│   ├── ChatWindow.js      # Chat display
│   ├── MessageInput.js    # Input handling
│   ├── VoiceRecorder.js   # Voice input
│   ├── CT01Modal.js       # Form modal
│   ├── CT01Form.js        # Form component
│   ├── CCCDScanner.js     # CCCD scanning
│   └── FloatingChatbot.js # Widget mode
├── hooks/                 # Custom React hooks
├── services/              # API services
└── config/                # Configuration
```

## 🔄 LangGraph Workflow

Hệ thống sử dụng sequential workflow với 8 bước:

1. **Intent Detection** → Phân loại intent của câu hỏi
2. **Semantic Cache** → Kiểm tra cache với threshold 0.85
3. **Guardrails Input** → Validate đầu vào an toàn
4. **Query Rewriting** → Cải thiện và làm sạch câu hỏi
5. **Document Retrieval** → Tìm kiếm semantic trong Qdrant
6. **Answer Generation** → Sinh câu trả lời với AWS Bedrock
7. **Output Validation** → Validate đầu ra an toàn
8. **Memory Update** → Cập nhật lịch sử và cache

## 🚀 Cài Đặt và Triển Khai

### Yêu Cầu Hệ Thống
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Redis
- Qdrant Vector Database
- Supabase (PostgreSQL)

### 1. Clone Repository
```bash
git clone <repository-url>
cd Vietnamese_Legal_Chatbot
```

### 2. Environment Setup
Tạo file `.env` trong thư mục gốc:
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
```

### 3. Backend Setup
```bash
# Install dependencies
pip install -r shared/requirements.txt

# Start backend
python main.py
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 5. Docker Deployment
```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Services included:
# - Redis (port 6379)
# - Backend (port 8000)
# - Frontend (port 3000) 
# - Nginx (port 80)
```

## 🔧 API Endpoints

### Chat API
- `POST /` - Chat thông thường
- `POST /stream` - Chat streaming với SSE

### Voice API
- `POST /voice/start-recording` - Bắt đầu ghi âm
- `POST /voice/stop-recording` - Dừng ghi âm
- `GET /voice/status` - Trạng thái recording
- `POST /voice/get-current-text` - Lấy text hiện tại
- `GET /voice/model-info` - Thông tin model

### CT01 Form API
- `POST /ct01/generate` - Tạo file CT01
- `POST /ct01/submit` - Xử lý form data

### Health Check
- `GET /health` - Trạng thái hệ thống
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check

## 🛠️ Công Nghệ Sử Dụng

### Backend
- **FastAPI** (0.116.0) - Web framework
- **LangGraph** (0.5.1) - Workflow orchestration
- **AWS Bedrock** - LLM service (Llama 4 Scout 17B, Claude)
- **Qdrant** (1.14.3) - Vector database
- **Redis** (6.2.0) - Caching và session
- **Supabase** (2.16.0) - PostgreSQL database
- **Sentence Transformers** (5.0.0) - Embedding models
- **BGE Reranker** - Document reranking
- **PhoWhisper** - Vietnamese voice-to-text

### Frontend
- **React** (18.2.0) - UI framework
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering
- **Lucide React** - Icons

### Models & AI
- **LLM**: Meta Llama 4 Scout 17B / Anthropic Claude 3.5 Sonnet
- **Embedding**: Qwen3-Embedding-0.6B / Alibaba GTE-multilingual
- **Reranker**: BAAI/bge-reranker-v2-m3
- **Voice**: vinai/PhoWhisper-medium

### DevOps
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Docker Compose** - Multi-container orchestration

## 📈 Performance Features

### Caching Strategy
- **Semantic Cache**: Cache câu hỏi tương tự (similarity ≥ 0.85)
- **Redis Cache**: Session management
- **Model Caching**: Eager loading models at startup

### Optimization
- **Streaming Response**: Real-time SSE streaming
- **Sequential Processing**: Simplified workflow without parallel overhead
- **Connection Pooling**: Database optimization

## 🔒 Security & Safety

### Content Safety
- **Guardrails**: Input và output validation
- **Policy-based Filtering**: Custom safety policies  
- **Sequential Validation**: Input → Processing → Output validation

### Data Protection
- **Environment Variables**: Secure configuration
- **API Key Management**: Secure credentials handling

## 📝 Documentation

- [Workflow Documentation](./Workflow.md) - Chi tiết LangGraph workflow
- [API Documentation](http://localhost:8000/docs) - Swagger UI

---

**Lưu ý**: Hệ thống hiện tại đang disable Bedrock Guardrails API do cấu hình, sử dụng mock responses để đảm bảo performance.