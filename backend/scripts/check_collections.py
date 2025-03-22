#!/usr/bin/env python3

"""
Check the contents of ChromaDB collections.
"""

import os
import sys
import logging
from pprint import pprint

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import relevant modules
from services.embedding_service import embedding_service

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_collection(collection_name):
    """Check the contents of a collection."""
    try:
        # Get the collection
        collection = embedding_service.get_collection(collection_name)
        
        # Get all items
        result = collection.get()
        
        # Print stats
        doc_count = len(result['ids']) if 'ids' in result else 0
        print(f"\nCollection: {collection_name}")
        print(f"Document count: {doc_count}")
        
        if doc_count > 0:
            # Print some sample metadata
            print("\nSample metadata:")
            for i in range(min(3, doc_count)):
                print(f"Document {i+1}:")
                pprint(result['metadatas'][i] if 'metadatas' in result else {})
                print(f"Text preview: {result['documents'][i][:100]}..." if 'documents' in result else "No text")
                print()
        
        return doc_count
    except Exception as e:
        logger.error(f"Error checking collection {collection_name}: {e}")
        return 0

def main():
    """Main function."""
    collections = ["case_law", "statutes", "regulations", "dummy_test_collection"]
    total_docs = 0
    
    print("Checking ChromaDB collections...")
    for collection_name in collections:
        doc_count = check_collection(collection_name)
        total_docs += doc_count
    
    print(f"\nTotal documents across all collections: {total_docs}")
    
    if total_docs == 0:
        print("\nThe collections are empty. You may need to populate them with documents first.")
        print("Try running:\npython scripts/test_pipeline.py --create-test-docs")

if __name__ == "__main__":
    main() 