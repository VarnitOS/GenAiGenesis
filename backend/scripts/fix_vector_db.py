#!/usr/bin/env python3
"""
Script to fix the vector database by re-populating collections and ensuring
stats match the actual document count.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.embedding_service import embedding_service
from services.vector_db_service import vector_db_service
from scripts.populate_vector_db import CASE_LAW_DOCUMENTS, STATUTE_DOCUMENTS, REGULATION_DOCUMENTS

def reset_collections():
    """Reset all collections to make sure we start fresh"""
    print("Resetting collections...")
    
    # Reset the collections
    try:
        # Delete existing collections
        for collection_name in ["case_law", "statutes", "regulations"]:
            try:
                embedding_service.client.delete_collection(collection_name)
                print(f"Collection {collection_name} deleted")
            except Exception as e:
                print(f"Error deleting collection {collection_name}: {e}")
        
        # Recreate the collections
        embedding_service.case_law_collection = embedding_service.client.create_collection(name="case_law")
        embedding_service.statutes_collection = embedding_service.client.create_collection(name="statutes")
        embedding_service.regulations_collection = embedding_service.client.create_collection(name="regulations")
        print("Collections recreated")
    except Exception as e:
        print(f"Error resetting collections: {e}")

def reset_stats_file():
    """Reset the statistics file completely"""
    print("Resetting statistics file...")
    
    stats_path = os.path.join(os.getcwd(), "data", "stats.json")
    
    # Create fresh stats
    stats = {
        "case_law": {"documents": 0, "embeddings": 0},
        "statutes": {"documents": 0, "embeddings": 0},
        "regulations": {"documents": 0, "embeddings": 0}
    }
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(stats_path), exist_ok=True)
        
        # Delete existing file if it exists
        if os.path.exists(stats_path):
            os.remove(stats_path)
            print("Deleted existing stats file")
        
        # Write new stats file
        with open(stats_path, 'w') as f:
            json.dump(stats, f)
        
        print("Created new stats file")
        
        # Reset the in-memory stats
        vector_db_service.stats = stats
    except Exception as e:
        print(f"Error resetting stats file: {e}")

def repopulate_collections():
    """Repopulate all collections with sample documents"""
    print("\nRepopulating collections...")
    
    # Case Law
    try:
        case_law_documents = [doc["document"] for doc in CASE_LAW_DOCUMENTS]
        case_law_metadatas = [doc["metadata"] for doc in CASE_LAW_DOCUMENTS]
        case_law_ids = [doc["id"] for doc in CASE_LAW_DOCUMENTS]
        
        vector_db_service.import_case_law(
            texts=case_law_documents,
            metadatas=case_law_metadatas,
            ids=case_law_ids
        )
        print(f"Added {len(case_law_documents)} case law documents")
    except Exception as e:
        print(f"Error adding case law documents: {e}")
    
    # Statutes
    try:
        statute_documents = [doc["document"] for doc in STATUTE_DOCUMENTS]
        statute_metadatas = [doc["metadata"] for doc in STATUTE_DOCUMENTS]
        statute_ids = [doc["id"] for doc in STATUTE_DOCUMENTS]
        
        vector_db_service.import_statutes(
            texts=statute_documents,
            metadatas=statute_metadatas,
            ids=statute_ids
        )
        print(f"Added {len(statute_documents)} statute documents")
    except Exception as e:
        print(f"Error adding statute documents: {e}")
    
    # Regulations
    try:
        regulation_documents = [doc["document"] for doc in REGULATION_DOCUMENTS]
        regulation_metadatas = [doc["metadata"] for doc in REGULATION_DOCUMENTS]
        regulation_ids = [doc["id"] for doc in REGULATION_DOCUMENTS]
        
        vector_db_service.import_regulations(
            texts=regulation_documents,
            metadatas=regulation_metadatas,
            ids=regulation_ids
        )
        print(f"Added {len(regulation_documents)} regulation documents")
    except Exception as e:
        print(f"Error adding regulation documents: {e}")

def fix_stats():
    """Fix the statistics file to match the actual document count"""
    print("\nFixing statistics...")
    
    try:
        # Get actual document counts
        case_law_count = len(embedding_service.case_law_collection.get()["ids"])
        statutes_count = len(embedding_service.statutes_collection.get()["ids"])
        regulations_count = len(embedding_service.regulations_collection.get()["ids"])
        
        # Update stats
        vector_db_service.stats = {
            "case_law": {"documents": case_law_count, "embeddings": case_law_count},
            "statutes": {"documents": statutes_count, "embeddings": statutes_count},
            "regulations": {"documents": regulations_count, "embeddings": regulations_count}
        }
        
        # Save updated stats
        vector_db_service._save_stats()
        print(f"Statistics updated: case_law={case_law_count}, statutes={statutes_count}, regulations={regulations_count}")
        
        # Verify stats file was written
        stats_path = os.path.join(os.getcwd(), "data", "stats.json")
        if os.path.exists(stats_path):
            with open(stats_path, 'r') as f:
                stored_stats = json.load(f)
            print(f"Stats file content: {json.dumps(stored_stats)}")
        else:
            print("Warning: Stats file does not exist after save")
    except Exception as e:
        print(f"Error fixing statistics: {e}")

def sync_with_s3():
    """Sync all collections with S3"""
    print("\nSyncing collections with S3...")
    
    try:
        embedding_service.sync_all_with_s3()
        print("All collections synced with S3")
    except Exception as e:
        print(f"Error syncing with S3: {e}")

def verify_collections():
    """Verify that collections have documents"""
    print("\nVerifying collections...")
    
    for collection_name in ["case_law", "statutes", "regulations"]:
        try:
            collection = embedding_service.get_collection(collection_name)
            data = collection.get()
            print(f"{collection_name}: {len(data['ids'])} documents")
            
            if data['ids']:
                print(f"  Sample IDs: {data['ids'][:3]}")
        except Exception as e:
            print(f"Error verifying {collection_name}: {e}")

def test_search():
    """Test search functionality"""
    print("\nTesting search functionality...")
    
    queries = {
        "case_law": "employment discrimination lawsuit",
        "statutes": "equal pay legislation",
        "regulations": "workplace harassment regulations"
    }
    
    for collection_name, query in queries.items():
        print(f"\nSearching {collection_name} for '{query}'...")
        try:
            results = vector_db_service.search(query, collection_name, top_k=2)
            print(f"Results: {len(results['results'])} documents found")
            
            if results['results']:
                for i, result in enumerate(results['results']):
                    print(f"\nResult {i+1}:")
                    print(f"ID: {result['id']}")
                    print(f"Metadata: {result['metadata']}")
                    doc_excerpt = result['document'][:100] + "..." if len(result['document']) > 100 else result['document']
                    print(f"Document excerpt: {doc_excerpt}")
        except Exception as e:
            print(f"Error searching {collection_name}: {e}")

def clean_temp_directory():
    """Clean temporary ChromaDB directory"""
    print("\nCleaning temporary ChromaDB directory...")
    
    import tempfile
    temp_db_path = os.path.join(tempfile.gettempdir(), "chromadb_temp")
    
    try:
        if os.path.exists(temp_db_path):
            shutil.rmtree(temp_db_path)
            print(f"Removed {temp_db_path}")
        
        # Recreate the directory
        os.makedirs(temp_db_path, exist_ok=True)
        print(f"Recreated {temp_db_path}")
    except Exception as e:
        print(f"Error cleaning temp directory: {e}")

def main():
    """Main function"""
    print("=== Fixing Vector Database ===")
    
    # Step 0: Clean temp directory
    clean_temp_directory()
    
    # Step 1: Reset stats file completely
    reset_stats_file()
    
    # Step 2: Reset collections
    reset_collections()
    
    # Step 3: Repopulate collections
    repopulate_collections()
    
    # Step 4: Fix statistics
    fix_stats()
    
    # Step 5: Sync with S3
    sync_with_s3()
    
    # Step 6: Verify collections
    verify_collections()
    
    # Step 7: Test search functionality
    test_search()
    
    print("\nDone! The vector database has been fixed.")
    print("You should now restart the application for changes to take effect:")
    print("  pkill -f app.py && python3 scripts/run_app.py")

if __name__ == "__main__":
    main() 