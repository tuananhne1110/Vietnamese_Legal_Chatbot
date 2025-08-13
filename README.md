# 🤖 Vietnamese Legal Chatbot

Một hệ thống chatbot thông minh hỗ trợ tư vấn pháp luật Việt Nam, được xây dựng với công nghệ AI tiên tiến và giao diện người dùng thân thiện.

## 🌟 Tính Năng Chính

### 💬 Chatbot Thông Minh
- **RAG (Retrieval-Augmented Generation)**: Tìm kiếm và trả lời dựa trên cơ sở dữ liệu pháp luật Việt Nam
- **Intent Detection**: Tự động phân loại loại câu hỏi (luật, biểu mẫu, thủ tục, v.v.)
- **Semantic Cache**: Cache thông minh để tăng tốc độ phản hồi
- **Guardrails**: Kiểm duyệt nội dung an toàn với AWS Bedrock Guardrails
- **Streaming Response**: Trả lời real-time từng chunk

### 🎤 Đa Phương Tiện
- **Voice-to-Text**: Chuyển đổi giọng nói thành văn bản với PhoWhisper
- **Text-to-Speech**: Chuyển đổi văn bản thành giọng nói
- **File Upload**: Hỗ trợ upload tài liệu để phân tích

### 📋 Biểu Mẫu Thông Minh
- **CT01 Form Filling**: Tự động điền biểu mẫu thuế thu nhập cá nhân
- **CCCD Scanning**: Quét và trích xuất thông tin từ CCCD
- **Form Validation**: Kiểm tra dữ liệu real-time
- **Document Generation**: Tạo file PDF/Word từ form

### 🔍 Tìm Kiếm Nâng Cao
- **Semantic Search**: Tìm kiếm ngữ nghĩa trong vector database
- **Multi-collection Retrieval**: Tìm kiếm đa nguồn dữ liệu
- **Reranking**: Sắp xếp lại kết quả với BGE reranker
- **Source Citation**: Trích dẫn nguồn tham khảo chính xác

## 🏗️ Kiến Trúc Hệ Thống

### Backend Architecture
```
backend/
├── agents/                 # LangGraph workflow
│   ├── nodes/             # Workflow nodes
│   ├── guardrails/        # AWS Bedrock Guardrails
│   ├── prompt/            # Prompt templates
│   └── workflow.py        # Main workflow
├── services/              # Core services
│   ├── llm_service.py     # AWS Bedrock integration
│   ├── qdrant_service.py  # Vector database
│   ├── cache_service.py   # Redis cache
│   └── reranker_service.py # BGE reranker
├── routers/               # API endpoints
│   ├── langgraph_chat.py  # Main chat API
│   ├── voice_to_text.py   # Voice processing
│   └── ct01.py           # Form handling
└── configs/               # Configuration
    ├── settings.py        # App settings
    └── configs.yaml       # Config file
```

### Frontend Architecture
```
frontend/src/
├── components/            # React components
│   ├── ChatInterface.js   # Main chat UI
│   ├── CT01Modal.js       # Form modal
│   └── VoiceRecorder.js   # Voice input
├── hooks/                 # Custom hooks
│   ├── useChatStream.js   # Chat streaming
│   └── useVoiceToText.js  # Voice processing
└── services/              # API services
```

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

### 2. Backend Setup

#### Cài đặt dependencies
```bash
cd backend
pip install -r ../shared/requirements.txt
```

#### Cấu hình môi trường
Tạo file `.env` trong thư mục gốc:
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-southeast-1

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

#### Cấu hình models
Chỉnh sửa `backend/configs/configs.yaml`:
```yaml
models:
  aws_bedrock:
    llm_model_configs:
      llama:
        model_id: "meta.llama4-scout-17b-v1.0-q4_0"
        region_name: "ap-southeast-1"
    guardrails:
      input_policy: "path/to/policy_input.yaml"
      output_policy: "path/to/policy_output.yaml"
  
  hugging_face:
    embedding_model_configs:
      qwen:
        model_name: "BAAI/bge-large-zh-v1.5"
        device: "cuda"
    reranker_model_configs:
      bge:
        model_name: "BAAI/bge-reranker-large"
        device: "cuda"
```

### 3. Frontend Setup

#### Cài đặt dependencies
```bash
cd frontend
npm install
```

#### Cấu hình môi trường
Tạo file `.env` trong thư mục `frontend`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
REACT_APP_DEBUG=true
```

### 4. Database Setup

#### Supabase Database
Chạy các SQL scripts trong `frontend/SETUP.md` để tạo các bảng cần thiết.

#### Qdrant Vector Database
```bash
# Khởi động Qdrant với Docker
docker run -p 6333:6333 qdrant/qdrant

# Hoặc sử dụng docker-compose
docker-compose up qdrant
```

### 5. Khởi động với Docker

#### Sử dụng docker-compose
```bash
# Khởi động toàn bộ hệ thống
docker-compose -f docker/docker-compose.yml up -d

# Xem logs
docker-compose -f docker/docker-compose.yml logs -f
```

#### Khởi động thủ công
```bash
# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm start
```

## 📊 Workflow LangGraph

Hệ thống sử dụng LangGraph workflow với 8 bước chính:

1. **Intent Detection**: Phân loại loại câu hỏi
2. **Semantic Cache**: Kiểm tra cache thông minh
3. **Guardrails Input**: Kiểm duyệt đầu vào
4. **Query Rewriting**: Làm sạch và cải thiện câu hỏi
5. **Semantic Retrieval**: Tìm kiếm thông tin liên quan
6. **Answer Generation**: Sinh câu trả lời với LLM
7. **Output Validation**: Kiểm duyệt đầu ra
8. **Memory Update**: Cập nhật bộ nhớ và cache

## 🔧 API Endpoints

### Chat Endpoints
- `POST /chat/` - Chat thông thường
- `POST /chat/stream` - Chat streaming
- `POST /chat/session` - Tạo session mới

### Voice Endpoints
- `POST /voice/transcribe` - Chuyển đổi giọng nói thành văn bản
- `POST /voice/synthesize` - Chuyển đổi văn bản thành giọng nói

### CT01 Form Endpoints
- `POST /ct01/generate` - Tạo file CT01
- `POST /ct01/submit` - Nộp form trực tuyến
- `GET /ct01/history` - Lấy lịch sử form
- `GET /ct01/template` - Lấy template form

### Health Check
- `GET /health` - Kiểm tra trạng thái hệ thống

## 🛠️ Công Nghệ Sử Dụng

### Backend
- **FastAPI**: Web framework
- **LangGraph**: Workflow orchestration
- **AWS Bedrock**: LLM service (Llama 4 Scout 17B)
- **Qdrant**: Vector database
- **Redis**: Caching
- **Supabase**: PostgreSQL database
- **Sentence Transformers**: Embedding models
- **BGE Reranker**: Document reranking

### Frontend
- **React 18**: UI framework
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **React Markdown**: Markdown rendering
- **Lucide React**: Icons

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy
- **Redis**: Session storage

## 📈 Performance & Scalability

### Caching Strategy
- **Semantic Cache**: Cache câu hỏi tương tự với similarity ≥ 0.85
- **Redis Cache**: Session management và temporary data
- **Vector Cache**: Embedding cache cho performance

### Optimization
- **Streaming Response**: Real-time response streaming
- **Parallel Processing**: Parallel guardrails validation
- **Lazy Loading**: Lazy load heavy resources
- **Connection Pooling**: Database connection optimization

## 🔒 Bảo Mật

### Content Safety
- **AWS Bedrock Guardrails**: Input/Output validation
- **Policy-based Filtering**: Custom safety policies
- **Content Moderation**: Real-time content checking

### Data Protection
- **Environment Variables**: Secure configuration management
- **API Key Management**: Secure API key handling
- **HTTPS**: Encrypted communication

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
```bash
# Test API endpoints
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Luật thuế thu nhập cá nhân quy định như thế nào?"}'
```

## 📝 Documentation

- [Workflow Documentation](./docs/Workflow.md) - Chi tiết workflow LangGraph
- [Frontend Setup](./frontend/SETUP.md) - Hướng dẫn setup frontend
- [API Documentation](http://localhost:8000/docs) - Swagger UI (khi chạy backend)

---

