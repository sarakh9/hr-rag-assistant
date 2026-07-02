# HR RAG Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

An intelligent HR chatbot assistant powered by **Retrieval-Augmented Generation (RAG)** that answers employee questions about company policies, benefits, procedures, and workplace culture using Google Gemini and ChromaDB.

## 🎯 Overview

HR RAG Assistant is a production-ready system that combines:
- **Document Processing**: Intelligent chunking and embedding of HR policies
- **Vector Database**: ChromaDB for semantic search
- **LLM Intelligence**: Google Gemini for reasoning and answer generation
- **REST API**: FastAPI backend with request tracking
- **User Interface**: Streamlit frontend for intuitive interaction

The system ensures **accuracy-first** responses by grounding answers in actual company documentation, preventing hallucinations and maintaining compliance.

## ✨ Features

- 🤖 **AI-Powered Responses**: Uses Google Gemini 3.1 Flash for fast, intelligent answers
- 📚 **RAG Pipeline**: Retrieves relevant policies before generating answers
- 🔐 **Privacy-Focused**: Refuses to collect sensitive personal data
- 📝 **Multi-turn Conversations**: Maintains context across conversation history
- 🏭 **Production Ready**: Error handling, request tracking, CORS support
- 🔄 **Configurable**: YAML-based configuration for prompts and models
- 📊 **Observable**: Structured logging with request IDs for debugging

## 🏗️ Architecture
```markdown
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                      │
│         User Chat Interface with Conversation History        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
│  ✓ Request ID Middleware  ✓ CORS Support  ✓ Error Handlers  │
│                  /chat endpoint                               │
└────────────────────────────┬────────────────────────────────┘
                             │
                ┌────────────┴───────────┐
                ↓                        ↓
        ┌──────────────────┐    ┌──────────────────┐
        │  HR Assistant    │    │  Knowledge Base  │
        │  (Gemini)        │    │  (ChromaDB)      │
        ├──────────────────┤    ├──────────────────┤
        │• Retrieval Query │    │• Vector Storage  │
        │• Answer Gen      │    │• Semantic Search │
        │• Multi-turn      │    │• HR Policies     │
        └──────────────────┘    └──────────────────┘
                │                        ↑
                └────────────────────────┘
                  Retrieval-Augmented
                      Generation
```

### Component Details

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | User-friendly chat interface |
| **Backend** | FastAPI + Uvicorn | REST API with middleware |
| **LLM** | Google Gemini 3.1 Flash | Query generation & answer synthesis |
| **Vector DB** | ChromaDB | Semantic search over policies |
| **Embeddings** | Google Gemini Embeddings | Convert text to vectors (768-dim) |
| **Config** | YAML | Prompt templates and model selection |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key ([get one here](https://ai.google.dev/))
- ~500MB disk space (for ChromaDB + embeddings)

### 1. Clone & Install

```bash
git clone https://github.com/sarakh9/hr-rag-assistant.git
cd hr-rag-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp config/.env.example config/.env

# Edit with your API key
# config/.env:
GEMINI_API_KEY=your_api_key_here
ASSISTANT_API_URL=http://127.0.0.1:8000/chat
```

### 3. Prepare Knowledge Base

Place your HR policy documents (Markdown format) in `data/raw/`:

```bash
mkdir -p data/raw
# Add your HR policies as .md files
# Example: data/raw/policies.md
```

Then run the pipeline:

```bash
# Step 1: Chunk the documents
python chunker.py
# Output: data/chunked/

# Step 2: Embed and ingest into ChromaDB
python ingestor.py
# Creates: chroma_db/
```

### 4. Start the Backend

```bash
python -m server
# Server running at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 5. Launch the Frontend

```bash
# In a new terminal
streamlit run frontend/frontend.py
# Open http://localhost:8501 in your browser
```

## 📖 Usage

### Via REST API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {
        "role": "user",
        "content": "What is the vacation policy?"
      }
    ]
  }'
```

**Response:**
```json
{
  "assistant_response": {
    "role": "assistant",
    "content": "Based on our policy documentation, employees receive 20 days of vacation annually..."
  }
}
```

### Via Streamlit UI

1. Open http://localhost:8501
2. Type your HR question
3. View the assistant's response with source information
4. Continue multi-turn conversation

## ⚙️ Configuration

### Customize Model Selection

Edit `config/assistant.yaml`:

```yaml
# Available models: gemini-2.5-flash, gemini-3.1-flash-lite, gemini-3.5-flash
answer_generation_model: gemini-3.1-flash-lite
retrieval_query_model: gemini-3.1-flash-lite

# Adjust response creativity (0.0 = deterministic, 1.0 = creative)
top_p: 0.8

knowledge_base:
  embedding_model: gemini-embedding-2
  search_limit: 10  # Top K results to retrieve
  collection_name: hr-policies-kb-collection
```

### Customize System Prompts

The `answer_generation_prompt` in `config/assistant.yaml` controls behavior:

```yaml
answer_generation_prompt: |
  Role: You are a AI HR Assistant...
  
  Tone and Style:
  1. Professional yet approachable
  2. Clear and Concise
  3. Empathetic
  
  Operational Guidelines:
  1. Accuracy First: Only answer based on provided documentation
  2. Privacy & Confidentiality: Don't ask for sensitive data
  3. Formatting: Use bullet points and bold text
```

## 📦 Project Structure

```
hr-rag-assistant/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config/
│   ├── .env.example                   # Environment variables template
│   ├── assistant.yaml                 # LLM & prompt configuration
│   └── logging.yaml                   # Logging configuration
├── data/
│   ├── raw/                           # Original HR policy documents
│   └── chunked/                       # Processed & chunked documents
├── assistant/
│   ├── assistant.py                   # Core RAG logic
│   ├── assistant_config.py            # Config loading
│   └── knowledgebase.py               # ChromaDB wrapper
├── server/
│   ├── __main__.py                    # FastAPI app entry point
│   ├── chat_endpoints/
│   │   ├── router.py                  # /chat endpoint
│   │   └── schema.py                  # Request/response models
│   ├── errors/
│   │   └── handlers.py                # Exception handlers
│   ├── middlewares/
│   │   └── request_id.py              # Request ID tracking
│   └── utils/
│       └── logging.py                 # Logging initialization
├── frontend/
│   └── frontend.py                    # Streamlit UI
├──src
│   ├── chunker.py                     # Document chunking script
│   └── ingestor.py                    # Knowledge base ingestion script
```

## 🔄 Data Pipeline

### 1. Document Chunking

The `chunker.py` script processes markdown files:

```python
# Input: data/raw/hr-policies.md
# Process:
# - Split by headers (H1, H2, H3)
# - Chunk into 2048-token segments
# - Preserve metadata (source, headers)
# Output: data/chunked/hr-policies/{0..n}.md + {0..n}.json
```

### 2. Knowledge Base Ingestion

The `ingestor.py` script embeds and stores:

```python
# Input: data/chunked/
# Process:
# - Read markdown content
# - Generate embeddings via Google Gemini (768-dim)
# - Store in ChromaDB with metadata
# - Persist to: chroma_db/
```

### 3. Query & Retrieval

During chat:
1. Generate optimized retrieval query from conversation
2. Embed query using same model
3. Search ChromaDB with cosine similarity
4. Return top-10 most relevant chunks

### 4. Answer Generation

LLM receives:
- Full conversation history
- Top-10 retrieved policy chunks
- System prompt (role, tone, constraints)
- Generates grounded answer


## 📊 Performance

### Typical Response Time

| Operation | Time |
|-----------|------|
| Retrieve Query Generation | ~500ms |
| ChromaDB Semantic Search | ~100ms |
| Answer Generation | ~1-2s |
| **Total** | **~2-3s** |

### Cost Estimation (Google Gemini API)

- **Embeddings**: ~$0.025 per 1M tokens
- **Inference**: ~$0.075 per 1M input tokens, ~$0.30 per 1M output tokens
- **Typical monthly** (1000 conversations): ~$5-10

## 🐛 Troubleshooting

### Issue: `GEMINI_API_KEY not set`

```bash
# Solution: Add to config/.env
GEMINI_API_KEY=your_actual_key_here
```

### Issue: `ChromaDB collection not found`

```bash
# Solution: Re-run the ingestion pipeline
python chunker.py
python ingestor.py
```

### Issue: Empty or irrelevant responses

```bash
# Possible causes:
# 1. Knowledge base not properly ingested
# 2. Query too dissimilar from documentation
# 3. search_limit too low in config/assistant.yaml

# Solution: Increase search_limit or add more relevant documents
```

### Issue: Frontend can't connect to backend

```bash
# Check backend is running:
curl http://localhost:8000/docs

# Update frontend config:
# config/.env: ASSISTANT_API_URL=http://localhost:8000/chat
```


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Docs](https://docs.streamlit.io/)


## 👤 Author

**Sarah.kh**  
GitHub: [@sarakh9](https://github.com/sarakh9)

---

**Last Updated**: July 2026  
**Status**: Active Development
