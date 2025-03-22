#!/usr/bin/env python3
"""
Comprehensive test for the entire AWS pipeline including:
1. S3 connectivity and configuration
2. Uploading collections to S3
3. Downloading collections from S3 
4. API search functionality
5. Direct vector searches
"""

import os
import sys
import json
import time
import requests
import shutil
from pathlib import Path

# Add the parent directory to the path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.embedding_service import embedding_service, S3_ENABLED
from services.s3_vector_store_fix import patched_s3_vector_store
from scripts.fix_embeddings import CASE_LAW_DOCUMENTS, STATUTE_DOCUMENTS, REGULATION_DOCUMENTS

# API endpoint
API_URL = "http://localhost:5001/api"

def print_divider(title):
    """Print a divider with a title for better readability"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def test_s3_connectivity():
    """Test S3 connectivity and configuration"""
    print_divider("TESTING S3 CONNECTIVITY")
    
    print(f"S3 enabled: {patched_s3_vector_store.s3_enabled}")
    if not patched_s3_vector_store.s3_enabled:
        print("S3 is not enabled. Check your environment variables.")
        return False
    
    print(f"S3 bucket: {patched_s3_vector_store.s3_bucket}")
    print(f"S3 prefix: {patched_s3_vector_store.s3_prefix}")
    
    try:
        # List collections in S3
        collections = patched_s3_vector_store.list_s3_collections()
        print(f"Collections in S3: {collections}")
        
        # Try to get a test bucket object if available
        if hasattr(patched_s3_vector_store, 's3'):
            try:
                response = patched_s3_vector_store.s3.list_objects_v2(
                    Bucket=patched_s3_vector_store.s3_bucket,
                    Prefix=patched_s3_vector_store.s3_prefix,
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
        return False

def reset_and_populate_collections():
    """Reset collections and populate them with sample documents"""
    print_divider("RESETTING AND POPULATING COLLECTIONS")
    
    # Delete existing collections
    try:
        collections = ['case_law', 'statutes', 'regulations']
        for collection in collections:
            try:
                if collection == 'case_law':
                    embedding_service.case_law_collection.delete(where={"_id": {"$exists": True}})
                elif collection == 'statutes':
                    embedding_service.statutes_collection.delete(where={"_id": {"$exists": True}})
                elif collection == 'regulations':
                    embedding_service.regulations_collection.delete(where={"_id": {"$exists": True}})
                print(f"Deleted {collection} collection")
            except Exception as e:
                print(f"Error deleting {collection} collection: {e}")
    except Exception as e:
        print(f"Error in collection cleanup: {e}")
    
    # Populate collections
    try:
        # Populate case_law collection
        documents = [doc["document"] for doc in CASE_LAW_DOCUMENTS]
        metadatas = [doc["metadata"] for doc in CASE_LAW_DOCUMENTS]
        ids = [doc["id"] for doc in CASE_LAW_DOCUMENTS]
        
        embeddings = embedding_service.generate_embeddings(documents)
        
        embedding_service.case_law_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to case_law collection")
        
        # Populate statutes collection
        documents = [doc["document"] for doc in STATUTE_DOCUMENTS]
        metadatas = [doc["metadata"] for doc in STATUTE_DOCUMENTS]
        ids = [doc["id"] for doc in STATUTE_DOCUMENTS]
        
        embeddings = embedding_service.generate_embeddings(documents)
        
        embedding_service.statutes_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to statutes collection")
        
        # Populate regulations collection
        documents = [doc["document"] for doc in REGULATION_DOCUMENTS]
        metadatas = [doc["metadata"] for doc in REGULATION_DOCUMENTS]
        ids = [doc["id"] for doc in REGULATION_DOCUMENTS]
        
        embeddings = embedding_service.generate_embeddings(documents)
        
        embedding_service.regulations_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to regulations collection")
        
        return True
    except Exception as e:
        print(f"Error populating collections: {e}")
        return False

def test_s3_upload():
    """Test uploading collections to S3"""
    print_divider("TESTING S3 UPLOAD")
    
    collections = ['case_law', 'statutes', 'regulations']
    upload_results = {}
    
    for collection in collections:
        print(f"Testing upload for collection: {collection}")
        try:
            success = patched_s3_vector_store.upload_collection(collection)
            upload_results[collection] = success
            if success:
                print(f"Successfully uploaded {collection} to S3")
            else:
                print(f"Failed to upload {collection} to S3")
        except Exception as e:
            print(f"Error uploading {collection} to S3: {e}")
            upload_results[collection] = False
    
    # Print summary
    print("\nS3 upload summary:")
    overall_success = True
    for collection, success in upload_results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  - {collection}: {status}")
        overall_success = overall_success and success
    
    return overall_success

def test_s3_download():
    """Test downloading collections from S3"""
    print_divider("TESTING S3 DOWNLOAD")
    
    collections = ['case_law', 'statutes', 'regulations']
    download_results = {}
    
    # First, try to delete the local collections
    try:
        for collection in collections:
            try:
                if collection == 'case_law':
                    embedding_service.case_law_collection.delete(where={"_id": {"$exists": True}})
                elif collection == 'statutes':
                    embedding_service.statutes_collection.delete(where={"_id": {"$exists": True}})
                elif collection == 'regulations':
                    embedding_service.regulations_collection.delete(where={"_id": {"$exists": True}})
                print(f"Deleted local {collection} collection")
            except Exception as e:
                print(f"Error deleting local {collection} collection: {e}")
    except Exception as e:
        print(f"Error in local collection cleanup: {e}")
    
    # Now try to download each collection
    for collection in collections:
        print(f"Testing download for collection: {collection}")
        try:
            success = patched_s3_vector_store.download_collection(collection)
            download_results[collection] = success
            if success:
                print(f"Successfully downloaded {collection} from S3")
                
                # Verify documents were downloaded
                collection_obj = None
                if collection == 'case_law':
                    collection_obj = embedding_service.case_law_collection
                elif collection == 'statutes':
                    collection_obj = embedding_service.statutes_collection
                elif collection == 'regulations':
                    collection_obj = embedding_service.regulations_collection
                
                if collection_obj:
                    data = collection_obj.get()
                    doc_count = len(data.get('ids', []))
                    print(f"Downloaded collection contains {doc_count} document(s)")
            else:
                print(f"Failed to download {collection} from S3")
        except Exception as e:
            print(f"Error downloading {collection} from S3: {e}")
            download_results[collection] = False
    
    # Print summary
    print("\nS3 download summary:")
    overall_success = True
    for collection, success in download_results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  - {collection}: {status}")
        overall_success = overall_success and success
    
    return overall_success

def test_api_search():
    """Test the search API endpoints"""
    print_divider("TESTING API SEARCH")
    
    test_queries = [
        {"collection": "case_law", "query": "employment discrimination lawsuit", "top_k": 2},
        {"collection": "statutes", "query": "equal pay legislation", "top_k": 2},
        {"collection": "regulations", "query": "sexual harassment", "top_k": 2}
    ]
    
    api_results = {}
    
    for test in test_queries:
        collection = test["collection"]
        query = test["query"]
        top_k = test["top_k"]
        
        print(f"Testing API search for query '{query}' in collection '{collection}'")
        
        try:
            response = requests.post(
                f"{API_URL}/search",
                json={
                    "query": query,
                    "collection": collection,
                    "top_k": top_k
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                print(f"API returned {len(results)} results")
                if len(results) > 0:
                    for i, result in enumerate(results):
                        if "metadata" in result and "title" in result["metadata"]:
                            print(f"  - Result {i+1}: {result['metadata']['title']}")
                        else:
                            print(f"  - Result {i+1}: {result.get('id', 'No ID')}")
                    
                    api_results[collection] = True
                else:
                    print("No results returned from API")
                    api_results[collection] = False
            else:
                print(f"API request failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                api_results[collection] = False
        except Exception as e:
            print(f"Error testing API search: {e}")
            api_results[collection] = False
    
    # Print summary
    print("\nAPI search summary:")
    overall_success = True
    for collection, success in api_results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  - {collection}: {status}")
        overall_success = overall_success and success
    
    return overall_success

def test_direct_vector_search():
    """Test direct vector searches"""
    print_divider("TESTING DIRECT VECTOR SEARCH")
    
    test_queries = [
        {"collection": "case_law", "query": "employment discrimination lawsuit", "top_k": 2},
        {"collection": "statutes", "query": "equal pay legislation", "top_k": 2},
        {"collection": "regulations", "query": "sexual harassment", "top_k": 2}
    ]
    
    direct_results = {}
    
    for test in test_queries:
        collection_name = test["collection"]
        query = test["query"]
        top_k = test["top_k"]
        
        print(f"Testing direct vector search for query '{query}' in collection '{collection_name}'")
        
        try:
            # Get the collection object
            collection = None
            if collection_name == "case_law":
                collection = embedding_service.case_law_collection
            elif collection_name == "statutes":
                collection = embedding_service.statutes_collection
            elif collection_name == "regulations":
                collection = embedding_service.regulations_collection
            
            if collection:
                # Generate query embedding
                query_embedding = embedding_service.generate_embeddings([query])[0]
                print(f"Generated query embedding with dimension {len(query_embedding)}")
                
                # Perform search
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                
                if results and 'ids' in results and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
                    print(f"Found {len(results['ids'][0])} results:")
                    for i in range(len(results['ids'][0])):
                        doc_id = results['ids'][0][i]
                        metadata = results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'][0] else {}
                        title = metadata.get('title', 'No title')
                        print(f"  - Result {i+1}: {title} (ID: {doc_id})")
                    
                    direct_results[collection_name] = True
                else:
                    print("No results found")
                    direct_results[collection_name] = False
            else:
                print(f"Collection {collection_name} not found")
                direct_results[collection_name] = False
        except Exception as e:
            print(f"Error in direct vector search: {e}")
            import traceback
            traceback.print_exc()
            direct_results[collection_name] = False
    
    # Print summary
    print("\nDirect vector search summary:")
    overall_success = True
    for collection, success in direct_results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  - {collection}: {status}")
        overall_success = overall_success and success
    
    return overall_success

def test_stats_api():
    """Test the stats API endpoint"""
    print_divider("TESTING STATS API")
    
    try:
        response = requests.get(f"{API_URL}/stats")
        
        if response.status_code == 200:
            data = response.json()
            print("Stats API returned:")
            print(json.dumps(data, indent=2))
            
            # Check if collections are present
            collections = data.get("collections", {})
            if "case_law" in collections and "statutes" in collections and "regulations" in collections:
                print("All collections found in stats")
                return True
            else:
                print("Not all collections found in stats")
                return False
        else:
            print(f"Stats API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing stats API: {e}")
        return False

def test_s3_sync_api():
    """Test the S3 sync API endpoint"""
    print_divider("TESTING S3 SYNC API")
    
    try:
        response = requests.post(f"{API_URL}/s3/sync")
        
        if response.status_code == 200:
            data = response.json()
            print("S3 sync API returned:")
            print(json.dumps(data, indent=2))
            
            if data.get("success", False):
                print("S3 sync was successful")
                return True
            else:
                print("S3 sync failed")
                return False
        else:
            print(f"S3 sync API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing S3 sync API: {e}")
        return False

def main():
    """Main function to run all tests"""
    print("=== AWS PIPELINE COMPREHENSIVE TEST ===")
    print(f"Starting tests at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Test S3 connectivity
    test_results["s3_connectivity"] = test_s3_connectivity()
    
    # Reset and populate collections
    test_results["reset_collections"] = reset_and_populate_collections()
    
    # Test S3 upload
    test_results["s3_upload"] = test_s3_upload()
    
    # Test S3 download
    test_results["s3_download"] = test_s3_download()
    
    # Test API search
    test_results["api_search"] = test_api_search()
    
    # Test direct vector search
    test_results["direct_vector_search"] = test_direct_vector_search()
    
    # Test stats API
    test_results["stats_api"] = test_stats_api()
    
    # Test S3 sync API
    test_results["s3_sync_api"] = test_s3_sync_api()
    
    # Print overall summary
    print_divider("TEST SUMMARY")
    overall_success = True
    for test_name, success in test_results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        overall_success = overall_success and success
    
    print(f"\nOverall Test Result: {'PASSED' if overall_success else 'FAILED'}")
    print(f"Tests completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 