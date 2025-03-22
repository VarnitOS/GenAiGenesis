#!/usr/bin/env python3
"""
Script to test S3 bucket integration with vector databases.
This script performs comprehensive tests on the S3 synchronization of ChromaDB collections.
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.embedding_service import embedding_service
from services.s3_vector_store import s3_vector_store

# Test document for collections
TEST_DOCUMENT = {
    "id": "test_s3_001",
    "document": "This is a test document for S3 bucket synchronization testing.",
    "metadata": {
        "title": "S3 Test Document",
        "type": "test",
        "timestamp": int(time.time())
    }
}

def print_divider(title):
    """Print a divider with a title for better readability"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def test_s3_connectivity():
    """Test basic connectivity to the S3 bucket"""
    print_divider("TESTING S3 CONNECTIVITY")
    
    print(f"S3 bucket: {s3_vector_store.s3_bucket}")
    print(f"S3 prefix: {s3_vector_store.s3_prefix}")
    print(f"S3 enabled: {s3_vector_store.s3_enabled}")
    
    if not s3_vector_store.s3_enabled:
        print("S3 is not enabled. Check your environment variables.")
        return False
    
    try:
        # List collections
        collections = s3_vector_store.list_s3_collections()
        print(f"Collections in S3: {collections}")
        
        # Try to get a test bucket object if available
        if hasattr(s3_vector_store, 's3'):
            try:
                response = s3_vector_store.s3.list_objects_v2(
                    Bucket=s3_vector_store.s3_bucket,
                    Prefix=s3_vector_store.s3_prefix,
                    MaxKeys=5
                )
                
                if 'Contents' in response:
                    print(f"Found {len(response['Contents'])} objects in the S3 bucket")
                    for obj in response['Contents']:
                        print(f"  - {obj['Key']} ({obj['Size']} bytes)")
                else:
                    print("No objects found in the S3 bucket with the current prefix")
            except Exception as e:
                print(f"Error listing S3 objects: {e}")
        
        return True
    except Exception as e:
        print(f"Error testing S3 connectivity: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_collection():
    """Create a test collection and verify it"""
    print_divider("CREATING TEST COLLECTION")
    
    collection_name = f"s3_test_{int(time.time())}"
    print(f"Creating test collection: {collection_name}")
    
    try:
        # Create or get collection
        try:
            embedding_service.client.delete_collection(collection_name)
            print("Deleted existing collection with same name")
        except:
            pass
        
        # Create collection
        test_collection = embedding_service.client.create_collection(name=collection_name)
        print(f"Created collection: {collection_name}")
        
        # Add test document
        test_collection.add(
            documents=[TEST_DOCUMENT["document"]],
            ids=[TEST_DOCUMENT["id"]],
            metadatas=[TEST_DOCUMENT["metadata"]]
        )
        print(f"Added test document with ID: {TEST_DOCUMENT['id']}")
        
        # Verify document was added
        data = test_collection.get()
        if len(data["ids"]) > 0:
            print(f"Collection contains {len(data['ids'])} document(s)")
            print(f"Document IDs: {data['ids']}")
            return collection_name
        else:
            print("Failed to add document to collection")
            return None
    except Exception as e:
        print(f"Error creating test collection: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_s3_upload(collection_name):
    """Test uploading a collection to S3"""
    print_divider("TESTING S3 UPLOAD")
    
    if not collection_name:
        print("No collection name provided, skipping upload test")
        return False
    
    try:
        print(f"Uploading collection '{collection_name}' to S3...")
        success = s3_vector_store.upload_collection(collection_name)
        
        if success:
            print(f"Successfully uploaded collection '{collection_name}' to S3")
            
            # Verify collection exists in S3
            exists = s3_vector_store.collection_exists_in_s3(collection_name)
            print(f"Collection exists in S3: {exists}")
            
            # List updated collections
            collections = s3_vector_store.list_s3_collections()
            print(f"Collections in S3 after upload: {collections}")
            
            return exists
        else:
            print(f"Failed to upload collection '{collection_name}' to S3")
            return False
    except Exception as e:
        print(f"Error uploading collection to S3: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_s3_download(collection_name):
    """Test downloading a collection from S3"""
    print_divider("TESTING S3 DOWNLOAD")
    
    if not collection_name:
        print("No collection name provided, skipping download test")
        return False
    
    try:
        # Delete local collection first
        try:
            embedding_service.client.delete_collection(collection_name)
            print(f"Deleted local collection '{collection_name}'")
        except Exception as e:
            print(f"Error deleting local collection: {e}")
        
        # Download collection from S3
        print(f"Downloading collection '{collection_name}' from S3...")
        success = s3_vector_store.download_collection(collection_name)
        
        if success:
            print(f"Successfully downloaded collection '{collection_name}' from S3")
            
            # Verify collection exists locally and has the test document
            try:
                collection = embedding_service.client.get_collection(collection_name)
                data = collection.get()
                print(f"Downloaded collection contains {len(data['ids'])} document(s)")
                
                if TEST_DOCUMENT["id"] in data["ids"]:
                    print(f"Test document '{TEST_DOCUMENT['id']}' found in downloaded collection")
                    return True
                else:
                    print(f"Test document '{TEST_DOCUMENT['id']}' not found in downloaded collection")
                    print(f"Document IDs in collection: {data['ids']}")
                    return False
            except Exception as e:
                print(f"Error verifying downloaded collection: {e}")
                return False
        else:
            print(f"Failed to download collection '{collection_name}' from S3")
            return False
    except Exception as e:
        print(f"Error downloading collection from S3: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_in_collection(collection_name):
    """Test searching in a collection"""
    print_divider("TESTING SEARCH IN COLLECTION")
    
    if not collection_name:
        print("No collection name provided, skipping search test")
        return False
    
    try:
        # Get collection
        collection = embedding_service.client.get_collection(collection_name)
        print(f"Got collection '{collection_name}'")
        
        # Generate query embedding
        query = "test document"
        print(f"Generating embedding for query: '{query}'")
        query_embedding = embedding_service.generate_embeddings([query])[0]
        
        # Search collection
        print(f"Searching collection '{collection_name}'...")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=1
        )
        
        print(f"Search results: {json.dumps(results)}")
        
        # Check if test document was found
        if results and 'ids' in results and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
            if TEST_DOCUMENT["id"] in results['ids'][0]:
                print(f"Test document '{TEST_DOCUMENT['id']}' found in search results")
                return True
            else:
                print(f"Test document not found in search results")
                print(f"Found document IDs: {results['ids'][0]}")
                return False
        else:
            print("No search results found")
            return False
    except Exception as e:
        print(f"Error searching in collection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_s3_sync_with_existing_collections():
    """Test S3 synchronization with existing collections"""
    print_divider("TESTING S3 SYNC WITH EXISTING COLLECTIONS")
    
    collections_to_test = ["case_law", "statutes", "regulations"]
    results = {}
    
    for collection_name in collections_to_test:
        print(f"\nTesting collection: {collection_name}")
        
        try:
            # Get collection
            collection = embedding_service.get_collection(collection_name)
            data = collection.get()
            doc_count = len(data.get('ids', []))
            print(f"Collection '{collection_name}' has {doc_count} document(s)")
            
            # Try to sync with S3
            print(f"Syncing collection '{collection_name}' with S3...")
            success = s3_vector_store.sync_collection(collection_name, force_upload=True)
            
            if success:
                print(f"Successfully synced collection '{collection_name}' with S3")
                results[collection_name] = True
            else:
                print(f"Failed to sync collection '{collection_name}' with S3")
                results[collection_name] = False
        except Exception as e:
            print(f"Error testing collection '{collection_name}': {e}")
            results[collection_name] = False
    
    # Print summary
    print("\nS3 sync test summary:")
    for collection_name, success in results.items():
        print(f"  - {collection_name}: {'SUCCESS' if success else 'FAILED'}")
    
    # Return overall success
    return all(results.values())

def clean_up(collection_name):
    """Clean up test collection"""
    print_divider("CLEANING UP")
    
    if not collection_name:
        print("No collection name provided, skipping cleanup")
        return
    
    try:
        # Delete local collection
        try:
            embedding_service.client.delete_collection(collection_name)
            print(f"Deleted local collection '{collection_name}'")
        except Exception as e:
            print(f"Error deleting local collection: {e}")
        
        # Delete collection from S3
        if s3_vector_store.s3_enabled and hasattr(s3_vector_store, 's3'):
            try:
                # Get S3 key
                s3_key = s3_vector_store._get_collection_s3_key(collection_name)
                
                # Delete object from S3
                s3_vector_store.s3.delete_object(
                    Bucket=s3_vector_store.s3_bucket,
                    Key=s3_key
                )
                print(f"Deleted collection '{collection_name}' from S3")
            except Exception as e:
                print(f"Error deleting collection from S3: {e}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def run_all_tests():
    """Run all tests in sequence"""
    overall_success = True
    test_collection_name = None
    
    # Test S3 connectivity
    s3_connected = test_s3_connectivity()
    if not s3_connected:
        print("S3 connectivity test failed, stopping tests")
        return False
    
    # Create test collection
    test_collection_name = create_test_collection()
    if not test_collection_name:
        print("Failed to create test collection, stopping tests")
        return False
    
    # Test S3 upload
    upload_success = test_s3_upload(test_collection_name)
    overall_success = overall_success and upload_success
    
    # Test S3 download
    download_success = test_s3_download(test_collection_name)
    overall_success = overall_success and download_success
    
    # Test search in collection
    search_success = test_search_in_collection(test_collection_name)
    overall_success = overall_success and search_success
    
    # Test S3 sync with existing collections
    sync_success = test_s3_sync_with_existing_collections()
    overall_success = overall_success and sync_success
    
    # Clean up
    clean_up(test_collection_name)
    
    # Print overall results
    print_divider("TEST RESULTS")
    print(f"S3 connectivity: {'PASSED' if s3_connected else 'FAILED'}")
    print(f"Create test collection: {'PASSED' if test_collection_name else 'FAILED'}")
    print(f"S3 upload: {'PASSED' if upload_success else 'FAILED'}")
    print(f"S3 download: {'PASSED' if download_success else 'FAILED'}")
    print(f"Search in collection: {'PASSED' if search_success else 'FAILED'}")
    print(f"S3 sync with existing collections: {'PASSED' if sync_success else 'FAILED'}")
    print(f"\nOverall result: {'PASSED' if overall_success else 'FAILED'}")
    
    return overall_success

def main():
    """Main function"""
    print("=== S3 Vector DB Test Tool ===")
    print(f"Running tests at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate code
    if success:
        print("\nAll tests completed successfully!")
        sys.exit(0)
    else:
        print("\nTests completed with failures.")
        sys.exit(1)

if __name__ == "__main__":
    main() 