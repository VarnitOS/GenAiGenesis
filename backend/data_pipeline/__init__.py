"""
GenAI Data Pipeline Package

This package provides a comprehensive data pipeline for processing, embedding, 
and storing legal documents in the vector search engine.
"""

__all__ = [
    'DataPipeline',
    'DocumentProcessor',
    'EmbeddingGenerator',
    'MetadataExtractor',
    'WebSearch'
]

from .pipeline import DataPipeline
from .processor import DocumentProcessor
from .embeddings import EmbeddingGenerator
from .metadata import MetadataExtractor
from .web_search import WebSearch 