# GenAiGenesis - Legal AI Assistant

An AI-powered legal advisory system that leverages Cohere's NLP capabilities to provide legal assistance.

## Features

- Document embedding and semantic search
- Legal document analysis
- Query understanding and processing
- Vector database storage for legal knowledge
- Client Consultation Agent (Model A) implementation
- Redis caching for efficient embedding storage and retrieval

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up Redis:
   ```
   # Using Docker
   docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
   
   # Or install Redis locally
   # See https://redis.io/docs/getting-started/installation/
   ```
5. Copy `.env.example` to `.env` and add your API keys:
   ```
   cp .env.example .env
   ```
6. Run the application:
   ```
   python -m app.flask_app
   ```

## Project Structure

```
backend/
├── app/
│   ├── flask_app.py           # Flask application 
│   ├── main.py                # FastAPI application
│   └── simple_app.py          # Simple Flask app
├── config/
│   └── settings.py            # Configuration settings
├── data/
│   └── vector_stores/         # Vector database storage
├── services/
│   ├── client_agent.py        # Client Consultation Agent (Model A)
│   ├── embedding_service.py   # Embedding and vector search
│   └── document_service.py    # Document processing
├── utils/
│   └── cohere_client.py       # Cohere API client
├── .env.example               # Example environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## API Endpoints

- `GET /`: Welcome message
- `GET /test`: Test endpoint
- `POST /api/embed`: Generate embedding for a query
- `POST /api/generate`: Generate text using Cohere
- `POST /api/client/understand`: Analyze client query using Client Consultation Agent
- `POST /api/client/respond`: Generate response to client query

## Efficient Use of Cohere Embeddings

The system uses Cohere's embedding API to represent text data in a high-dimensional vector space. To maximize efficiency:

1. **Input cleaning**: All inputs are automatically stripped of trailing whitespace to avoid API warnings.

2. **Redis Caching**: The Client Consultation Agent implements Redis-based caching for embeddings to provide:
   - Persistent storage across application restarts
   - Shared cache for multiple instances in distributed deployments
   - Configurable TTL (time-to-live) for cached embeddings (default: 24 hours)
   - Fallback to in-memory cache if Redis is unavailable

3. **RedisVL Integration**: We use RedisVL's CohereTextVectorizer for optimal integration with Redis:
   - Proper serialization of vector data
   - Consistent parameter formatting
   - Error handling and graceful fallbacks

4. **Embedding model**: We use `embed-english-v3.0` which is optimized for English text.

5. **Input type specification**: We specify `input_type="search_query"` to optimize embeddings for search scenarios.

6. **Parameters format**: All API calls are properly formatted to avoid warnings about invalid fields.

7. **Error handling**: Robust error handling ensures graceful failure when API calls don't succeed.

## Redis Vector Database Setup

For semantic search capabilities, the system can be extended to use Redis as a full vector database:

1. **Define a schema**: Create a schema for your vector index
2. **Initialize the Redis index**: Set up the appropriate index structure
3. **Load documents**: Embed and store your legal documents
4. **Query with filters**: Use Redis filters to enhance search precision

See the `services/client_agent.py` implementation for details on the Redis caching integration.

## Development Roadmap

1. Core Infrastructure & Embedding (Complete)
2. Client Consultation Agent (Model A) with Redis Caching (Complete)
3. Legal Research Agent (Model B)
4. Verification Agent (Model C)
5. Case Archive & Search
6. Lawyer Finder Service
7. API & Integration

## License

MIT 
