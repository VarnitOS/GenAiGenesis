#!/usr/bin/env python3
"""
Script to completely reset and rebuild ChromaDB collections with consistent embedding dimensions.
This addresses dimension mismatch issues by ensuring all collections use the same embedding model.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.embedding_service import embedding_service
from services.s3_vector_store import s3_vector_store
from scripts.populate_vector_db import CASE_LAW_DOCUMENTS, STATUTE_DOCUMENTS, REGULATION_DOCUMENTS

def clean_environment():
    """Clean all collection data to start fresh"""
    print("=== Cleaning Environment ===")
    
    # Delete all collections
    try:
        for collection_name in ["case_law", "statutes", "regulations"]:
            try:
                embedding_service.client.delete_collection(collection_name)
                print(f"Deleted collection {collection_name}")
            except Exception as e:
                print(f"No collection to delete: {collection_name}")
    except Exception as e:
        print(f"Error deleting collections: {e}")
    
    # Clean ChromaDB directory
    chroma_dir = os.path.join(s3_vector_store.persistent_dir, "chroma")
    if os.path.exists(chroma_dir):
        try:
            shutil.rmtree(chroma_dir)
            print(f"Removed ChromaDB directory: {chroma_dir}")
            os.makedirs(chroma_dir, exist_ok=True)
            print(f"Created fresh ChromaDB directory")
        except Exception as e:
            print(f"Error cleaning ChromaDB directory: {e}")
    
    # Clean collection directories
    for collection_name in ["case_law", "statutes", "regulations"]:
        collection_path = os.path.join(s3_vector_store.persistent_dir, collection_name)
        if os.path.exists(collection_path):
            try:
                shutil.rmtree(collection_path)
                print(f"Removed collection directory: {collection_path}")
                os.makedirs(collection_path, exist_ok=True)
                print(f"Created fresh collection directory")
            except Exception as e:
                print(f"Error cleaning collection directory: {e}")
    
    # Reset stats file if it exists
    stats_path = os.path.join(os.getcwd(), "data", "stats.json")
    if os.path.exists(stats_path):
        try:
            os.remove(stats_path)
            print(f"Removed stats file: {stats_path}")
        except Exception as e:
            print(f"Error removing stats file: {e}")
    
    # Create fresh stats
    stats = {
        "case_law": {"documents": 0, "embeddings": 0},
        "statutes": {"documents": 0, "embeddings": 0},
        "regulations": {"documents": 0, "embeddings": 0}
    }
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(stats_path), exist_ok=True)
        
        # Write new stats file
        with open(stats_path, 'w') as f:
            json.dump(stats, f)
        
        print("Created new stats file")
        
        # Reset the in-memory stats in vector_db_service
        from services.vector_db_service import vector_db_service
        vector_db_service.stats = stats
    except Exception as e:
        print(f"Error resetting stats file: {e}")

def create_collections():
    """Create fresh collections with consistent settings"""
    print("\n=== Creating Fresh Collections ===")
    
    collections = {}
    
    try:
        # Create case_law collection
        print("Creating case_law collection...")
        collections["case_law"] = embedding_service.client.create_collection(name="case_law")
        embedding_service.case_law_collection = collections["case_law"]
        
        # Create statutes collection
        print("Creating statutes collection...")
        collections["statutes"] = embedding_service.client.create_collection(name="statutes")
        embedding_service.statutes_collection = collections["statutes"]
        
        # Create regulations collection
        print("Creating regulations collection...")
        collections["regulations"] = embedding_service.client.create_collection(name="regulations")
        embedding_service.regulations_collection = collections["regulations"]
        
        print("All collections created successfully")
        return collections
    except Exception as e:
        print(f"Error creating collections: {e}")
        return None

def populate_collections(collections):
    """Populate collections with sample documents"""
    print("\n=== Populating Collections ===")
    
    if not collections:
        print("No collections to populate")
        return False
    
    # Get embedding function for consistency
    def embed_func(texts):
        return embedding_service.generate_embeddings(texts)
    
    try:
        # Populate case_law collection
        print("Populating case_law collection...")
        documents = [doc["document"] for doc in CASE_LAW_DOCUMENTS]
        metadatas = [doc["metadata"] for doc in CASE_LAW_DOCUMENTS]
        ids = [doc["id"] for doc in CASE_LAW_DOCUMENTS]
        
        # Generate embeddings explicitly for consistency
        embeddings = embed_func(documents)
        print(f"Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}")
        
        # Add documents with embeddings
        collections["case_law"].add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to case_law collection")
        
        # Populate statutes collection
        print("\nPopulating statutes collection...")
        documents = [doc["document"] for doc in STATUTE_DOCUMENTS]
        metadatas = [doc["metadata"] for doc in STATUTE_DOCUMENTS]
        ids = [doc["id"] for doc in STATUTE_DOCUMENTS]
        
        # Generate embeddings explicitly for consistency
        embeddings = embed_func(documents)
        print(f"Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}")
        
        # Add documents with embeddings
        collections["statutes"].add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to statutes collection")
        
        # Populate regulations collection
        print("\nPopulating regulations collection...")
        documents = [doc["document"] for doc in REGULATION_DOCUMENTS]
        metadatas = [doc["metadata"] for doc in REGULATION_DOCUMENTS]
        ids = [doc["id"] for doc in REGULATION_DOCUMENTS]
        
        # Generate embeddings explicitly for consistency
        embeddings = embed_func(documents)
        print(f"Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}")
        
        # Add documents with embeddings
        collections["regulations"].add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to regulations collection")
        
        return True
    except Exception as e:
        print(f"Error populating collections: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_stats():
    """Update stats to match actual document counts"""
    print("\n=== Updating Stats ===")
    
    try:
        # Get actual document counts
        case_law_count = len(embedding_service.case_law_collection.get()["ids"])
        statutes_count = len(embedding_service.statutes_collection.get()["ids"])
        regulations_count = len(embedding_service.regulations_collection.get()["ids"])
        
        # Update stats
        from services.vector_db_service import vector_db_service
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
            print(f"Stats file content verified")
        else:
            print("Warning: Stats file does not exist after save")
    except Exception as e:
        print(f"Error updating statistics: {e}")

def sync_with_s3():
    """Sync all collections with S3"""
    print("\n=== Syncing with S3 ===")
    
    try:
        for collection_name in ["case_law", "statutes", "regulations"]:
            print(f"Syncing {collection_name} with S3...")
            success = s3_vector_store.upload_collection(collection_name)
            if success:
                print(f"Successfully synced {collection_name}")
            else:
                print(f"Failed to sync {collection_name}")
    except Exception as e:
        print(f"Error syncing with S3: {e}")

def test_search():
    """Test search functionality with the rebuilt collections"""
    print("\n=== Testing Search Functionality ===")
    
    queries = {
        "case_law": "employment discrimination lawsuit",
        "statutes": "equal pay legislation",
        "regulations": "workplace harassment regulations"
    }
    
    for collection_name, query in queries.items():
        print(f"\nTesting search in {collection_name} for query: '{query}'")
        try:
            # Generate query embedding
            query_embedding = embedding_service.generate_embeddings([query])[0]
            print(f"Generated query embedding with dimension {len(query_embedding)}")
            
            # Get collection
            collection = None
            if collection_name == "case_law":
                collection = embedding_service.case_law_collection
            elif collection_name == "statutes":
                collection = embedding_service.statutes_collection
            elif collection_name == "regulations":
                collection = embedding_service.regulations_collection
            
            # Search directly
            if collection:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=2
                )
                
                print(f"Found {len(results['ids'][0])} results")
                for i in range(len(results['ids'][0])):
                    print(f"  Result {i+1}: {results['ids'][0][i]}")
            else:
                print(f"Collection {collection_name} not found")
        except Exception as e:
            print(f"Error testing search: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    print("=== ChromaDB Collection Reset Tool ===")
    
    # Step 1: Clean environment
    clean_environment()
    
    # Step 2: Create fresh collections
    collections = create_collections()
    
    # Step 3: Populate collections
    success = populate_collections(collections)
    
    if success:
        # Step 4: Update stats
        update_stats()
        
        # Step 5: Sync with S3
        sync_with_s3()
        
        # Step 6: Test search
        test_search()
        
        print("\nDone! Collections have been reset and rebuilt successfully.")
        print("You should now restart the application for changes to take effect:")
        print("  pkill -f app.py && python3 scripts/run_app.py")
    else:
        print("\nError: Failed to populate collections. Further debugging required.")

if __name__ == "__main__":
    main() 