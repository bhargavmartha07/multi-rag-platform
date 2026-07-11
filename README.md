# Enterprise RAG Platform

A production-ready, multi-tenant Retrieval-Augmented Generation (RAG) system with advanced features including hybrid search, re-ranking, Redis caching, and full observability with Prometheus and Grafana.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Browser)                      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   FastAPI (API)                          │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
│  │  Auth    │  │Documents │  │  Query   │  │Metrics  │  │
│  │ Router   │  │  Router  │  │  Router  │  │ Router  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘  │
│       │              │              │              │       │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐  ┌────▼────┐  │
│  │  Auth    │  │Document  │  │  Query   │  │Prometheus│  │
│  │ Service  │  │ Service  │  │ Service  │  │ Metrics │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────────┘  │
│       │              │              │                      │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐               │
│  │   User   │  │Document  │  │Embedding │               │
│  │   Repo   │  │   Repo   │  │ Service  │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │              │              │                      │
│  ┌────▼──────────────▼──────────────▼────────────┐       │
│  │              PostgreSQL 15                      │       │
│  └────────────────────────────────────────────────┘       │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│               Celery Worker                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │Document  │  │Chunking  │  │Embedding │              │
│  │Processor │  │ Pipeline │  │ Pipeline │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │              │                     │
│  ┌────▼──────────────▼──────────────▼────────────┐      │
│  │              Qdrant Vector DB                   │      │
│  └────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│              Supporting Services                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Redis   │  │Prometheus│  │ Grafana  │              │
│  │ (Cache)  │  │(Metrics) │  │(Dashbrd) │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└──────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt |
| Vector DB | Qdrant |
| Cache | Redis 7 |
| Queue | Celery + Redis Broker |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | OpenAI GPT-3.5-turbo |
| Monitoring | Prometheus + Grafana |
| Container | Docker + Docker Compose |

## Project Structure

```
rag-platform/
├── api/                          # FastAPI application
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic Settings
│   │   │   ├── security.py       # JWT + bcrypt
│   │   │   └── celery_client.py  # Celery client for dispatching tasks
│   │   ├── db/
│   │   │   ├── base.py           # DeclarativeBase
│   │   │   └── database.py       # Engine + SessionLocal
│   │   ├── dependencies/
│   │   │   ├── auth.py           # JWT dependency
│   │   │   ├── database.py       # DB session dependency
│   │   │   └── storage.py        # File storage utility
│   │   ├── middleware/
│   │   │   ├── logging.py        # Request logging
│   │   │   └── metrics.py        # Prometheus metrics
│   │   ├── models/
│   │   │   ├── base_model.py     # Abstract base model
│   │   │   ├── user.py           # User model
│   │   │   ├── document.py       # Document model
│   │   │   └── enums.py          # Status enums
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   └── document_repository.py
│   │   ├── routers/
│   │   │   ├── auth.py           # POST /register, /login, GET /me
│   │   │   ├── documents.py      # POST /, GET /{id}/status
│   │   │   ├── query.py          # POST /query
│   │   │   ├── metrics.py        # GET /metrics
│   │   │   ├── health.py         # GET /health
│   │   │   └── root.py           # GET /
│   │   ├── schemas/
│   │   │   ├── auth.py           # Auth request/response DTOs
│   │   │   ├── document.py       # Document DTOs
│   │   │   └── query.py          # Query DTOs
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── document_service.py
│   │   │   ├── query_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── vector_service.py
│   │   │   └── cache_service.py
│   │   ├── lifespan.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── worker/                       # Celery worker
│   ├── app/
│   │   ├── celery_app.py         # Celery configuration
│   │   ├── tasks.py              # Document processing task
│   │   ├── chunking.py           # Text chunking logic
│   │   ├── models_document.py    # Standalone Document model
│   │   └── worker.py             # Entry point
│   ├── Dockerfile
│   └── requirements.txt
├── grafana/
│   ├── dashboards/
│   │   └── rag_dashboard.json    # Auto-provisioned dashboard
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboard.yml
│       └── datasources/
│           └── datasource.yml
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   ├── test_auth.py              # Auth endpoint tests
│   ├── test_documents.py         # Document upload tests
│   ├── test_query.py             # Query endpoint tests
│   └── test_tenant_isolation.py  # Multi-tenancy tests
├── docker-compose.yml
├── prometheus.yml
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd rag-platform
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```

4. Start all services:
```bash
docker-compose up --build
```

5. Verify all services are healthy:
```bash
docker-compose ps
```

### Service URLs

| Service | URL |
|---------|-----|
| API (Swagger) | http://localhost:8000/docs |
| API Health | http://localhost:8000/health |
| API Metrics | http://localhost:8000/metrics |
| Grafana | http://localhost:3000 (admin/admin) |
| Prometheus | http://localhost:9090 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT |
| GET | `/api/v1/auth/me` | Get current user (protected) |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents` | Upload document (protected) |
| GET | `/api/v1/documents/{id}/status` | Check processing status (protected) |

### Query

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/query` | RAG query (protected) |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

## Usage Examples

### Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "SecurePass123!"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "SecurePass123!"}'
```

### Upload a Document

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@document.pdf"
```

### Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic of the document?"}'
```

## Multi-Tenancy

Every user is automatically assigned a unique `tenant_id` upon registration. All document uploads and queries are scoped to this tenant. Data isolation is enforced at:

- **Database level**: All queries include `WHERE tenant_id = ?`
- **Vector DB level**: Qdrant searches are filtered by `tenant_id` in the payload
- **API level**: Auth dependency extracts tenant from JWT token

## Monitoring

### Prometheus Metrics

The API exposes the following metrics at `/metrics`:

- `http_requests_total` — Total HTTP requests by method, endpoint, status
- `http_requests_latency_seconds` — Request latency histogram
- `rag_query_total` — Total RAG queries by tenant
- `rag_query_tokens_used_total` — Total LLM tokens consumed
- `document_uploads_total` — Total document uploads by tenant
- `http_active_requests` — Currently active requests

### Grafana Dashboard

Access Grafana at http://localhost:3000 with admin/admin credentials. The RAG Platform dashboard is auto-provisioned and includes:

- API Request Rate & Latency
- RAG Query Throughput
- Token Usage
- Document Uploads by Tenant
- Error Rate

## Running Tests

```bash
# Unit tests (no external services needed)
docker-compose exec api pytest tests/ -v

# Or run locally
pip install -r tests/requirements.txt
pytest tests/ -v
```

## Design Decisions

- **Repository Pattern**: Clean separation of data access from business logic
- **Service Layer**: Business logic isolated from HTTP concerns
- **DTOs (Schemas)**: Pydantic models for request/response validation
- **Background Processing**: Celery handles heavy document processing asynchronously
- **Cache-First Query**: Redis cache reduces LLM API costs for repeated queries
- **Tenant Isolation**: Every data access path is filtered by tenant_id from JWT
