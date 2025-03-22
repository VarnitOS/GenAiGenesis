#!/usr/bin/env python3
"""
Script to debug search functionality in the vector database.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.embedding_service import embedding_service

def inspect_collection(collection_name):
    """Inspect a collection in the vector database"""
    print(f"\n=== Inspecting collection: {collection_name} ===")
    
    collection = embedding_service.get_collection(collection_name)
    
    try:
        data = collection.get()
        print(f"Collection size: {len(data['ids'])} documents")
        
        if data['ids']:
            print(f"Sample document IDs: {data['ids'][:3]}")
            
            # Print a sample document
            if data['documents'] and len(data['documents']) > 0:
                print("\nSample document content:")
                print("-" * 50)
                print(data['documents'][0][:500] + "..." if len(data['documents'][0]) > 500 else data['documents'][0])
                print("-" * 50)
            
            # Print sample metadata
            if data['metadatas'] and len(data['metadatas']) > 0:
                print("\nSample metadata:")
                print(data['metadatas'][0])
        else:
            print("Collection is empty")
    except Exception as e:
        print(f"Error inspecting collection: {e}")

def test_search(query, collection_name, top_k=3):
    """Test search functionality"""
    print(f"\n=== Testing search on {collection_name} ===")
    print(f"Query: '{query}'")
    print(f"Top K: {top_k}")
    
    try:
        # Generate query embedding for debugging
        query_embedding = embedding_service.generate_embeddings(
            [query],
            cache_key=f"query:{query}"
        )[0]
        print(f"Query embedding generated: {len(query_embedding)} dimensions")
        
        # Get collection
        collection = embedding_service.get_collection(collection_name)
        
        # Perform search directly
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        print("\nRaw search results:")
        print(results)
        
        # Test the service function
        formatted_results = embedding_service.similarity_search(
            query=query,
            collection_name=collection_name,
            top_k=top_k
        )
        
        print("\nFormatted search results:")
        for i, result in enumerate(formatted_results):
            print(f"\nResult {i+1}:")
            print(f"ID: {result['id']}")
            print(f"Metadata: {result['metadata']}")
            doc_excerpt = result['document'][:200] + "..." if len(result['document']) > 200 else result['document']
            print(f"Document excerpt: {doc_excerpt}")
    except Exception as e:
        print(f"Error during search: {e}")

def main():
    """Main debug function"""
    print("=== Vector Database Search Debug ===")
    
    # Inspect all collections
    for collection_name in ["case_law", "statutes", "regulations"]:
        inspect_collection(collection_name)
    
    # Test search on each collection
    test_search("employment discrimination", "case_law")
    test_search("equal pay regulations", "regulations")
    test_search("housing discrimination", "statutes")

if __name__ == "__main__":
    main() 