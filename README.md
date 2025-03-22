# GenAiGenesis - LegalMind AI

An AI-powered legal advisory system leveraging Cohere's LLM capabilities for advanced legal assistance.

## Features

- Document embedding and semantic search
- Legal document analysis
- Query understanding and processing
- Vector database storage for legal knowledge
- Client Consultation Agent (Model A) implementation
- Redis caching for efficient embedding storage and retrieval

## Getting Started

### Using Docker (Recommended)

The easiest way to run the system is with Docker:

1. Clone the repository:
   ```
   git clone https://github.com/VarnitOS/GenAiGenesis.git
   cd GenAiGenesis
   ```

2. Copy the environment example and add your API keys:
   ```
   cp backend/.env.example backend/.env
   ```
   Edit the `backend/.env` file and add your Cohere API key.

3. Run the system with Docker:
   ```
   ./run.sh
   ```

4. Access the system:
   - API: http://localhost:8080
   - Redis GUI: http://localhost:8001

### Manual Setup (Development)

1. Set up Python environment (Python 3.9+ required)
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Set up Redis:
   ```
   docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
   ```

3. Run the Flask app:
   ```
   cd backend
   PYTHONPATH=/path/to/GenAiGenesis/backend python -m app.flask_app
   ```

## API Endpoints

- `GET /`: Welcome message
- `GET /test`: Test endpoint
- `POST /api/embed`: Generate embedding for a query
- `POST /api/generate`: Generate text using Cohere
- `POST /api/client/understand`: Analyze client query
- `POST /api/client/respond`: Generate response to client query

## Architecture

The system uses a modular design with three main components:
- Client Consultation Agent (Model A)
- Redis for embedding caching and vector storage
- Flask API for client access

The Redis integration provides:
- Persistent caching of embeddings
- Improved performance with reduced API calls
- Failover to in-memory cache if Redis is unavailable

## Project Structure

This repository contains multiple components:

- `backend/`: The LegalMind AI backend system with Model A (Client Consultation Agent)

## License

MIT 