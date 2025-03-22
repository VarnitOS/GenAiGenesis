# GenAiGenesis - Legal AI Assistant

An AI-powered legal advisory system that leverages Cohere's NLP capabilities to provide legal assistance.

## Features

- Document embedding and semantic search
- Legal document analysis
- Query understanding and processing
- Vector database storage for legal knowledge
- Client Consultation Agent (Model A) implementation

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
4. Copy `.env.example` to `.env` and add your API keys:
   ```
   cp .env.example .env
   ```
5. Run the application:
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

## Development Roadmap

1. Core Infrastructure & Embedding (Complete)
2. Client Consultation Agent (Model A) (Complete)
3. Legal Research Agent (Model B)
4. Verification Agent (Model C)
5. Case Archive & Search
6. Lawyer Finder Service
7. API & Integration

## License

MIT 
