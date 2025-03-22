#!/usr/bin/env python3
"""
Script to perform direct searches on the vector database without going through the API.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.embedding_service import embedding_service, S3_ENABLED
from services.vector_db_service import vector_db_service

def print_collection_info(collection_name):
    """Print detailed information about a collection"""
    print(f"\n=== Collection Info: {collection_name} ===")
    
    try:
        collection = embedding_service.get_collection(collection_name)
        data = collection.get()
        
        print(f"Collection exists: {collection is not None}")
        print(f"Document count: {len(data.get('ids', []))}")
        
        if data.get('ids'):
            print(f"Document IDs: {data.get('ids')}")
            print(f"First document: {data.get('documents', [''])[0][:200]}...")
        else:
            print("Collection is empty")
    except Exception as e:
        print(f"Error inspecting collection: {e}")

def direct_search(query, collection_name, top_k=2):
    """Perform a direct search on the vector database with detailed logging"""
    print(f"\n=== Direct Search: '{query}' in {collection_name} ===")
    
    try:
        # Get the collection
        collection = embedding_service.get_collection(collection_name)
        print(f"Collection reference obtained: {collection is not None}")
        
        # Generate query embedding
        print("Generating query embedding...")
        query_embedding = embedding_service.generate_embeddings(
            [query],
            cache_key=f"query:{query}"
        )[0]
        print(f"Query embedding generated: {len(query_embedding)} dimensions")
        
        # Perform direct search
        print("Executing direct search...")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        print("\nRaw search results:")
        print(f"Result IDs: {results.get('ids', [[]])[0]}")
        print(f"Result distances: {results.get('distances', [[]])[0]}")
        
        # Also try the service method
        print("\nTrying vector_db_service.search method...")
        service_results = vector_db_service.search(
            query=query,
            collection_name=collection_name,
            top_k=top_k
        )
        
        print(f"Service results: {json.dumps(service_results)}")
        
        return results
    except Exception as e:
        print(f"Error during direct search: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_s3_config():
    """Check S3 configuration"""
    print("\n=== S3 Configuration ===")
    print(f"S3 enabled: {S3_ENABLED}")
    
    if S3_ENABLED:
        from services.s3_vector_store import s3_vector_store
        print(f"S3 bucket: {s3_vector_store.s3_bucket}")
        print(f"S3 prefix: {s3_vector_store.s3_prefix}")
        
        print("Listing S3 collections...")
        try:
            collections = s3_vector_store.list_s3_collections()
            print(f"Collections in S3: {collections}")
        except Exception as e:
            print(f"Error listing S3 collections: {e}")

def examine_stats():
    """Examine stats stored in memory and on disk"""
    print("\n=== Stats Examination ===")
    
    # Check in-memory stats
    print("In-memory stats:")
    print(json.dumps(vector_db_service.stats))
    
    # Check on-disk stats
    stats_path = os.path.join(os.getcwd(), "data", "stats.json")
    if os.path.exists(stats_path):
        try:
            with open(stats_path, 'r') as f:
                disk_stats = json.load(f)
            print("\nOn-disk stats:")
            print(json.dumps(disk_stats))
        except Exception as e:
            print(f"Error reading stats file: {e}")
    else:
        print(f"Stats file does not exist: {stats_path}")

def download_collections_from_s3():
    """Attempt to download collections from S3"""
    print("\n=== Downloading Collections from S3 ===")
    
    if not S3_ENABLED:
        print("S3 is not enabled. Skipping download.")
        return
    
    from services.s3_vector_store import s3_vector_store
    
    for collection_name in ["case_law", "statutes", "regulations"]:
        try:
            print(f"Downloading {collection_name}...")
            success = s3_vector_store.download_collection(collection_name)
            if success:
                print(f"Successfully downloaded {collection_name} from S3")
            else:
                print(f"Failed to download {collection_name} from S3")
        except Exception as e:
            print(f"Error downloading {collection_name}: {e}")

def main():
    """Main function"""
    print("=== Direct Vector DB Search Test ===")
    
    # Check S3 configuration
    check_s3_config()
    
    # Examine stats
    examine_stats()
    
    # Try downloading collections from S3
    download_collections_from_s3()
    
    # Check each collection
    for collection_name in ["case_law", "statutes", "regulations"]:
        print_collection_info(collection_name)
    
    # Perform searches
    direct_search("gender discrimination", "case_law")
    direct_search("equal pay", "statutes")
    direct_search("sexual harassment", "regulations")
    
    print("\nDone!")

if __name__ == "__main__":
    main() 