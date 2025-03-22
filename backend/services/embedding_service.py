import os
from dotenv import load_dotenv
import chromadb
import numpy as np
import cohere
from pathlib import Path
import redis
import pickle
import json
from services.s3_vector_store import s3_vector_store
import time
import tempfile
import shutil

# Load environment variables
load_dotenv()

# Configure temporary directory for ChromaDB
TEMP_DB_PATH = os.path.join(tempfile.gettempdir(), "chromadb_temp")
Path(TEMP_DB_PATH).mkdir(parents=True, exist_ok=True)

# Initialize Redis for caching embeddings
try:
    # Check for Docker environment
    redis_host = os.environ.get('REDIS_HOST', 'localhost')
    redis_port = int(os.environ.get('REDIS_PORT', 6379))
    redis_client = redis.Redis(host=redis_host, port=redis_port)
    redis_client.ping()  # Check connection
    print(f"Redis connection established for embedding cache at {redis_host}:{redis_port}")
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"Redis connection failed: {e}")
    print("Embedding caching will be disabled")
    REDIS_AVAILABLE = False

# Check if S3 storage is enabled
S3_ENABLED = os.getenv("S3_ENABLED", "False").lower() in ("true", "1", "t")
if not S3_ENABLED:
    raise ValueError("S3 storage must be enabled for this configuration. Set S3_ENABLED=True in .env file.")
else:
    print("S3 storage for vector database is enabled")

class EmbeddingService:
    """Service for generating and managing embeddings using Cohere API with S3 as primary storage"""

    def __init__(self):
        # Initialize tracking dictionary for last S3 sync times FIRST
        # to avoid attribute error during initialization
        self.last_s3_sync = {
            "case_law": 0,
            "statutes": 0,
            "regulations": 0,
            "dummy_test_collection": 0
        }
        
        # Initialize Cohere client
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY not found in environment variables. Please add it to .env file.")
        
        self.co = cohere.Client(api_key)
        print("Initializing Cohere embeddings")
        
        # AWS S3 auto-sync interval (in seconds)
        self.s3_sync_interval = int(os.getenv("S3_SYNC_INTERVAL", "60"))  # Default 1 minute for S3-only mode
        
        # Initialize ChromaDB client based on configuration
        chroma_mode = os.getenv("CHROMA_MODE", "local").lower()
        
        if chroma_mode == "http" or chroma_mode == "remote":
            # Use HTTP client for remote ChromaDB server
            chroma_host = os.getenv("CHROMA_HOST", "localhost")
            chroma_port = int(os.getenv("CHROMA_PORT", 8000))
            chroma_ssl = os.getenv("CHROMA_SSL", "False").lower() == "true"
            chroma_headers = json.loads(os.getenv("CHROMA_HEADERS", "{}"))
            
            print(f"Connecting to remote ChromaDB server at {chroma_host}:{chroma_port}")
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=chroma_port,
                ssl=chroma_ssl,
                headers=chroma_headers
            )
        else:
            # Use in-memory client that loads from S3
            print(f"Using in-memory ChromaDB with S3 backend")
            self.client = chromadb.Client()
            
            # Create a temporary path for downloading collections
            self.temp_path = TEMP_DB_PATH
            
            # Download collections from S3 on startup
            self._load_collections_from_s3()
        
        # Create collections if they don't exist
        self.case_law_collection = self.get_or_create_collection("case_law")
        self.statutes_collection = self.get_or_create_collection("statutes")
        self.regulations_collection = self.get_or_create_collection("regulations")
    
    def _load_collections_from_s3(self):
        """Load collections from S3 on startup"""
        try:
            # Get list of collections from S3
            collections = ["case_law", "statutes", "regulations", "dummy_test_collection"]
            
            for collection_name in collections:
                try:
                    # Download the collection from S3
                    success = s3_vector_store.download_collection(collection_name)
                    if success:
                        print(f"Collection {collection_name} downloaded from S3")
                        self.last_s3_sync[collection_name] = time.time()
                except Exception as e:
                    print(f"Error downloading collection {collection_name} from S3: {e}")
        except Exception as e:
            print(f"Error loading collections from S3: {e}")
    
    def get_or_create_collection(self, name):
        """Get a collection by name or create it if it doesn't exist"""
        try:
            return self.client.get_collection(name=name)
        except Exception:
            collection = self.client.create_collection(name=name)
            # Save new collection to S3
            self._save_collection_to_s3(name)
            return collection
    
    def _save_collection_to_s3(self, collection_name):
        """Save a collection to S3"""
        try:
            s3_vector_store.upload_collection(collection_name)
            self.last_s3_sync[collection_name] = time.time()
            print(f"Collection {collection_name} saved to S3")
        except Exception as e:
            print(f"Error saving collection {collection_name} to S3: {e}")
    
    def get_collection(self, collection_name):
        """Get a collection by name"""
        if collection_name == "case_law":
            return self.case_law_collection
        elif collection_name == "statutes":
            return self.statutes_collection
        elif collection_name == "regulations":
            return self.regulations_collection
        else:
            raise ValueError(f"Unknown collection: {collection_name}")
    
    def generate_embeddings(self, texts, model="embed-english-v3.0", cache_key=None):
        """
        Generate embeddings for a list of texts using Cohere API
        With Redis caching if available
        """
        if not texts:
            return []
        
        # If Redis is available and cache_key is provided, try to get from cache
        if REDIS_AVAILABLE and cache_key:
            cached_embeddings = redis_client.get(f"embed:{cache_key}")
            if cached_embeddings:
                return pickle.loads(cached_embeddings)
        
        # Generate embeddings using Cohere
        response = self.co.embed(
            texts=texts,
            model=model,
            input_type="search_document"
        )
        
        embeddings = response.embeddings
        
        # Cache embeddings if Redis is available and cache_key is provided
        if REDIS_AVAILABLE and cache_key:
            redis_client.set(
                f"embed:{cache_key}",
                pickle.dumps(embeddings),
                ex=86400  # Cache for 24 hours
            )
        
        return embeddings
    
    def add_documents(self, documents, metadatas, collection_name, ids=None):
        """Add documents to the specified collection"""
        if not documents:
            return
        
        collection = self.get_collection(collection_name)
        
        # Generate embeddings
        embeddings = self.generate_embeddings(documents)
        
        # Add documents to collection
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids if ids else [f"doc-{i}" for i in range(len(documents))]
        )
        
        # Save to S3 immediately after adding documents
        self._save_collection_to_s3(collection_name)
    
    def similarity_search(self, query, collection_name, top_k=5):
        """Search for similar documents in the specified collection"""
        collection = self.get_collection(collection_name)
        
        # Generate query embedding (with a specific cache key for this query)
        query_embedding = self.generate_embeddings(
            [query],
            cache_key=f"query:{query}"
        )[0]
        
        # Search collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i] if results['metadatas'][0] else {},
                "id": results['ids'][0][i]
            })
        
        return formatted_results
    
    def sync_all_with_s3(self):
        """Manually sync all collections with S3"""
        try:
            # For S3-only mode, we're saving to S3 not syncing
            for collection_name in ["case_law", "statutes", "regulations"]:
                self._save_collection_to_s3(collection_name)
                
            return {"success": True, "message": "All collections saved to S3"}
        except Exception as e:
            return {"error": str(e)}

# Create a singleton instance
embedding_service = EmbeddingService()