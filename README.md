# 📹 TexLink AI Video Chat Microservice

> A high-performance, async B2B microservice that enables "Chat with Video" capabilities for LMS platforms.
> Built with **FastAPI**, **PostgreSQL (Async)**, **Redis**, and **LiteLLM**.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)

## 📖 Overview

It is a **B2B Microservice** designed to integrate into Learning Management Systems (LMS). It allows students to have context-aware, real-time conversations with educational videos.

This service is architected for **Multi-Tenancy**, **High Concurrency**, and **LLM Agnosticism**, making it capable of serving multiple platforms simultaneously with strict data isolation.

---

## 🏗 Architecture

The system follows an **Event-Driven, Async Architecture** to handle high throughput without blocking.

```mermaid
graph TD
    Client[LMS Client / Frontend] -->|REST API| LB[FastAPI Gateway]

    subgraph "Microservice Core"
        LB -->|Auth & Routing| Controller[Async Controller]
        Controller -->|Read/Write| DB[(PostgreSQL)]
        Controller -->|State/History| Cache[(Redis)]

        subgraph "AI Gateway (LiteLLM)"
            Controller -->|Dynamic Route| AI_Router[Model Router]
            AI_Router -->|LLM Model| Gemini[Gemini 2.5 Flash lite]
        end
    end

    DB -->|Transcripts & Metadata| Controller
    Cache -->|Session History| Controller
    AI_Router -->|Streaming Response| LB
```

---

## 🚀 Key Features

### 🔐 1. B2B Multi-Tenancy (Security)

- **Strict Isolation**: Data is isolated by TenantID. Platform A cannot access Platform B's data.
- **API Key Auth**: Secure, header-based authentication (`x-api-key`) for every request.

### ⚡ 2. Fully Asynchronous (Performance)

- Built on `asyncpg` (PostgreSQL) and `redis-py` (Async).
- Non-blocking I/O allows a single instance to handle thousands of concurrent chat sessions efficiently.

### 🧠 3. Stateful "Memory" Engine

- **Session Management**: Uses Redis to store short-term conversation history with TTL (Time-To-Live).
- **Context Injection**: Intelligently injects chat history + video transcript into the LLM context window.

---

## 🛠 Tech Stack

| Component         | Technology              | Reason                                                      |
| ----------------- | ----------------------- | ----------------------------------------------------------- |
| Framework         | FastAPI (Python)        | High performance, native Async support, auto-documentation. |
| Database          | PostgreSQL + asyncpg    | Reliable relational storage for Tenants & Transcripts.      |
| Caching           | Redis                   | Low-latency storage for chat session history (Memory).      |
| LLM Orchestration | LiteLLM                 | Unified interface for 100+ LLM providers.                   |
| Package Manager   | uv                      | Ultra-fast Python dependency management.                    |
| Deployment        | Docker & Docker Compose | Containerized for easy scaling and deployment.              |

---

## 🔌 API Documentation

Once running, access the interactive routes at: **http://localhost:8000/docs**

### Core Endpoints

| Method | Endpoint               | Description                                      |
| ------ | ---------------------- | ------------------------------------------------ |
| POST   | `/api/v1/ingest/video` | Upload a video transcript (Secure B2B Endpoint). |
| POST   | `/api/v1/chat/`        | Send a message to the AI about a specific video. |
| GET    | `/health`              | Service health check.                            |

---

## 💻 Local Setup

### Prerequisites

- Python 3.11+ (or `uv` installed)
- Docker (optional, for Redis/Postgres)

### 1. Clone & Install

```bash
git clone https://github.com/Rohit1419/LLM-video-agent.git
cd LLM-video-agent

# Install dependencies using uv
uv sync
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
# Database & Cache
DATABASE_URL="postgresql+asyncpg://user:password@localhost/texlink_db"
REDIS_URL="redis://localhost:6379"

# AI Provider Keys (Add whichever you use)
GEMINI_API_KEY="your_google_key"

```

### 3. Run Services

Start the database and cache using Docker:

```bash
docker-compose up -d postgres redis
```

### 4. Start the Microservice

```bash
uv run main.py
```

Server will start at **http://0.0.0.0:8000**

---

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or support, reach out at: rohitgite03@gmail.com || +91 7823846641
