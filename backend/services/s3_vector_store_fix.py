"""
Patched version of the S3 vector store to ensure proper directory handling.
This module is meant to be imported in place of the original s3_vector_store.py.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the original module
from services.s3_vector_store import s3_vector_store

# Store the original method
original_get_path = s3_vector_store._get_collection_path

# Patched method to ensure directory exists
def patched_get_collection_path(collection_name):
    """Patched method that ensures the collection directory exists"""
    path = original_get_path(collection_name)
    os.makedirs(path, exist_ok=True)
    return path

# Patch the method
s3_vector_store._get_collection_path = patched_get_collection_path

# Create directory structure if it doesn't exist
if hasattr(s3_vector_store, 'persistent_dir'):
    # Create the persistent directory
    os.makedirs(s3_vector_store.persistent_dir, exist_ok=True)
    
    # Create a ChromaDB directory
    chroma_dir = os.path.join(s3_vector_store.persistent_dir, "chroma")
    os.makedirs(chroma_dir, exist_ok=True)
    
    # Create collection directories
    for collection_name in ["case_law", "statutes", "regulations"]:
        collection_path = os.path.join(s3_vector_store.persistent_dir, collection_name)
        os.makedirs(collection_path, exist_ok=True)

# Enhance the upload collection method to be more robust
original_upload = s3_vector_store.upload_collection

def patched_upload_collection(collection_name):
    """Patched upload collection method to be more robust"""
    if not s3_vector_store.s3_enabled:
        print(f"S3 storage is disabled. Collection {collection_name} will not be uploaded.")
        return False
        
    try:
        # Create a directory for the collection if it doesn't exist
        collection_path = s3_vector_store._get_collection_path(collection_name)
        
        # Ensure the directory contains at least one file
        dummy_file = os.path.join(collection_path, "collection_info.txt")
        if not os.path.exists(dummy_file):
            with open(dummy_file, "w") as f:
                f.write(f"Collection: {collection_name}\nCreated: {os.environ.get('USER', 'unknown')}")
        
        # Call the original upload method
        return original_upload(collection_name)
    except Exception as e:
        print(f"Error in patched upload collection: {e}")
        import traceback
        traceback.print_exc()
        return False

# Apply the patch to the upload method
s3_vector_store.upload_collection = patched_upload_collection

# Export the patched module
patched_s3_vector_store = s3_vector_store 