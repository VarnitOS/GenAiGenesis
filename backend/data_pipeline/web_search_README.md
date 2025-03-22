# Web Search Module for the Legal Document Data Pipeline

This module extends the data pipeline with web search functionality, enabling on-demand discovery and processing of legal documents from the web.

## Overview

The web search module handles:

1. **Web Search**: Search for legal documents across authorized sources
2. **Content Scraping**: Download and extract content from search results
3. **Document Classification**: Determine document types (case law, statute, regulation)
4. **Pipeline Integration**: Process scraped content through the data pipeline
5. **Vector Storage**: Store processed documents in the vector database

## Features

- **Multiple Search Engines**: Support for Google, Google Scholar, and extensible to other engines
- **Authorized Sources**: Configurable list of trusted legal domains
- **Document Type Detection**: Automatic classification of legal documents
- **Recursive Crawling**: Optional following of links to specified depth
- **Parallel Processing**: Concurrent downloading and processing of documents
- **Fallback Mechanisms**: Default legal documents when search fails

## Usage

### Basic Usage

```python
from data_pipeline import DataPipeline, WebSearch

# Initialize pipeline and web search
pipeline = DataPipeline()
web_search = WebSearch(data_pipeline=pipeline)

# Search and process documents
result = web_search.search_and_process(
    query="Fourth Amendment privacy expectations",
    collection="case_law",
    search_engine="google_scholar",
    max_results=5,
    follow_links=False
)

# Print statistics
print(f"URLs found: {result['stats']['urls_found']}")
print(f"Documents processed: {result['stats']['documents_processed']}")
```

### Command Line Usage

```bash
# Basic search
python -m data_pipeline.web_search --query "Fourth Amendment privacy" --collection case_law

# Advanced options
python -m data_pipeline.web_search \
  --query "Fourth Amendment privacy" \
  --collection case_law \
  --search-engine google_scholar \
  --max-results 10 \
  --follow-links
```

### Demo Script

For a complete demonstration, use the demo script:

```bash
python -m scripts.demo_web_search \
  --query "Fourth Amendment privacy expectations" \
  --collection case_law \
  --search-engine google_scholar \
  --max-results 5
```

## Security and Ethics

The web search module includes several safeguards:

1. **Authorized Domains**: Only scrapes content from approved legal domains
2. **Rate Limiting**: Respects website rate limits
3. **User-Agent Identification**: Properly identifies itself in HTTP requests
4. **Error Handling**: Graceful handling of connection failures

## Configuration

The list of authorized domains can be configured in:
- `config/authorized_domains.json`

## Integration with Vector Search Engine

This module completes the Model B (Legal Research Agent) component of the architecture by:

1. Performing web searches for relevant legal information
2. Processing and embedding the search results
3. Storing the embeddings in the vector database
4. Making them available for semantic search through the vector search engine 