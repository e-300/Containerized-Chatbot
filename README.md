# AI Chatbot with Production Infrastructure

A production-ready Containerized AI chatbot built with Claude API, featuring Redis caching, comprehensive observability with Prometheus/Grafana, and automated CI/CD pipelines. 

My goal for this Project was to learn and demonstrate enterprise level software engineering practices like:

- **Infrastructure-as-Code**: Complete containerized deployment with orchestration
- **Observability-First Design**: Comprehensive metrics collection and visualization
- **Reliability Engineering**: Error handling, caching strategies, health checks
- **DevOps Automation**: CI/CD pipeline with automated testing and validation
- **Production Thinking**: Design decisions made for scalability and maintainability

---

## Getting Started

### 1. Clone Repo
```bash
git clone https://github.com/eb-300/ai-agent-mvp.git
cd ai-agent-mvp
```

### 2. Configure Environment Variables
Create `.env` file in project root:

**Required:**
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**Optional (defaults provided):**
```
REDIS_HOST=redis
REDIS_PORT=6379
```

### 3. Start Services
```bash
docker compose up
```

This will start four Containers:
- **AI Agent**: FastAPI server on http://localhost:8000
- **Redis**: Cache server on localhost:6379
- **Prometheus**: Metrics collector on http://localhost:9090
- **Grafana**: Dashboard on http://localhost:3000

### 4. Verify Installation

**Check agent health:**
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy"}`

**Check Prometheus targets:**
```bash
curl http://localhost:9090/-/healthy
```
Expected: `Prometheus is Healthy.`

**Grafana Dashboard:**
- URL: http://localhost:3000
- Credentials: `admin/admin`

### 5. Test in CLI
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Docker?"}'
```

### 6. Clean Up

**Stop containers:**
```bash
docker-compose down
```

**Remove containers, networks, and volumes:**
```bash
docker-compose down -v
```

**Remove images:**
```bash
docker-compose down --rmi all
```

---

## Grafana Dashboard

<img width="2903" alt="Grafana Dashboard Screenshot" src="https://github.com/user-attachments/assets/bf19c85d-454d-4555-952b-6c1ee0039ab9" />

---

## Tech Stack

- **Runtime**: Python 3.10.12
- **API Framework**: FastAPI with Pydantic validation
- **LLM Provider**: Anthropic Claude (Haiku 3.5)
- **Caching Layer**: Redis 7 (Alpine)
- **Containerization**: Docker & Docker Compose
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions
- **Testing**: Pytest with coverage reporting
- **Code Quality**: Flake8, Black

---

## Architecture Overview
```
   ┌─────────────┐
   │   Client    │
   └──────┬──────┘
          │ HTTP POST /chat
          ▼
   ┌─────────────────────────────────────┐
   │         FastAPI Layer               │
   │  • Request validation (Pydantic)    │
   │  • Metrics instrumentation          │
   │  • Error handling                   │
   └──────┬──────────────────────────────┘
          │
          ▼
   ┌─────────────────────────────────────┐
   │      AnthropicAgent Layer           │
   │  • Cache key generation (SHA-256)   │
   │  • Redis cache check                │
   │  • Response extraction              │
   └──────┬──────────────────────────────┘
          │
          ├─── Cache Hit? ───► Redis ────┐
          │                              │
          └─── Cache Miss ───► Claude API │
                                          │
                               Response ◄─┘
          
   ┌─────────────────────────────────────┐
   │      Monitoring Stack               │
   │  Prometheus ──scrapes──► /metrics   │
   │       │                             │
   │       └──► Grafana (visualization)  │
   └─────────────────────────────────────┘
```

---

## Three-Layer Architecture

### Layer 1: Abstract Interface (`agent/base.py`)
- Abstract `AI_Platform` interface
- Enables future support for various LLM providers
- Enforces consistent behavior

### Layer 2: Implementation (`agent/claude.py`)
- `AnthropicAgent` class extends from the Abstract Interface
- Claude API integration
- Redis Caching Logic with:
  - SHA-256 cache keys with collision resistance
  - Connection pooling

### Layer 3: API Exposure (`agent/api.py`)
- FastAPI REST endpoint with Pydantic Validation
- Prometheus Metrics captured:
  - Request count
  - Response time
  - Cache miss/hit
- Health check endpoint for container orchestration

---

## Features

### Core Functionality
✅ RESTful chat API with JSON request/response  
✅ Input validation and sanitization  
✅ Comprehensive error handling with informative messages  
✅ Empty input detection and rejection  

### Caching & Performance
✅ Redis-based response caching (1-hour TTL)  
✅ Graceful degradation when Redis unavailable  
✅ Connection pooling for Redis client  
✅ Cache key generation using system prompt + user input  

### Observability
✅ Prometheus metrics endpoint (`/metrics`)  
✅ Request counter with success/error labels  
✅ Response time histogram  
✅ Cache hit/miss counters  
✅ Error type categorization  
✅ Pre-configured Grafana dashboard  

### Infrastructure
✅ Multi-container orchestration (Agent, Redis, Prometheus, Grafana)  
✅ Health check endpoints for monitoring  
✅ Automated container restarts  
✅ Volume management for persistent data  
✅ Network isolation between services  

### CI/CD
✅ Automated testing on push/PR  
✅ Code linting with Flake8  
✅ Test coverage reporting  
✅ Docker image build validation  
✅ Branch protection ready  

---

## Project Status

**Stage 1 is Complete:**
- [x] Project structure and planning
- [x] Core agent implementation
- [x] FastAPI REST API with validation
- [x] Docker containerization
- [x] Docker Compose orchestration
- [x] Redis server-side caching
- [x] Prometheus and Grafana monitoring
- [x] GitHub Actions CI/CD pipeline
- [x] Documentation and polish

**Next Stage:** Kubernetes Deployment with a proper use case that allows horizontal scaling

---

## CI/CD Pipeline

The pipeline runs on every push and pull request to `main` and `develop` branches.

### Pipeline Stages:

**1. Test Job:**
- Checkout code
- Set up Python 3.10
- Install dependencies
- Run Flake8 linting
- Execute pytest with coverage reporting

**2. Docker Job** (runs after tests pass):
- Checkout code
- Build Docker image with commit SHA tag
- Verify image creation

<img width="2903" alt="GitHub Actions Screenshot - Successful Pipeline" src="https://github.com/user-attachments/assets/b0e1b91b-9c4b-4200-b9e9-ad3e62eecd50" />

---

## What I Learned

Building this project taught me:

### Infrastructure & DevOps:
- Container orchestration with Docker Compose
- Metrics-driven development with Prometheus
- Visualization best practices with Grafana
- CI/CD pipeline design with GitHub Actions

### Software Architecture:
- Abstract interfaces for flexibility (Strategy pattern)
- Separation of concerns in layered architecture
- Error handling and graceful degradation
- Caching strategies for external APIs

### Production Engineering:
- Observability instrumentation from day one
- Health checks for container orchestration
- Connection pooling for resource efficiency
- Cost optimization through intelligent caching

### Python Ecosystem:
- FastAPI for high-performance APIs
- Pydantic for data validation
- Pytest for comprehensive testing
- Type hints for code clarity

---

## License

MIT

---

## Changelog

### v1.0.0 (11-25-2025)

✨ Initial MVP release  
✨ Three-layer architecture implementation  
✨ Redis caching with fallback  
✨ Prometheus + Grafana monitoring  
✨ CI/CD pipeline with GitHub Actions  
✨ Comprehensive test suite (95% coverage)  
✨ Docker Compose orchestration  
📝 Complete documentation
