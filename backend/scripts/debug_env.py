#!/usr/bin/env python3
"""
Debug script to check if environment variables are being loaded correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def debug_env():
    print("\n🔍 Debugging Environment Variables\n")
    print("=" * 80)
    
    # Print current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Print .env file path
    env_path = os.path.join(os.getcwd(), ".env")
    print(f".env file path: {env_path}")
    print(f".env file exists: {os.path.exists(env_path)}")
    
    # Try to load .env file
    print("\nTrying to load .env file...")
    load_dotenv(env_path)
    
    # Check AWS environment variables
    aws_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "S3_BUCKET_NAME",
        "S3_ENABLED"
    ]
    
    print("\nAWS Environment Variables:")
    for var in aws_vars:
        value = os.getenv(var)
        if value:
            # Show only first few characters of sensitive values
            if "KEY" in var:
                masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                print(f"  - {var}: {masked_value}")
            else:
                print(f"  - {var}: {value}")
        else:
            print(f"  - {var}: NOT SET")

    # Read .env file contents directly
    print("\nContents of .env file:")
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                # Skip comments and empty lines
                if line.strip() and not line.strip().startswith('#'):
                    # Mask sensitive values
                    if "KEY" in line or "SECRET" in line:
                        parts = line.split('=', 1)
                        if len(parts) > 1:
                            key = parts[0]
                            value = parts[1].strip()
                            masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                            print(f"  {key}={masked_value}")
                    else:
                        print(f"  {line.strip()}")
    except Exception as e:
        print(f"Error reading .env file: {e}")

if __name__ == "__main__":
    debug_env() 