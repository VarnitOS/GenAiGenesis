#!/usr/bin/env python3
"""
Script to test the search override patch directly.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Make sure we can import our override
from services import search_override

# Import services
from services.embedding_service import embedding_service
from services.vector_db_service import vector_db_service

def rebuild_collections():
    """Rebuild the collections with sample documents directly"""
    print("=== Rebuilding Collections ===")
    
    # Sample documents
    from scripts.populate_vector_db import CASE_LAW_DOCUMENTS, STATUTE_DOCUMENTS, REGULATION_DOCUMENTS
    
    # Rebuild case_law collection
    print("\nRebuilding case_law collection...")
    try:
        # Get collection
        collection = embedding_service.case_law_collection
        
        # Check if empty
        data = collection.get()
        if len(data.get('ids', [])) == 0:
            # Extract document data
            documents = [doc["document"] for doc in CASE_LAW_DOCUMENTS]
            metadatas = [doc["metadata"] for doc in CASE_LAW_DOCUMENTS]
            ids = [doc["id"] for doc in CASE_LAW_DOCUMENTS]
            
            # Generate embeddings
            embeddings = embedding_service.generate_embeddings(documents)
            
            # Add documents
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(documents)} documents to case_law collection")
        else:
            print(f"Collection already has {len(data['ids'])} documents")
    except Exception as e:
        print(f"Error rebuilding case_law collection: {e}")
    
    # Rebuild statutes collection
    print("\nRebuilding statutes collection...")
    try:
        # Get collection
        collection = embedding_service.statutes_collection
        
        # Check if empty
        data = collection.get()
        if len(data.get('ids', [])) == 0:
            # Extract document data
            documents = [doc["document"] for doc in STATUTE_DOCUMENTS]
            metadatas = [doc["metadata"] for doc in STATUTE_DOCUMENTS]
            ids = [doc["id"] for doc in STATUTE_DOCUMENTS]
            
            # Generate embeddings
            embeddings = embedding_service.generate_embeddings(documents)
            
            # Add documents
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(documents)} documents to statutes collection")
        else:
            print(f"Collection already has {len(data['ids'])} documents")
    except Exception as e:
        print(f"Error rebuilding statutes collection: {e}")
    
    # Rebuild regulations collection
    print("\nRebuilding regulations collection...")
    try:
        # Get collection
        collection = embedding_service.regulations_collection
        
        # Check if empty
        data = collection.get()
        if len(data.get('ids', [])) == 0:
            # Extract document data
            documents = [doc["document"] for doc in REGULATION_DOCUMENTS]
            metadatas = [doc["metadata"] for doc in REGULATION_DOCUMENTS]
            ids = [doc["id"] for doc in REGULATION_DOCUMENTS]
            
            # Generate embeddings
            embeddings = embedding_service.generate_embeddings(documents)
            
            # Add documents
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(documents)} documents to regulations collection")
        else:
            print(f"Collection already has {len(data['ids'])} documents")
    except Exception as e:
        print(f"Error rebuilding regulations collection: {e}")

def test_search():
    """Test the vector database search functionality"""
    print("\n=== Testing Search Functionality ===")
    
    # Test case_law search
    print("\nTesting case_law search...")
    case_law_results = vector_db_service.search(
        query="employment discrimination",
        collection_name="case_law",
        top_k=2
    )
    print(f"Case law results: {json.dumps(case_law_results)}")
    
    # Test statutes search
    print("\nTesting statutes search...")
    statutes_results = vector_db_service.search(
        query="equal pay",
        collection_name="statutes",
        top_k=2
    )
    print(f"Statutes results: {json.dumps(statutes_results)}")
    
    # Test regulations search
    print("\nTesting regulations search...")
    regulations_results = vector_db_service.search(
        query="sexual harassment",
        collection_name="regulations",
        top_k=2
    )
    print(f"Regulations results: {json.dumps(regulations_results)}")

def verify_collections():
    """Verify that collections have documents"""
    print("\n=== Verifying Collections ===")
    
    # Check case_law collection
    print("\nChecking case_law collection:")
    try:
        data = embedding_service.case_law_collection.get()
        print(f"Document count: {len(data.get('ids', []))}")
        if data.get('ids'):
            print(f"IDs: {data['ids']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check statutes collection
    print("\nChecking statutes collection:")
    try:
        data = embedding_service.statutes_collection.get()
        print(f"Document count: {len(data.get('ids', []))}")
        if data.get('ids'):
            print(f"IDs: {data['ids']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check regulations collection
    print("\nChecking regulations collection:")
    try:
        data = embedding_service.regulations_collection.get()
        print(f"Document count: {len(data.get('ids', []))}")
        if data.get('ids'):
            print(f"IDs: {data['ids']}")
    except Exception as e:
        print(f"Error: {e}")

def try_direct_search():
    """Try searching directly with the collection query method"""
    print("\n=== Trying Direct Search ===")
    
    try:
        # Generate query embedding
        query = "employment discrimination"
        print(f"Generating embedding for query: '{query}'")
        query_embedding = embedding_service.generate_embeddings([query])[0]
        
        # Get collection
        collection = embedding_service.case_law_collection
        
        # Query collection directly
        print("Querying collection directly...")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=2
        )
        
        print(f"Direct search results: {json.dumps(results)}")
    except Exception as e:
        print(f"Error during direct search: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("=== Testing Search Override ===")
    
    # Verify if search override is active
    print(f"Original search function: {search_override._original_search}")
    print(f"Current search function: {vector_db_service.search}")
    
    # Verify collections
    verify_collections()
    
    # Rebuild collections
    rebuild_collections()
    
    # Verify collections again
    verify_collections()
    
    # Try direct search
    try_direct_search()
    
    # Test search
    test_search()
    
    print("\nDone!")

if __name__ == "__main__":
    main() 