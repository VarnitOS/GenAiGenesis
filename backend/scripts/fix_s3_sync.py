#!/usr/bin/env python3
"""
Script to fix S3 synchronization of vector database collections.
This script focuses on ensuring that collections are properly uploaded to S3
and testing different S3 paths to find a working configuration.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.embedding_service import embedding_service

def test_s3_path():
    """Test S3 path configuration to find a working path"""
    print("\n=== Testing S3 Path Configuration ===")
    
    # Import S3 service
    from services.s3_vector_store import s3_vector_store
    
    # Print current configuration
    print(f"Current S3 bucket: {s3_vector_store.s3_bucket}")
    print(f"Current S3 prefix: {s3_vector_store.s3_prefix}")
    
    # Try different prefixes
    prefixes = [
        "vector_db/",
        "",
        "chroma/",
        "collections/"
    ]
    
    for prefix in prefixes:
        print(f"\nTrying prefix: '{prefix}'")
        
        # Update prefix
        old_prefix = s3_vector_store.s3_prefix
        s3_vector_store.s3_prefix = prefix
        
        # List collections with this prefix
        try:
            collections = s3_vector_store.list_s3_collections()
            print(f"Collections found with prefix '{prefix}': {collections}")
        except Exception as e:
            print(f"Error listing collections with prefix '{prefix}': {e}")
        
        # Restore original prefix
        s3_vector_store.s3_prefix = old_prefix

def setup_test_collection():
    """Set up a test collection and upload it to S3"""
    print("\n=== Setting Up Test Collection ===")
    
    # Import services
    from services.s3_vector_store import s3_vector_store
    
    # Create and populate test collection
    test_collection_name = "test_s3_sync"
    try:
        # Create collection
        print(f"Creating test collection '{test_collection_name}'...")
        try:
            embedding_service.client.delete_collection(test_collection_name)
            print(f"Deleted existing collection")
        except:
            pass
        
        test_collection = embedding_service.client.create_collection(name=test_collection_name)
        
        # Add a test document
        test_collection.add(
            documents=["This is a test document to verify S3 synchronization"],
            ids=["test_doc_001"],
            metadatas=[{"test": True, "purpose": "S3 sync verification"}]
        )
        
        print("Added test document to collection")
        
        # Get collection data to verify
        data = test_collection.get()
        print(f"Collection size: {len(data['ids'])} documents")
        print(f"Document IDs: {data['ids']}")
        
        # Try to upload to S3
        print("Uploading collection to S3...")
        
        # Direct upload attempt
        s3_vector_store._get_collection_path = lambda x: os.path.join(
            s3_vector_store.persistent_dir, x)
        
        success = s3_vector_store.upload_collection(test_collection_name)
        
        if success:
            print("Successfully uploaded collection to S3")
        else:
            print("Failed to upload collection to S3")
        
        # Verify it exists in S3
        exists = s3_vector_store.collection_exists_in_s3(test_collection_name)
        print(f"Collection exists in S3: {exists}")
        
        # Try to list S3 collections
        collections = s3_vector_store.list_s3_collections()
        print(f"Collections in S3: {collections}")
        
        return test_collection_name
    except Exception as e:
        print(f"Error setting up test collection: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_download(collection_name):
    """Test downloading the test collection from S3"""
    print(f"\n=== Testing Download of Collection '{collection_name}' ===")
    
    if not collection_name:
        print("No collection name provided, skipping download test")
        return False
    
    # Import services
    from services.s3_vector_store import s3_vector_store
    
    try:
        # Try to download from S3
        print(f"Downloading collection '{collection_name}' from S3...")
        
        # Delete local collection first
        try:
            embedding_service.client.delete_collection(collection_name)
            print("Deleted local collection")
        except:
            pass
        
        # Download collection
        success = s3_vector_store.download_collection(collection_name)
        
        if success:
            print("Successfully downloaded collection from S3")
        else:
            print("Failed to download collection from S3")
            return False
        
        # Try to get the collection
        try:
            collection = embedding_service.client.get_collection(collection_name)
            data = collection.get()
            print(f"Collection size: {len(data['ids'])} documents")
            print(f"Document IDs: {data['ids']}")
            
            if len(data['ids']) > 0:
                print("Download test PASSED")
                return True
            else:
                print("Downloaded collection is empty, test FAILED")
                return False
        except Exception as e:
            print(f"Error getting downloaded collection: {e}")
            return False
    except Exception as e:
        print(f"Error testing download: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_fix():
    """Apply fixes to S3 vector store implementation"""
    print("\n=== Applying Fixes to S3 Vector Store ===")
    
    # Import services
    from services.s3_vector_store import s3_vector_store
    
    # Try different S3 prefix
    old_prefix = s3_vector_store.s3_prefix
    new_prefix = ""  # Try without a prefix
    
    print(f"Changing S3 prefix from '{old_prefix}' to '{new_prefix}'")
    s3_vector_store.s3_prefix = new_prefix
    
    # Update temp directory
    old_temp_dir = s3_vector_store.temp_dir
    new_temp_dir = os.path.join(tempfile.gettempdir(), "chromadb_fixed")
    
    print(f"Changing temp directory from '{old_temp_dir}' to '{new_temp_dir}'")
    
    # Create new temp directory
    Path(new_temp_dir).mkdir(parents=True, exist_ok=True)
    s3_vector_store.temp_dir = new_temp_dir
    s3_vector_store.persistent_dir = new_temp_dir
    
    # Reupload all collections
    for collection_name in ["case_law", "statutes", "regulations"]:
        try:
            # Get collection
            collection = embedding_service.get_collection(collection_name)
            data = collection.get()
            
            print(f"\nReuploading {collection_name}...")
            print(f"Collection size: {len(data['ids'])} documents")
            
            # If collection has documents, force upload to S3
            if len(data['ids']) > 0:
                success = s3_vector_store.upload_collection(collection_name)
                if success:
                    print(f"Successfully uploaded {collection_name} to S3")
                else:
                    print(f"Failed to upload {collection_name} to S3")
            else:
                print(f"Collection {collection_name} is empty, skipping upload")
        except Exception as e:
            print(f"Error reuploading {collection_name}: {e}")
    
    # Verify uploads
    collections = s3_vector_store.list_s3_collections()
    print(f"\nCollections in S3 after fix: {collections}")
    
    # Return to original prefix
    s3_vector_store.s3_prefix = old_prefix
    print(f"Restored S3 prefix to '{old_prefix}'")

def test_direct_embedding():
    """Test direct embedding and collection manipulation"""
    print("\n=== Testing Direct Embedding and Collection Manipulation ===")
    
    # Create a temporary collection for testing
    test_collection_name = "direct_embed_test"
    
    try:
        # Create or get collection
        try:
            embedding_service.client.delete_collection(test_collection_name)
        except:
            pass
        
        print(f"Creating collection {test_collection_name}...")
        test_collection = embedding_service.client.create_collection(name=test_collection_name)
        
        # Create some test documents
        test_docs = [
            "This is the first test document for direct embedding",
            "This is the second test document with different content"
        ]
        test_ids = ["direct_001", "direct_002"]
        test_metadata = [
            {"test": True, "order": 1},
            {"test": True, "order": 2}
        ]
        
        print("Generating embeddings...")
        embeddings = embedding_service.generate_embeddings(test_docs)
        print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")
        
        # Add documents with embeddings
        print("Adding documents with embeddings...")
        test_collection.add(
            documents=test_docs,
            embeddings=embeddings,
            ids=test_ids,
            metadatas=test_metadata
        )
        
        # Check if documents were added
        data = test_collection.get()
        print(f"Collection size: {len(data['ids'])} documents")
        print(f"Document IDs: {data['ids']}")
        
        # Test search
        print("\nTesting search...")
        query = "test document"
        query_embedding = embedding_service.generate_embeddings([query])[0]
        
        results = test_collection.query(
            query_embeddings=[query_embedding],
            n_results=2
        )
        
        print(f"Search results: {json.dumps(results)}")
        
        # Try to save to S3
        from services.s3_vector_store import s3_vector_store
        print("\nSaving collection to S3...")
        success = s3_vector_store.upload_collection(test_collection_name)
        
        if success:
            print("Successfully saved collection to S3")
        else:
            print("Failed to save collection to S3")
        
        # Cleanup
        print("\nCleaning up...")
        embedding_service.client.delete_collection(test_collection_name)
        print(f"Deleted test collection '{test_collection_name}'")
        
        return True
    except Exception as e:
        print(f"Error in direct embedding test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("=== S3 Synchronization Fix Tool ===")
    
    # Test S3 path configuration
    test_s3_path()
    
    # Test direct embedding
    test_direct_embedding()
    
    # Set up test collection
    test_collection_name = setup_test_collection()
    
    # Test download
    download_success = test_download(test_collection_name)
    
    # Apply fixes
    if not download_success:
        apply_fix()
        # Test download again
        test_download(test_collection_name)
    
    print("\nDone! You should restart the application to apply changes:")
    print("  pkill -f app.py && python3 scripts/run_app.py")

if __name__ == "__main__":
    main() 