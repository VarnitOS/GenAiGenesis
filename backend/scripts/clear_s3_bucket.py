#!/usr/bin/env python3
"""
Script to clear S3 bucket after response generation.

This script can be:
1. Imported and used programmatically
2. Run directly from the command line to clear the S3 bucket

It uses the VectorDBCleanup class to clear the S3 bucket.
"""

import os
import sys
import logging
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import cleanup module
from data_pipeline.cleanup import VectorDBCleanup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ClearS3Bucket")

def clear_s3_bucket():
    """
    Clear the S3 bucket used for vector database storage.
    
    Returns:
        int: Number of objects deleted
    """
    try:
        cleanup = VectorDBCleanup()
        deleted_objects = cleanup.clear_s3_bucket()
        logger.info(f"Successfully cleared S3 bucket. Deleted {len(deleted_objects)} objects.")
        return len(deleted_objects)
    except Exception as e:
        logger.error(f"Failed to clear S3 bucket: {str(e)}")
        raise

def clear_all():
    """
    Clear all vector database collections and S3 bucket.
    
    Returns:
        dict: Results of the cleanup operation
    """
    try:
        cleanup = VectorDBCleanup()
        result = cleanup.cleanup_all()
        logger.info(f"Successfully cleared all collections and S3 bucket.")
        return result
    except Exception as e:
        logger.error(f"Failed to clear collections and S3 bucket: {str(e)}")
        raise

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Clear S3 bucket and/or vector database collections')
    parser.add_argument('--all', action='store_true', help='Clear all collections and S3 bucket')
    parser.add_argument('--confirm', action='store_true', help='Confirm clearing operation (required)')
    
    args = parser.parse_args()
    
    if not args.confirm:
        print("ERROR: This operation will DELETE DATA from the S3 bucket.")
        print("To confirm, run again with --confirm flag.")
        return 1
    
    try:
        if args.all:
            result = clear_all()
            print(f"Cleared {result['collections_cleared']} collections and {result['s3_objects_deleted']} S3 objects.")
        else:
            num_deleted = clear_s3_bucket()
            print(f"Cleared {num_deleted} objects from S3 bucket.")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 