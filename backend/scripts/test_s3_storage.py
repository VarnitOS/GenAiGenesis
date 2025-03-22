"""
Test script for the AWS S3 Vector Store integration
This script demonstrates how to use the S3 vector store for ChromaDB collections.
"""

import sys
import os
import json
from time import time
from dotenv import load_dotenv

# Add the parent directory to the path to import the services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_s3_integration():
    """Test the S3 vector store integration"""
    print("\n🧪 Testing S3 Vector Store Integration\n")
    print("=" * 80)
    
    # Ensure .env is loaded
    load_dotenv()
    
    # Verify AWS configuration before importing services
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing AWS configuration in .env file:")
        for var in missing_vars:
            print(f"  - {var} is not set")
        
        print("\nPlease update your .env file with the correct AWS credentials")
        return
    
    # Now try to import the services
    try:
        from services.s3_vector_store import s3_vector_store
        from services.embedding_service import S3_ENABLED
    except ImportError as e:
        print(f"❌ Error importing services: {e}")
        print("Make sure you have all required dependencies installed")
        return
    except Exception as e:
        print(f"❌ Error in services initialization: {e}")
        print("This might be due to incorrect AWS credentials or ChromaDB setup")
        return
    
    # Check if S3 storage is enabled
    if not S3_ENABLED:
        print("❌ S3 storage is not enabled. Set S3_ENABLED=True in .env")
        return
    
    # 1. Test S3 connection
    print("\n🔄 Testing AWS S3 Connection...\n")
    try:
        # List S3 collections
        response = s3_vector_store.s3.list_objects_v2(
            Bucket=s3_vector_store.s3_bucket,
            Prefix=s3_vector_store.s3_prefix
        )
        print("✅ Successfully connected to S3 bucket:", s3_vector_store.s3_bucket)
        
        # Show existing collections
        if 'Contents' in response and response['Contents']:
            print(f"\nFound {len(response['Contents'])} objects in S3:")
            for obj in response['Contents'][:5]:  # Show first 5 only
                print(f"- {obj['Key']} ({obj['Size']} bytes)")
            if len(response['Contents']) > 5:
                print(f"  ... and {len(response['Contents']) - 5} more")
        else:
            print("No existing collections found in S3")
    except Exception as e:
        print(f"❌ Error connecting to S3: {str(e)}")
        print("\nPossible reasons for this error:")
        print("1. Incorrect AWS credentials")
        print("2. The S3 bucket doesn't exist or is in a different region")
        print("3. Network connectivity issues")
        print("\nMake sure your AWS credentials and bucket configuration are correct.")
        return
    
    # 2. Test uploading a collection
    print("\n🔄 Testing collection upload...\n")
    
    # Check if we have any local collections
    local_collections = [
        d for d in os.listdir(s3_vector_store.persistent_dir) 
        if os.path.isdir(os.path.join(s3_vector_store.persistent_dir, d))
    ]
    
    if not local_collections:
        print("❌ No local collections found to upload")
        print("This is expected if you've just cleared the vector_db directory")
        print("Try running your ingestion script first to create some collections")
        
        # Create a dummy collection for testing
        print("\nCreating a dummy collection for testing...")
        dummy_dir = os.path.join(s3_vector_store.persistent_dir, "dummy_test_collection")
        os.makedirs(dummy_dir, exist_ok=True)
        with open(os.path.join(dummy_dir, "test.txt"), "w") as f:
            f.write("Test file for S3 upload")
        
        local_collections = ["dummy_test_collection"]
    
    # Choose the first collection for testing
    test_collection = local_collections[0]
    print(f"Found local collection: {test_collection}")
    
    # Time the upload process
    start_time = time()
    try:
        success = s3_vector_store.upload_collection(test_collection)
        upload_time = time() - start_time
        
        if success:
            print(f"✅ Successfully uploaded collection {test_collection} to S3 in {upload_time:.2f} seconds")
        else:
            print(f"❌ Failed to upload collection {test_collection} to S3")
            return
    except Exception as e:
        print(f"❌ Error uploading to S3: {str(e)}")
        print("Make sure your AWS credentials have write permissions to the bucket")
        return
    
    # 3. Test the manual sync endpoint (simulate an API call)
    print("\n🔄 Testing manual sync through the API...\n")
    
    try:
        # Import necessary components for a simulated API call
        from flask import Flask, request, jsonify
        from werkzeug.test import Client
        from werkzeug.wrappers import Response
        
        # Create a simple Flask app with just the sync endpoint
        app = Flask(__name__)
        
        @app.route('/api/s3/sync', methods=['POST'])
        def sync_with_s3():
            data = request.json or {}
            collection = data.get('collection')
            
            try:
                if collection:
                    result = s3_vector_store.sync_collection(collection)
                    return jsonify({
                        "success": result,
                        "collection": collection
                    })
                else:
                    # Import only here to avoid circular imports
                    from services.embedding_service import embedding_service
                    result = embedding_service.sync_all_with_s3()
                    return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # Create a test client
        with app.test_client() as client:
            # Test syncing a specific collection
            response = client.post('/api/s3/sync', json={"collection": test_collection})
            print(f"Response from sync collection {test_collection}:")
            print(json.dumps(response.get_json(), indent=2))
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
    
    print("\n✅ S3 Vector Store Integration Test Completed")
    print("""
Next steps:
1. Keep S3 storage enabled in your .env file: S3_ENABLED=True
2. Make sure your AWS credentials are correct:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - S3_BUCKET_NAME
3. Run your normal application workflow
4. Your vector database will now automatically sync with S3 storage
""")

if __name__ == "__main__":
    test_s3_integration() 