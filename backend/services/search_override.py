# Override for search functionality to ensure it always checks for documents
import os
import json
from typing import Dict, Any
from pathlib import Path

# Store original search function
_original_search = None

def recreate_collection(collection, collection_name):
    """Recreate a collection with the proper dimensionality"""
    from services.embedding_service import embedding_service
    
    print(f"Recreating collection {collection_name} due to dimension mismatch")
    
    # Delete the existing collection
    try:
        embedding_service.client.delete_collection(collection_name)
        print(f"Deleted collection {collection_name}")
    except Exception as e:
        print(f"Error deleting collection {collection_name}: {e}")
    
    # Create a new collection
    if collection_name == "case_law":
        embedding_service.case_law_collection = embedding_service.client.create_collection(name=collection_name)
        new_collection = embedding_service.case_law_collection
    elif collection_name == "statutes":
        embedding_service.statutes_collection = embedding_service.client.create_collection(name=collection_name)
        new_collection = embedding_service.statutes_collection
    elif collection_name == "regulations":
        embedding_service.regulations_collection = embedding_service.client.create_collection(name=collection_name)
        new_collection = embedding_service.regulations_collection
    else:
        print(f"Unknown collection: {collection_name}")
        return None
    
    print(f"Created new collection {collection_name}")
    return new_collection

def ensure_collection_has_documents(collection, collection_name):
    """Ensure a collection has documents by adding them if needed"""
    # Check if collection has documents
    try:
        data = collection.get()
        if len(data.get('ids', [])) == 0:
            print(f"Collection {collection_name} is empty. Adding sample documents...")
            
            # Import sample documents
            from scripts.populate_vector_db import CASE_LAW_DOCUMENTS, STATUTE_DOCUMENTS, REGULATION_DOCUMENTS
            
            # Select documents based on collection name
            if collection_name == "case_law":
                docs_data = CASE_LAW_DOCUMENTS
            elif collection_name == "statutes":
                docs_data = STATUTE_DOCUMENTS
            elif collection_name == "regulations":
                docs_data = REGULATION_DOCUMENTS
            else:
                return  # Unknown collection
            
            # Extract document data
            documents = [doc["document"] for doc in docs_data]
            metadatas = [doc["metadata"] for doc in docs_data]
            ids = [doc["id"] for doc in docs_data]
            
            # Add documents to collection
            collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            
            print(f"Added {len(documents)} documents to {collection_name} collection")
            
            # Verify documents were added
            data = collection.get()
            doc_count = len(data.get('ids', []))
            print(f"Collection now has {doc_count} documents")
    except Exception as e:
        print(f"Error ensuring collection has documents: {e}")

def patch_vector_db_service():
    """Patch the vector_db_service to ensure search works properly"""
    global _original_search
    
    from services.vector_db_service import vector_db_service
    from services.embedding_service import embedding_service
    
    # Store the original search function if not already stored
    if _original_search is None:
        _original_search = vector_db_service.search
    
    # Define the patched search function
    def patched_search(query: str, collection_name: str = "case_law", top_k: int = 5) -> Dict[str, Any]:
        """Patched search function that ensures collections have documents and handles dimension mismatches"""
        # Get the collection
        collection = None
        if collection_name == "case_law":
            collection = embedding_service.case_law_collection
        elif collection_name == "statutes":
            collection = embedding_service.statutes_collection
        elif collection_name == "regulations":
            collection = embedding_service.regulations_collection
        else:
            # Use original function for unknown collections
            return _original_search(query, collection_name, top_k)
        
        # Ensure collection has documents
        ensure_collection_has_documents(collection, collection_name)
        
        # Use the original search function
        try:
            # Generate query embedding directly
            query_embedding = embedding_service.generate_embeddings([query], cache_key=f"query:{query}")[0]
            
            # Search directly with the collection
            try:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
            except Exception as e:
                if "dimension mismatch" in str(e).lower() or "dimension" in str(e).lower():
                    # Handle dimension mismatch by recreating collection
                    collection = recreate_collection(collection, collection_name)
                    if collection:
                        # Add documents to recreated collection
                        ensure_collection_has_documents(collection, collection_name)
                        
                        # Try again with correct dimensions
                        results = collection.query(
                            query_embeddings=[query_embedding],
                            n_results=top_k
                        )
                    else:
                        raise Exception(f"Failed to recreate collection {collection_name}")
                else:
                    raise e
            
            # Format results manually
            formatted_results = []
            if results and 'ids' in results and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i] if 'documents' in results and results['documents'][0] else "",
                        "metadata": results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'][0] else {}
                    }
                    formatted_results.append(result)
            
            return {
                "query": query,
                "results": formatted_results
            }
        except Exception as e:
            print(f"Error in patched search: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to original search
            return _original_search(query, collection_name, top_k)
    
    # Replace the search function
    vector_db_service.search = patched_search
    print("Vector DB search function has been patched for safer operation")

# Apply the patch when this module is imported
patch_vector_db_service()
