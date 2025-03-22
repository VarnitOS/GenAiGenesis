#!/usr/bin/env python3
"""
Run script for the application with S3-only storage for ChromaDB.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """Run the application with S3-only storage"""
    # Get the base directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Create temporary directory for ChromaDB operations
    temp_dir = os.path.join(tempfile.gettempdir(), "chromadb_temp")
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"Using ChromaDB with S3-only storage (temporary dir: {temp_dir})")
    
    # Import the app and run it
    print("\nStarting application...")
    os.chdir(base_dir)
    
    # Run the app using exec to replace the current process
    sys.path.insert(0, base_dir)
    app_path = os.path.join(base_dir, 'app.py')
    
    # Print debug information
    print(f"App path: {app_path}")
    print(f"Current directory: {os.getcwd()}")
    print("Python path:")
    for path in sys.path:
        print(f"  - {path}")
    
    # Execute the app
    os.execv(sys.executable, [sys.executable, app_path])

if __name__ == "__main__":
    main() 