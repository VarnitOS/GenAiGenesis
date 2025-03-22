#!/usr/bin/env python3
"""
Script to run the Flask application with enhanced S3 vector store support.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import the patched S3 vector store
from services.s3_vector_store_fix import patched_s3_vector_store

# Import the search override
from services import search_override

# Run the application
from app import app

if __name__ == "__main__":
    # Print status information
    print("Starting Flask application with enhanced S3 vector store support")
    print(f"S3 enabled: {patched_s3_vector_store.s3_enabled}")
    if patched_s3_vector_store.s3_enabled:
        print(f"S3 bucket: {patched_s3_vector_store.s3_bucket}")
        print(f"S3 prefix: {patched_s3_vector_store.s3_prefix}")
    
    # Run the Flask application
    app.run(host="0.0.0.0", port=5001, debug=True) 