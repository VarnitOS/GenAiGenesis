# Model B: Legal Research Agent

The Legal Research Agent is a specialized component designed to conduct comprehensive legal research, retrieve relevant legal documents, and synthesize findings into coherent responses. It integrates with vector databases, web search capabilities, and Cohere's language models to provide accurate and contextually relevant legal information.

## Architecture

The Legal Research Agent consists of three primary components:

1. **Cohere Chat Integration (B1)**
   - Interfaces with Cohere's language models
   - Manages conversation context and history
   - Provides legal expertise through specialized system prompts

2. **Vector Search Engine (B2)**
   - Processes and stores legal documents using Cohere embeddings
   - Enables semantic search across multiple legal collections
   - Integrates web search for supplementary information
   - Maintains data quality through verification and cleanup processes

3. **Research Synthesis Chain (B3)**
   - Prioritizes and extracts key points from legal documents
   - Synthesizes information into comprehensive responses
   - Provides proper citations and maintains source attribution
   - Implements caching for improved performance

## Key Features

- **Multi-source research**: Searches across case law, statutes, regulations, and the web
- **Intelligent document prioritization**: Prioritizes documents based on relevance, recency, and authority
- **Contextual synthesis**: Generates responses that directly address the research query
- **Conversation management**: Maintains context across multiple interactions
- **Performance optimization**: Implements caching and efficient document processing

## API Endpoints

The following endpoints are available for interacting with the Legal Research Agent:

- `POST /api/research/query`: Conducts comprehensive research on a legal query
- `POST /api/research/chat`: Direct conversation with the legal agent
- `GET /api/research/conversation/<id>`: Retrieves conversation history
- `DELETE /api/research/conversation/<id>`: Clears conversation history
- `POST /api/research/context`: Adds research context to the conversation
- `DELETE /api/research/context`: Clears research context

## Usage

### Basic Research Query

```python
import requests
import json

url = "http://localhost:5000/api/research/query"
payload = {
    "query": "What is the standard for a reasonable search under the Fourth Amendment?",
    "collections": ["case_law", "statutes"],
    "use_web_search": True,
    "max_web_results": 5
}

response = requests.post(url, json=payload)
results = response.json()

print(results["research"])
```

### Chat Interaction

```python
import requests
import json

url = "http://localhost:5000/api/research/chat"
payload = {
    "message": "What are the exceptions to the exclusionary rule?",
    "conversation_id": "optional-previous-conversation-id",
    "include_context": True
}

response = requests.post(url, json=payload)
results = response.json()

print(results["text"])
```

## Testing

You can test the Legal Research Agent using the provided test script:

```bash
# Test the complete workflow
python scripts/test_research_agent.py --query "What are the elements of a valid contract?"

# Test individual components
python scripts/test_research_agent.py --component chat
python scripts/test_research_agent.py --component web --query "Fourth Amendment search"
python scripts/test_research_agent.py --component synthesis
python scripts/test_research_agent.py --component vector --collection case_law
```

## Environment Requirements

Make sure the following environment variables are set:

- `COHERE_API_KEY`: Your Cohere API key
- `AWS_ACCESS_KEY_ID`: AWS access key for S3 storage (if using S3)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 storage (if using S3)
- `S3_BUCKET_NAME`: S3 bucket for vector database persistence (if using S3)

## Dependencies

- `cohere`: For embeddings and chat capabilities
- `chromadb`: Vector database for document storage
- `redis`: For caching synthesis results
- `flask`: For API endpoints
- Various libraries for document processing and web search 