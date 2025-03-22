# Legal Document Data Pipeline

A comprehensive data pipeline for processing, embedding, and storing legal documents for vector search.

## Overview

This data pipeline handles the entire workflow from document ingestion to searchable vector embeddings:

1. **Document Processing**: Extract text from various file formats (PDF, DOCX, TXT, JSON, HTML)
2. **Text Preprocessing**: Clean and normalize text for optimal embedding generation
3. **Metadata Extraction**: Extract structured metadata from legal documents
4. **Embedding Generation**: Generate high-quality vector embeddings using Cohere
5. **Quality Verification**: Ensure document and embedding quality
6. **Vector Storage**: Store embeddings in ChromaDB with S3 synchronization
7. **Monitoring & Analytics**: Track pipeline metrics and collection quality

## Components

The pipeline consists of several modular components:

- **DocumentProcessor**: Extracts and preprocesses text from documents
- **MetadataExtractor**: Extracts and enriches metadata from document content
- **EmbeddingGenerator**: Generates vector embeddings using Cohere
- **DataPipeline**: Orchestrates the entire workflow

## Usage

### Basic Usage

```python
from data_pipeline import DataPipeline

# Initialize pipeline
pipeline = DataPipeline()

# Process documents
stats = pipeline.process_documents(
    source_dir="data/raw/case_law",
    collection="case_law",
    batch_size=10,
    recursive=True
)

print(f"Processed {stats['succeeded']} documents successfully")
```

### Command Line Usage

```bash
# Process documents
python -m data_pipeline.pipeline --source-dir data/raw/case_law --collection case_law --batch-size 10 --recursive

# Analyze collection
python -m data_pipeline.pipeline --collection case_law --analyze
```

## Document Collections

The pipeline supports multiple document collections:

- **case_law**: Court opinions and decisions
- **statutes**: Statutory law and legislation
- **regulations**: Administrative regulations and rules

## Dependencies

- Python 3.8+
- Cohere API key for embeddings
- ChromaDB for vector storage
- Redis for embedding caching (optional)
- S3 for vector database persistence (optional)

## Installation

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```
   COHERE_API_KEY=your_api_key
   REDIS_HOST=localhost
   REDIS_PORT=6379
   S3_BUCKET=your-bucket-name
   S3_PREFIX=vector_db/
   ```

## Document Quality

The pipeline ensures document quality through:

1. **Text validation**: Minimum word count and content checks
2. **Metadata extraction**: Structured metadata for better searchability
3. **Embedding verification**: Validating embedding dimensions and distributions
4. **Collection analysis**: Tools for analyzing document collections

## Performance

The pipeline includes several performance optimizations:

- **Batch processing**: Process documents in configurable batches
- **Concurrent processing**: Use multiple threads for document processing
- **Embedding caching**: Cache embeddings to avoid regeneration
- **S3 synchronization**: Persist vector database to S3 for durability 