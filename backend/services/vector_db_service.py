import os
import json
from typing import List, Dict, Any, Optional
from services.embedding_service import embedding_service
import cohere
import chromadb
from chromadb.utils.embedding_functions import CohereEmbeddingFunction


class VectorDBService:
    """Service for managing vector database operations for legal knowledge."""
    
    def __init__(self):
        self.co = cohere.Client(os.environ.get('COHERE_API_KEY'))

        # Initialize ChromaDB with Cohere embedding function
        self.embedding_function = CohereEmbeddingFunction(api_key=os.environ.get('COHERE_API_KEY'), model_name="embed-english-v3.0")
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")  # Stores the DB locally
        self.collection = self.chroma_client.get_or_create_collection(name="documents", embedding_function=self.embedding_function)




        # """Initialize the vector database service."""
        # self.embedding_service = embedding_service
        
        # Statistics tracking
        self.stats = {
            "case_law": {"documents": 0, "embeddings": 0},
            "statutes": {"documents": 0, "embeddings": 0},
            "regulations": {"documents": 0, "embeddings": 0}
        }
        
        # Load stats if they exist
        self._load_stats()
    
    def _load_stats(self):
        """Load statistics from file if available."""
        stats_path = os.path.join(os.getcwd(), "data", "stats.json")
        if os.path.exists(stats_path):
            try:
                with open(stats_path, 'r') as f:
                    self.stats = json.load(f)
            except Exception as e:
                print(f"Error loading stats: {e}")
    
    def _save_stats(self):
        """Save statistics to file."""
        stats_path = os.path.join(os.getcwd(), "data", "stats.json")
        try:
            os.makedirs(os.path.dirname(stats_path), exist_ok=True)
            with open(stats_path, 'w') as f:
                json.dump(self.stats, f)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def import_case_law(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, 
                        ids: Optional[List[str]] = None) -> int:
        """Import case law documents into vector database.
        
        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            Number of documents imported
        """
        self.embedding_service.add_documents(
            documents=texts,
            metadatas=metadatas or [{}] * len(texts),
            collection_name="case_law",
            ids=ids
        )
        
        # Update stats
        self.stats["case_law"]["documents"] += len(texts)
        self.stats["case_law"]["embeddings"] += len(texts)
        self._save_stats()
        
        return len(texts)
    
    def import_statutes(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, 
                        ids: Optional[List[str]] = None) -> int:
        """Import statute documents into vector database.
        
        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            Number of documents imported
        """
        self.embedding_service.add_documents(
            documents=texts,
            metadatas=metadatas or [{}] * len(texts),
            collection_name="statutes",
            ids=ids
        )
        
        # Update stats
        self.stats["statutes"]["documents"] += len(texts)
        self.stats["statutes"]["embeddings"] += len(texts)
        self._save_stats()
        
        return len(texts)
    
    def import_regulations(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, 
                          ids: Optional[List[str]] = None) -> int:
        """Import regulation documents into vector database.
        
        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            Number of documents imported
        """
        self.embedding_service.add_documents(
            documents=texts,
            metadatas=metadatas or [{}] * len(texts),
            collection_name="regulations",
            ids=ids
        )
        
        # Update stats
        self.stats["regulations"]["documents"] += len(texts)
        self.stats["regulations"]["embeddings"] += len(texts)
        self._save_stats()
        
        return len(texts)
    
    def bulk_import(self, data_dict: Dict[str, Dict]) -> Dict[str, int]:
        """Bulk import documents into multiple collections.
        
        Args:
            data_dict: Dictionary mapping collection names to document data
                Each collection should have 'texts' and optionally 'metadatas' and 'ids'
                
        Returns:
            Dictionary mapping collection names to number of documents imported
        """
        results = {}
        
        for collection_name, data in data_dict.items():
            if collection_name == "case_law":
                results[collection_name] = self.import_case_law(
                    texts=data.get("texts", []),
                    metadatas=data.get("metadatas"),
                    ids=data.get("ids")
                )
            elif collection_name == "statutes":
                results[collection_name] = self.import_statutes(
                    texts=data.get("texts", []),
                    metadatas=data.get("metadatas"),
                    ids=data.get("ids")
                )
            elif collection_name == "regulations":
                results[collection_name] = self.import_regulations(
                    texts=data.get("texts", []),
                    metadatas=data.get("metadatas"),
                    ids=data.get("ids")
                )
            else:
                raise ValueError(f"Invalid collection name: {collection_name}")
        
        return results
    
    def search(self, query: str, collection_name: str = "case_law", top_k: int = 5) -> Dict[str, Any]:
        """Search for similar documents across collections.
        
        Args:
            query: Query text
            collection_name: Name of collection to search
            top_k: Number of results to return
            
        Returns:
           reranked results
        """
        # results = self.embedding_service.similarity_search(
        #     query=query,
        #     collection_name=collection_name,
        #     top_k=top_k
        # )
        
        # return {
        #     "query": query,
        #     "results": results
        # }
            # Step 1: Retrieve candidates from ChromaDB
        search_results = self.collection.query(query_texts=[query], n_results=top_k)

        if not search_results['documents'][0]:  # No results found
            return []

        # Step 2: Rerank results using Cohere
        rerank_results = self.co.rerank(
            model="rerank-english-v2.0",
            query=query,
            documents=search_results['documents'][0],  # Extract documents from ChromaDB results
            top_n=top_k
        )

        return rerank_results  # Returns reranked documents with relevance scores
    
    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics about the vector databases.
        
        Returns:
            Dictionary containing statistics
        """
        return self.stats

# Create a singleton instance
vector_db_service = VectorDBService() 