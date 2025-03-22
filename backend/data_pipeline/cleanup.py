#!/usr/bin/env python3
"""
Cleanup module for vector database maintenance.

This module handles:
1. Clearing vector database collections
2. Deleting S3 bucket objects related to vector db
3. Exposing functionality through API endpoints
"""

import os
import sys
import logging
import boto3
from typing import Dict, Any, List, Optional, Union

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import vector database service if available
try:
    from services.vector_db_service import vector_db
except ImportError:
    vector_db = None
    logging.warning("Vector DB service not available")

logger = logging.getLogger("VectorDBCleanup")

class VectorDBCleanup:
    """Cleanup functionality for vector database and S3 storage"""
    
    def __init__(self):
        """Initialize cleanup module"""
        self.s3_bucket = os.environ.get("S3_BUCKET", "lawder-vector-store-test")
        self.s3_prefix = os.environ.get("S3_PREFIX", "vector_db/")
        self.collections = ["case_law", "statutes", "regulations", "web_search"]
    
    def cleanup_all(self) -> Dict[str, Any]:
        """
        Clean up all vector database collections and S3 storage
        
        Returns:
            Dictionary with cleanup results
        """
        logger.info("Starting complete vector database cleanup")
        
        result = {
            "collections_cleared": 0,
            "s3_objects_deleted": 0,
            "errors": []
        }
        
        # Clear vector database collections
        try:
            cleared_collections = self.clear_collections()
            result["collections_cleared"] = len(cleared_collections)
            result["cleared_collections"] = cleared_collections
        except Exception as e:
            error_msg = f"Error clearing collections: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        # Clear S3 bucket
        try:
            deleted_objects = self.clear_s3_bucket()
            result["s3_objects_deleted"] = len(deleted_objects)
        except Exception as e:
            error_msg = f"Error clearing S3 bucket: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        logger.info(f"Cleanup completed: {result['collections_cleared']} collections cleared, {result['s3_objects_deleted']} S3 objects deleted")
        
        return result
    
    def clear_collections(self) -> List[str]:
        """
        Clear all vector database collections
        
        Returns:
            List of cleared collection names
        """
        cleared_collections = []
        
        if vector_db is not None and hasattr(vector_db, 'get_collection'):
            for collection_name in self.collections:
                try:
                    # Get collection
                    collection = vector_db.get_collection(collection_name)
                    
                    # Delete all documents
                    collection.delete()
                    
                    # Re-create empty collection
                    vector_db.create_collection(collection_name)
                    
                    cleared_collections.append(collection_name)
                    logger.info(f"Cleared collection: {collection_name}")
                except Exception as e:
                    logger.error(f"Error clearing collection {collection_name}: {e}")
        else:
            # Fallback to direct ChromaDB if available
            try:
                import chromadb
                client = chromadb.Client()
                
                for collection_name in self.collections:
                    try:
                        # Delete collection
                        client.delete_collection(collection_name)
                        
                        # Re-create empty collection
                        client.create_collection(collection_name)
                        
                        cleared_collections.append(collection_name)
                        logger.info(f"Cleared collection: {collection_name}")
                    except Exception as e:
                        logger.error(f"Error clearing collection {collection_name}: {e}")
            except ImportError:
                logger.error("Neither vector_db service nor ChromaDB available")
        
        return cleared_collections
    
    def clear_s3_bucket(self) -> List[str]:
        """
        Clear all vector database objects from S3 bucket
        
        Returns:
            List of deleted S3 object keys
        """
        deleted_objects = []
        
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        try:
            # List objects in bucket with prefix
            response = s3.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=self.s3_prefix
            )
            
            # Check if objects exist
            if 'Contents' not in response:
                logger.info(f"No objects found in {self.s3_bucket}/{self.s3_prefix}")
                return deleted_objects
            
            # Get list of objects to delete
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            
            # Delete objects
            if objects_to_delete:
                s3.delete_objects(
                    Bucket=self.s3_bucket,
                    Delete={'Objects': objects_to_delete}
                )
                
                deleted_objects = [obj['Key'] for obj in objects_to_delete]
                logger.info(f"Deleted {len(deleted_objects)} objects from {self.s3_bucket}/{self.s3_prefix}")
        
        except Exception as e:
            logger.error(f"Error deleting S3 objects: {e}")
            raise
        
        return deleted_objects


# Command line interface
if __name__ == "__main__":
    import argparse
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Clean up vector database and S3 storage")
    parser.add_argument("--confirm", action="store_true", 
                        help="Confirm cleanup operation (required)")
    
    args = parser.parse_args()
    
    if not args.confirm:
        print("ERROR: This operation will DELETE ALL VECTOR DATABASE DATA.")
        print("To confirm, run again with --confirm flag.")
        sys.exit(1)
    
    # Perform cleanup
    cleanup = VectorDBCleanup()
    result = cleanup.cleanup_all()
    
    # Print result
    print("Cleanup completed:")
    print(f"Collections cleared: {result['collections_cleared']}")
    print(f"S3 objects deleted: {result['s3_objects_deleted']}")
    
    if result['errors']:
        print("Errors:")
        for error in result['errors']:
            print(f"  - {error}") 