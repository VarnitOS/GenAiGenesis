#!/usr/bin/env python3
"""
Embedding generator module for creating vector representations of text.

This module handles:
1. Generating embeddings using Cohere's API
2. Optimizing embeddings for legal documents
3. Caching embeddings for performance
4. Quality verification of embeddings
"""

import os
import sys
import json
import time
import logging
import hashlib
from typing import List, Dict, Any, Optional, Union, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services
from services.embedding_service import embedding_service

logger = logging.getLogger("EmbeddingGenerator")

class EmbeddingGenerator:
    """Generate and manage embeddings for legal documents"""
    
    def __init__(self):
        self.embedding_model = "COHERE"  # Default model
        self.embedding_dimension = 1024  # Default dimension for Cohere embeddings
        self.use_cache = True
        self.stats = {
            "generated": 0,
            "cached": 0,
            "failed": 0,
            "avg_generation_time": 0
        }
    
    def generate(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate embeddings for text
        
        Args:
            text: Text to generate embeddings for
            metadata: Optional metadata to use for embedding customization
            
        Returns:
            Dictionary containing embedding and generation info
        """
        if not text:
            logger.warning("Attempted to generate embedding for empty text")
            return {
                "success": False,
                "error": "Empty text",
                "embedding": None,
                "embedding_model": self.embedding_model
            }
        
        # Calculate text hash for caching
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # Check cache if enabled
        if self.use_cache:
            cached_embedding = self._check_cache(text_hash)
            if cached_embedding is not None:
                self.stats["cached"] += 1
                return {
                    "success": True,
                    "embedding": cached_embedding,
                    "embedding_model": self.embedding_model,
                    "cached": True
                }
        
        # Generate embedding
        try:
            start_time = time.time()
            
            # Use embedding service
            if embedding_service:
                embedding = self._generate_with_service(text, metadata)
            else:
                embedding = self._generate_with_direct_api(text, metadata)
            
            generation_time = time.time() - start_time
            
            # Update stats
            self.stats["generated"] += 1
            self._update_avg_time(generation_time)
            
            # Cache embedding
            if self.use_cache and embedding is not None:
                self._cache_embedding(text_hash, embedding)
            
            # Verify embedding quality
            quality_info = self._verify_embedding_quality(embedding)
            
            return {
                "success": True,
                "embedding": embedding,
                "embedding_model": self.embedding_model,
                "dimension": len(embedding) if embedding else 0,
                "generation_time": generation_time,
                "quality": quality_info
            }
        
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            self.stats["failed"] += 1
            
            return {
                "success": False,
                "error": str(e),
                "embedding": None,
                "embedding_model": self.embedding_model
            }
    
    def generate_batch(self, texts: List[str], 
                      metadatas: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts
            metadatas: Optional list of metadata dictionaries
            
        Returns:
            List of embedding results
        """
        if not texts:
            return []
        
        if metadatas is None:
            metadatas = [None] * len(texts)
        
        # Generate embeddings for each text
        results = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if i < len(metadatas) else None
            result = self.generate(text, metadata)
            results.append(result)
        
        return results
    
    def _generate_with_service(self, text: str, 
                              metadata: Optional[Dict[str, Any]]) -> List[float]:
        """Generate embedding using the embedding service"""
        # Prepare document type for optimized embeddings
        doc_type = metadata.get("document_type", "default") if metadata else "default"
        collection = metadata.get("collection", "default") if metadata else "default"
        
        # Use embedding service to generate embedding
        if hasattr(embedding_service, 'get_embedding'):
            embedding = embedding_service.get_embedding(text)
            return embedding
        else:
            logger.warning("Embedding service lacking get_embedding method")
            return self._generate_with_direct_api(text, metadata)
    
    def _generate_with_direct_api(self, text: str, 
                                metadata: Optional[Dict[str, Any]]) -> List[float]:
        """Generate embedding using direct API call (fallback)"""
        try:
            import cohere
            
            # Get API key from environment
            api_key = os.environ.get("COHERE_API_KEY")
            
            if not api_key:
                logger.error("Cohere API key not found in environment")
                return []
            
            # Initialize client
            co = cohere.Client(api_key)
            
            # Get embedding
            response = co.embed(
                texts=[text],
                model="embed-english-v3.0",
                input_type="search_document"
            )
            
            return response.embeddings[0]
        
        except ImportError:
            logger.error("Cohere package not installed")
            return []
        except Exception as e:
            logger.error(f"Error in direct API call: {e}")
            return []
    
    def _check_cache(self, text_hash: str) -> Optional[List[float]]:
        """Check if embedding exists in cache"""
        try:
            if hasattr(embedding_service, 'get_cached_embedding'):
                return embedding_service.get_cached_embedding(text_hash)
            return None
        except Exception as e:
            logger.error(f"Error checking embedding cache: {e}")
            return None
    
    def _cache_embedding(self, text_hash: str, embedding: List[float]) -> None:
        """Cache embedding for future use"""
        try:
            if hasattr(embedding_service, 'cache_embedding'):
                embedding_service.cache_embedding(text_hash, embedding)
        except Exception as e:
            logger.error(f"Error caching embedding: {e}")
    
    def _update_avg_time(self, generation_time: float) -> None:
        """Update average generation time stat"""
        current_avg = self.stats["avg_generation_time"]
        total_generated = self.stats["generated"]
        
        if total_generated <= 1:
            self.stats["avg_generation_time"] = generation_time
        else:
            # Calculate new running average
            self.stats["avg_generation_time"] = (
                (current_avg * (total_generated - 1) + generation_time) / total_generated
            )
    
    def _verify_embedding_quality(self, embedding: List[float]) -> Dict[str, Any]:
        """Verify the quality of generated embedding"""
        if not embedding:
            return {"valid": False, "reason": "Empty embedding"}
        
        # Check dimension
        if len(embedding) != self.embedding_dimension:
            return {
                "valid": False, 
                "reason": f"Wrong dimension: {len(embedding)} (expected {self.embedding_dimension})"
            }
        
        # Check for NaN or infinity values
        if any(not isinstance(x, (int, float)) or float('nan') == x or float('inf') == abs(x) 
               for x in embedding):
            return {"valid": False, "reason": "Contains NaN or infinity values"}
        
        # Check variance/distribution
        # Simple check for all zeros or very low variance
        if all(abs(x) < 1e-6 for x in embedding):
            return {"valid": False, "reason": "All values near zero"}
        
        # Success
        return {"valid": True}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model"""
        return {
            "model": self.embedding_model,
            "dimension": self.embedding_dimension,
            "stats": self.stats
        }
    
    def set_model(self, model_name: str) -> None:
        """Set the embedding model"""
        self.embedding_model = model_name
        
        # Update dimension based on model
        if model_name == "COHERE":
            self.embedding_dimension = 1024  # Cohere's dimension 