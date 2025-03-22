import os
from langchain.vectorstores import Chroma
from langchain.embeddings import CohereEmbeddings
from langchain.schema import Document
from utils.cohere_client import cohere_client
from config.settings import (
    COHERE_API_KEY, 
    CASE_LAW_DB_PATH, 
    STATUTES_DB_PATH, 
    REGULATIONS_DB_PATH,
    EMBED_MODEL
)

class EmbeddingService:
    """Service to manage document embeddings and vector storage"""
    
    def __init__(self):
        # Initialize Cohere embeddings
        self.embeddings = CohereEmbeddings(
            cohere_api_key=COHERE_API_KEY,
            model=EMBED_MODEL
        )
        
        # Create directories if they don't exist
        for path in [CASE_LAW_DB_PATH, STATUTES_DB_PATH, REGULATIONS_DB_PATH]:
            os.makedirs(path, exist_ok=True)
        
        # Initialize vector stores
        self.vector_stores = {
            "case_law": Chroma(
                persist_directory=CASE_LAW_DB_PATH,
                embedding_function=self.embeddings
            ),
            "statutes": Chroma(
                persist_directory=STATUTES_DB_PATH,
                embedding_function=self.embeddings
            ),
            "regulations": Chroma(
                persist_directory=REGULATIONS_DB_PATH,
                embedding_function=self.embeddings
            )
        }
    
    def embed_documents(self, texts, metadatas=None, store_type="case_law"):
        """Embed and store documents in the specified vector store"""
        if store_type not in self.vector_stores:
            raise ValueError(f"Invalid store type: {store_type}. Choose from: {list(self.vector_stores.keys())}")
        
        # Create LangChain documents
        if metadatas:
            documents = [Document(page_content=text, metadata=meta) for text, meta in zip(texts, metadatas)]
        else:
            documents = [Document(page_content=text) for text in texts]
        
        # Add documents to vector store
        self.vector_stores[store_type].add_documents(documents)
        return len(documents)
    
    def search(self, query, store_type="case_law", k=5, filter=None, rerank=True):
        """Search for relevant documents in the specified vector store"""
        if store_type not in self.vector_stores:
            raise ValueError(f"Invalid store type: {store_type}. Choose from: {list(self.vector_stores.keys())}")
        
        # Get vector store
        store = self.vector_stores[store_type]
        
        # Search for documents
        if filter:
            results = store.similarity_search(query, k=k, filter=filter)
        else:
            results = store.similarity_search(query, k=k)
        
        # Apply reranking if requested
        if rerank and len(results) > 1:
            docs = [doc.page_content for doc in results]
            reranked = cohere_client.rerank(query=query, documents=docs, top_n=min(k, len(docs)))
            return [results[idx] for idx in reranked.indices]
        
        return results
    
    def direct_embed(self, text, input_type="search_document"):
        """Directly generate embeddings using Cohere's API"""
        return cohere_client.embed([text], input_type=input_type)[0]

# Create a singleton instance
embedding_service = EmbeddingService() 