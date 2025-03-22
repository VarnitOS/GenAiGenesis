#!/usr/bin/env python3
"""
Script to fix S3 path issues in the vector store.
This script diagnoses and fixes issues with ChromaDB collection paths.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.embedding_service import embedding_service
from services.s3_vector_store import s3_vector_store

def print_divider(title):
    """Print a divider with a title for better readability"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_current_config():
    """Print current S3 and path configuration"""
    print_divider("CURRENT CONFIGURATION")
    
    print(f"S3 enabled: {s3_vector_store.s3_enabled}")
    print(f"S3 bucket: {s3_vector_store.s3_bucket}")
    print(f"S3 prefix: {s3_vector_store.s3_prefix}")
    print(f"Temp directory: {s3_vector_store.temp_dir}")
    print(f"Persistent directory: {s3_vector_store.persistent_dir}")
    
    # Check if directories exist
    if s3_vector_store.temp_dir:
        print(f"Temp directory exists: {os.path.exists(s3_vector_store.temp_dir)}")
    
    if s3_vector_store.persistent_dir:
        print(f"Persistent directory exists: {os.path.exists(s3_vector_store.persistent_dir)}")
        
        # Check contents of persistent directory
        if os.path.exists(s3_vector_store.persistent_dir):
            contents = os.listdir(s3_vector_store.persistent_dir)
            print(f"Contents of persistent directory: {contents}")
    
    # Check S3 collections
    if s3_vector_store.s3_enabled:
        collections = s3_vector_store.list_s3_collections()
        print(f"Collections in S3: {collections}")

def test_path_resolution():
    """Test path resolution for collections"""
    print_divider("TESTING PATH RESOLUTION")
    
    # Test collections
    test_collections = ["case_law", "statutes", "regulations", "dummy_test_collection"]
    
    for collection_name in test_collections:
        print(f"\nTesting paths for collection: {collection_name}")
        
        # Test getting collection S3 key
        s3_key = s3_vector_store._get_collection_s3_key(collection_name)
        print(f"S3 key: {s3_key}")
        
        # Test getting collection local path
        local_path = s3_vector_store._get_collection_path(collection_name)
        print(f"Local path: {local_path}")
        print(f"Path exists: {os.path.exists(local_path)}")
        
        # Test if collection exists in S3
        exists_in_s3 = s3_vector_store.collection_exists_in_s3(collection_name)
        print(f"Exists in S3: {exists_in_s3}")

def fix_persistent_directory():
    """Fix the persistent directory issue"""
    print_divider("FIXING PERSISTENT DIRECTORY")
    
    # Check if the persistent directory exists
    if not os.path.exists(s3_vector_store.persistent_dir):
        print(f"Creating persistent directory: {s3_vector_store.persistent_dir}")
        Path(s3_vector_store.persistent_dir).mkdir(parents=True, exist_ok=True)
    
    # Check if ChromaDB collections directory exists
    chroma_dir = os.path.join(s3_vector_store.persistent_dir, "chroma")
    if not os.path.exists(chroma_dir):
        print(f"Creating ChromaDB directory: {chroma_dir}")
        Path(chroma_dir).mkdir(parents=True, exist_ok=True)
    
    # Create collection directories if needed
    for collection_name in ["case_law", "statutes", "regulations"]:
        collection_path = os.path.join(s3_vector_store.persistent_dir, collection_name)
        if not os.path.exists(collection_path):
            print(f"Creating collection directory: {collection_path}")
            Path(collection_path).mkdir(parents=True, exist_ok=True)
    
    print("Persistent directory structure fixed")

def patch_s3_vector_store():
    """Patch the S3 vector store to fix path issues"""
    print_divider("PATCHING S3 VECTOR STORE")
    
    # Original _get_collection_path method
    original_get_path = s3_vector_store._get_collection_path
    
    # Patched method to ensure directory exists
    def patched_get_collection_path(collection_name):
        path = original_get_path(collection_name)
        os.makedirs(path, exist_ok=True)
        return path
    
    # Apply patch
    print("Patching _get_collection_path method")
    s3_vector_store._get_collection_path = patched_get_collection_path
    
    # Test patched method
    test_collection = "test_patch"
    path = s3_vector_store._get_collection_path(test_collection)
    print(f"Patched path for {test_collection}: {path}")
    print(f"Path exists: {os.path.exists(path)}")
    
    print("S3 vector store patched")

def test_upload_dummy_collection():
    """Test uploading a dummy collection to S3"""
    print_divider("TESTING DUMMY COLLECTION UPLOAD")
    
    # Create a dummy collection
    collection_name = "fix_s3_test_collection"
    print(f"Creating collection: {collection_name}")
    
    try:
        # Delete if exists
        try:
            embedding_service.client.delete_collection(collection_name)
        except:
            pass
        
        # Create collection
        collection = embedding_service.client.create_collection(name=collection_name)
        
        # Add a dummy document
        collection.add(
            documents=["This is a test document for S3 path fixing"],
            ids=["fix_test_001"],
            metadatas=[{"test": True}]
        )
        
        print("Added test document to collection")
        
        # Verify document was added
        data = collection.get()
        print(f"Collection contains {len(data['ids'])} document(s)")
        
        # Create directory structure
        collection_path = s3_vector_store._get_collection_path(collection_name)
        print(f"Collection path: {collection_path}")
        
        # Create a dummy file in the collection directory
        dummy_file = os.path.join(collection_path, "dummy.txt")
        with open(dummy_file, "w") as f:
            f.write("Test content")
        
        print(f"Created dummy file: {dummy_file}")
        
        # Try to upload to S3
        print("Uploading collection to S3...")
        success = s3_vector_store.upload_collection(collection_name)
        
        if success:
            print("Successfully uploaded collection to S3")
        else:
            print("Failed to upload collection to S3")
        
        # Clean up
        try:
            embedding_service.client.delete_collection(collection_name)
            print(f"Deleted collection: {collection_name}")
        except:
            pass
        
        return success
    except Exception as e:
        print(f"Error testing upload: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("=== S3 Path Fix Tool ===")
    
    # Print current configuration
    print_current_config()
    
    # Test path resolution
    test_path_resolution()
    
    # Fix persistent directory
    fix_persistent_directory()
    
    # Patch S3 vector store
    patch_s3_vector_store()
    
    # Test upload after fixing
    success = test_upload_dummy_collection()
    
    if success:
        print("\nS3 path issues fixed successfully!")
    else:
        print("\nFailed to fix S3 path issues. Additional investigation needed.")

if __name__ == "__main__":
    main() 