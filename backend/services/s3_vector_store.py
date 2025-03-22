import os
import pickle
import json
from dotenv import load_dotenv
import time
import chromadb
from pathlib import Path
import shutil
import tempfile

# Load environment variables
load_dotenv()

# Check if S3 is enabled
S3_ENABLED = os.getenv("S3_ENABLED", "False").lower() in ("true", "1", "t")

# Only import boto3 if S3 is enabled
if S3_ENABLED:
    import boto3
    from botocore.exceptions import ClientError

class S3VectorStore:
    """Service for storing and retrieving vector database collections from AWS S3"""
    
    def __init__(self):
        """Initialize the S3 vector store service"""
        # Get AWS credentials from environment variables
        self.s3_enabled = S3_ENABLED
        
        if not self.s3_enabled:
            print("S3 storage is disabled. Using local storage only.")
            # Set up local directories even if S3 is disabled
            self.temp_dir = os.path.join(tempfile.gettempdir(), "chromadb_temp")
            Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
            return
            
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.s3_prefix = os.getenv("S3_PREFIX", "vector_db/")
        
        if not aws_access_key or not aws_secret_key or not self.s3_bucket:
            print("Warning: AWS credentials or bucket not set in environment variables")
            self.s3_enabled = False
        else:
            try:
                # Initialize S3 client
                self.s3 = boto3.client(
                    's3',
                    region_name=aws_region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
            except Exception as e:
                print(f"Error initializing S3 client: {e}")
                self.s3_enabled = False
        
        # Local temporary directory for ChromaDB files
        self.temp_dir = os.path.join(tempfile.gettempdir(), "chromadb_temp")
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        
        # Local persistent directory for ChromaDB is now the same as temp
        self.persistent_dir = self.temp_dir
        
        # Track last sync time
        self.last_sync = {}
    
    def _get_collection_s3_key(self, collection_name):
        """Get the S3 key for a collection"""
        return f"{self.s3_prefix}{collection_name}.zip"
    
    def _get_collection_path(self, collection_name):
        """Get the local path for a collection"""
        return os.path.join(self.persistent_dir, collection_name)
    
    def _get_temp_collection_path(self, collection_name):
        """Get a temporary path for a collection"""
        return os.path.join(self.temp_dir, collection_name)
    
    def upload_collection(self, collection_name):
        """Upload a collection to S3"""
        if not self.s3_enabled:
            print(f"S3 storage is disabled. Collection {collection_name} will not be uploaded.")
            return False
            
        try:
            # Create a zip file of the collection directory
            collection_path = self._get_collection_path(collection_name)
            temp_zip = os.path.join(self.temp_dir, f"{collection_name}.zip")
            
            # Check if collection exists locally
            if not os.path.exists(collection_path):
                print(f"Collection {collection_name} not found locally")
                return False
            
            # Create a zip archive
            shutil.make_archive(
                os.path.join(self.temp_dir, collection_name),
                'zip',
                self.persistent_dir,
                collection_name
            )
            
            # Upload to S3
            s3_key = self._get_collection_s3_key(collection_name)
            self.s3.upload_file(
                temp_zip,
                self.s3_bucket,
                s3_key
            )
            
            # Update sync time
            self.last_sync[collection_name] = time.time()
            
            # Clean up temp file
            if os.path.exists(temp_zip):
                os.remove(temp_zip)
                
            print(f"Collection {collection_name} uploaded to S3")
            return True
            
        except Exception as e:
            print(f"Error uploading collection {collection_name} to S3: {e}")
            return False
    
    def download_collection(self, collection_name):
        """Download a collection from S3"""
        if not self.s3_enabled:
            print(f"S3 storage is disabled. Collection {collection_name} will not be downloaded.")
            return False
            
        try:
            # Get S3 key
            s3_key = self._get_collection_s3_key(collection_name)
            temp_zip = os.path.join(self.temp_dir, f"{collection_name}.zip")
            
            # Download from S3
            self.s3.download_file(
                self.s3_bucket,
                s3_key,
                temp_zip
            )
            
            # Extract zip file
            shutil.unpack_archive(
                temp_zip,
                self.persistent_dir,
                'zip'
            )
            
            # Clean up temp file
            if os.path.exists(temp_zip):
                os.remove(temp_zip)
                
            # Update sync time
            self.last_sync[collection_name] = time.time()
            
            print(f"Collection {collection_name} downloaded from S3")
            return True
            
        except Exception as e:
            if hasattr(e, 'response') and e.response['Error']['Code'] == 'NoSuchKey':
                print(f"Collection {collection_name} not found in S3")
            else:
                print(f"Error downloading collection {collection_name} from S3: {e}")
            return False
    
    def collection_exists_in_s3(self, collection_name):
        """Check if a collection exists in S3"""
        if not self.s3_enabled:
            return False
            
        try:
            s3_key = self._get_collection_s3_key(collection_name)
            self.s3.head_object(Bucket=self.s3_bucket, Key=s3_key)
            return True
        except Exception:
            return False
    
    def list_s3_collections(self):
        """List all collections in S3"""
        if not self.s3_enabled:
            return []
            
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=self.s3_prefix
            )
            
            s3_collections = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith('.zip'):
                        collection_name = key[len(self.s3_prefix):-4]  # Remove prefix and .zip
                        s3_collections.append(collection_name)
                        
            return s3_collections
        except Exception as e:
            print(f"Error listing S3 collections: {e}")
            return []
    
    def sync_collection(self, collection_name, force_upload=False):
        """Sync a collection with S3 (upload if changes, download if not local)"""
        if not self.s3_enabled:
            print(f"S3 storage is disabled. Collection {collection_name} will use local storage only.")
            return True
            
        # In S3-only mode, we prioritize S3 version
        s3_exists = self.collection_exists_in_s3(collection_name)
        local_exists = os.path.exists(self._get_collection_path(collection_name))
        
        if force_upload and local_exists:
            # Force upload from local to S3
            return self.upload_collection(collection_name)
        elif s3_exists and not local_exists:
            # Download from S3 if not local
            return self.download_collection(collection_name)
        elif s3_exists and local_exists:
            # Both exist, we favor the S3 version in S3-only mode
            return self.download_collection(collection_name)
        elif local_exists:
            # Only local exists, upload to S3
            return self.upload_collection(collection_name)
        else:
            # Neither exists
            print(f"Collection {collection_name} does not exist locally or in S3")
            return False
    
    def sync_all_collections(self):
        """Sync all collections with S3"""
        if not self.s3_enabled:
            print("S3 storage is disabled. Collections will use local storage only.")
            return True
            
        # Get all S3 collections
        s3_collections = self.list_s3_collections()
        print(f"Found {len(s3_collections)} collections in S3: {s3_collections}")
        
        # Get all local collections
        local_collections = []
        if os.path.exists(self.persistent_dir):
            local_collections = [
                d for d in os.listdir(self.persistent_dir) 
                if os.path.isdir(os.path.join(self.persistent_dir, d))
            ]
        
        # Combine unique collections
        all_collections = set(local_collections + s3_collections)
        
        # Sync each collection
        success = True
        for collection_name in all_collections:
            if not self.sync_collection(collection_name):
                success = False
                
        return success

# Create a singleton instance
s3_vector_store = S3VectorStore() 