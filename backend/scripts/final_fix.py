#!/usr/bin/env python3
"""
Final fix script that combines previous approaches to ensure vector search works properly.
This script will:
1. Reset the ChromaDB environment completely
2. Populate collections with sample documents
3. Verify collections contain documents
4. Add safeguards to ensure searches work properly
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
import time

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Sample documents from the populate script
from scripts.populate_vector_db import CASE_LAW_DOCUMENTS, STATUTE_DOCUMENTS, REGULATION_DOCUMENTS

def clean_environment():
    """Clean the entire environment to start fresh"""
    print("=== Cleaning Environment ===")
    
    # Remove temporary ChromaDB directory
    temp_dir = os.path.join(tempfile.gettempdir(), "chromadb_temp")
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"Removed ChromaDB temp directory: {temp_dir}")
        except Exception as e:
            print(f"Error removing temp directory: {e}")
    
    # Create fresh temp directory
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Created fresh temp directory: {temp_dir}")
    
    # Reset stats file
    stats_path = os.path.join(os.getcwd(), "data", "stats.json")
    if os.path.exists(stats_path):
        try:
            os.remove(stats_path)
            print(f"Removed stats file: {stats_path}")
        except Exception as e:
            print(f"Error removing stats file: {e}")
    
    # Create fresh stats directory
    os.makedirs(os.path.dirname(stats_path), exist_ok=True)
    print(f"Created fresh stats directory: {os.path.dirname(stats_path)}")

def initialize_embedding_service():
    """Initialize the embedding service with a fresh environment"""
    print("\n=== Initializing Embedding Service ===")
    
    # Import here after cleaning environment
    from services.embedding_service import embedding_service
    
    # Print S3 status
    from services.embedding_service import S3_ENABLED
    print(f"S3 enabled: {S3_ENABLED}")
    
    # Return the embedding service
    return embedding_service

def verify_collection_empty(embedding_service, collection_name):
    """Verify that a collection is empty"""
    try:
        collection = embedding_service.get_collection(collection_name)
        data = collection.get()
        return len(data.get('ids', [])) == 0
    except:
        return True

def populate_collection(embedding_service, collection_name, documents_data):
    """Populate a collection with documents"""
    print(f"\n=== Populating Collection: {collection_name} ===")
    
    # Get the collection
    collection = embedding_service.get_collection(collection_name)
    
    # Verify it's empty first
    if not verify_collection_empty(embedding_service, collection_name):
        print(f"Collection {collection_name} already has documents. Skipping population.")
        return
    
    # Extract document data
    documents = [doc["document"] for doc in documents_data]
    metadatas = [doc["metadata"] for doc in documents_data]
    ids = [doc["id"] for doc in documents_data]
    
    # Generate embeddings
    print(f"Generating embeddings for {len(documents)} documents...")
    embeddings = embedding_service.generate_embeddings(documents)
    print(f"Generated {len(embeddings)} embeddings")
    
    # Add documents to collection
    print(f"Adding documents to {collection_name}...")
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    # Verify documents were added
    data = collection.get()
    doc_count = len(data.get('ids', []))
    print(f"Collection now has {doc_count} documents")
    
    # Verify by printing sample document
    if doc_count > 0:
        print(f"Sample document ID: {data['ids'][0]}")
        print(f"Sample metadata: {data['metadatas'][0]}")
        sample_text = data['documents'][0][:200] + "..." if len(data['documents'][0]) > 200 else data['documents'][0]
        print(f"Sample text: {sample_text}")
    
    # Add direct embedding check
    if 'embeddings' in data and data['embeddings'] is not None:
        print(f"Embeddings are present in collection")
    else:
        print(f"Warning: Embeddings are not stored in collection")

def update_stats(collection_map):
    """Update stats file based on actual collection counts"""
    print("\n=== Updating Stats File ===")
    
    from services.vector_db_service import vector_db_service
    
    # Create stats object
    stats = {}
    for collection_name, collection in collection_map.items():
        try:
            doc_count = len(collection.get().get('ids', []))
            stats[collection_name] = {
                "documents": doc_count,
                "embeddings": doc_count
            }
            print(f"{collection_name}: {doc_count} documents")
        except Exception as e:
            print(f"Error getting count for {collection_name}: {e}")
            stats[collection_name] = {"documents": 0, "embeddings": 0}
    
    # Update vector_db_service stats
    vector_db_service.stats = stats
    
    # Save stats
    vector_db_service._save_stats()
    print("Stats saved to file")
    
    # Verify stats file was saved
    stats_path = os.path.join(os.getcwd(), "data", "stats.json")
    if os.path.exists(stats_path):
        with open(stats_path, 'r') as f:
            saved_stats = json.load(f)
        print(f"Saved stats: {json.dumps(saved_stats)}")
    else:
        print("Warning: Stats file was not created")

def test_search(embedding_service, collection_map):
    """Test search functionality for each collection"""
    print("\n=== Testing Search Functionality ===")
    
    test_queries = {
        "case_law": "employment discrimination lawsuit",
        "statutes": "equal pay legislation",
        "regulations": "workplace harassment"
    }
    
    for collection_name, query in test_queries.items():
        print(f"\nTesting search on {collection_name} for '{query}':")
        
        collection = collection_map.get(collection_name)
        if not collection:
            print(f"Collection {collection_name} not found. Skipping.")
            continue
        
        # First check if collection has documents
        data = collection.get()
        doc_count = len(data.get('ids', []))
        if doc_count == 0:
            print(f"Collection {collection_name} is empty. Skipping search.")
            continue
        
        try:
            # Generate query embedding
            query_embedding = embedding_service.generate_embeddings([query])[0]
            
            # Search directly
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=2
            )
            
            # Print results
            result_ids = results.get('ids', [[]])[0]
            result_count = len(result_ids)
            print(f"Found {result_count} results")
            
            if result_count > 0:
                print(f"Result IDs: {result_ids}")
                for i, doc_id in enumerate(result_ids):
                    print(f"\nResult {i+1}:")
                    print(f"ID: {doc_id}")
                    if 'metadatas' in results and results['metadatas'][0]:
                        print(f"Metadata: {results['metadatas'][0][i]}")
                    if 'documents' in results and results['documents'][0]:
                        doc_text = results['documents'][0][i][:150] + "..." if len(results['documents'][0][i]) > 150 else results['documents'][0][i]
                        print(f"Text: {doc_text}")
            else:
                print("No results found")
        except Exception as e:
            print(f"Error testing search: {e}")
            import traceback
            traceback.print_exc()

def create_override_patch():
    """Create an override patch for the search function to ensure it always checks for documents"""
    print("\n=== Creating Search Override Patch ===")
    
    # Path to override file
    override_path = os.path.join(os.getcwd(), "services", "search_override.py")
    
    # Create the override file
    with open(override_path, 'w') as f:
        f.write("""
# Override for search functionality to ensure it always checks for documents
import os
import json
from typing import Dict, Any
from pathlib import Path

# Store original search function
_original_search = None

def patch_vector_db_service():
    \"\"\"Patch the vector_db_service to ensure search works properly\"\"\"
    global _original_search
    
    from services.vector_db_service import vector_db_service
    from services.embedding_service import embedding_service
    
    # Store the original search function if not already stored
    if _original_search is None:
        _original_search = vector_db_service.search
    
    # Define the patched search function
    def patched_search(query: str, collection_name: str = "case_law", top_k: int = 5) -> Dict[str, Any]:
        \"\"\"Patched search function that ensures collections have documents\"\"\"
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
        
        # Check if collection has documents
        try:
            data = collection.get()
            if len(data.get('ids', [])) == 0:
                print(f"Warning: Collection {collection_name} is empty, no search results possible")
                return {"query": query, "results": []}
        except Exception as e:
            print(f"Error checking collection {collection_name}: {e}")
        
        # Use the original search function
        return _original_search(query, collection_name, top_k)
    
    # Replace the search function
    vector_db_service.search = patched_search
    print("Vector DB search function has been patched for safer operation")

# Apply the patch when this module is imported
patch_vector_db_service()
""")
    
    print(f"Created search override at {override_path}")
    
    # Create an __init__.py file in the services directory if it doesn't exist
    init_path = os.path.join(os.getcwd(), "services", "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write("# Services package\n")
        print(f"Created __init__.py at {init_path}")

def update_run_app():
    """Update the run_app.py script to import our override patch"""
    print("\n=== Updating Run App Script ===")
    
    # Path to run_app.py
    run_app_path = os.path.join(os.getcwd(), "scripts", "run_app.py")
    
    # Read the run_app.py file
    with open(run_app_path, 'r') as f:
        lines = f.readlines()
    
    # Find where to insert our import
    insert_line = None
    for i, line in enumerate(lines):
        if "sys.path.append" in line and i < len(lines) - 1:
            insert_line = i + 1
            break
    
    # Insert our import
    if insert_line is not None:
        import_line = "    # Import search override patch for safer operation\n    sys.path.insert(0, base_dir)\n    from services import search_override\n\n"
        lines.insert(insert_line, import_line)
        
        # Write the updated file
        with open(run_app_path, 'w') as f:
            f.writelines(lines)
        
        print(f"Updated {run_app_path} to import search override patch")
    else:
        print(f"Could not find insertion point in {run_app_path}")

def main():
    """Main function to fix the vector search"""
    print("=== FINAL FIX: Vector Search ===")
    
    # Step 1: Clean the environment
    clean_environment()
    
    # Step 2: Initialize the embedding service
    embedding_service = initialize_embedding_service()
    
    # Step 3: Populate collections
    populate_collection(embedding_service, "case_law", CASE_LAW_DOCUMENTS)
    populate_collection(embedding_service, "statutes", STATUTE_DOCUMENTS)
    populate_collection(embedding_service, "regulations", REGULATION_DOCUMENTS)
    
    # Step 4: Save collections to S3
    collection_map = {
        "case_law": embedding_service.case_law_collection,
        "statutes": embedding_service.statutes_collection,
        "regulations": embedding_service.regulations_collection
    }
    
    # Step 5: Update stats based on actual collection contents
    update_stats(collection_map)
    
    # Step 6: Test search functionality
    test_search(embedding_service, collection_map)
    
    # Step 7: Create search override patch
    create_override_patch()
    
    # Step 8: Update run_app.py to use our patch
    update_run_app()
    
    print("\n=== Fix Complete ===")
    print("The vector database has been reset and populated with sample documents.")
    print("Please restart the application to apply all changes:")
    print("  pkill -f app.py && python3 scripts/run_app.py")

if __name__ == "__main__":
    main() 