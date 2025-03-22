#!/usr/bin/env python3
"""
Test script for vector database cleanup functionality.

This script demonstrates how to use the cleanup API endpoint.
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_cleanup(api_url, admin_token):
    """Test the cleanup API endpoint"""
    print("\n=== Testing Vector Database Cleanup API ===\n")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}"
    }
    
    # First, try without confirmation (should fail)
    print("Testing without confirmation (should fail)...")
    response = requests.post(
        f"{api_url}/api/cleanup/vector-db",
        headers=headers,
        json={}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Confirm with the user
    print("\n⚠️  WARNING: This will DELETE ALL VECTOR DATABASE DATA! ⚠️")
    confirmation = input("Are you sure you want to proceed? (yes/no): ")
    
    if confirmation.lower() != "yes":
        print("Operation cancelled.")
        return
    
    # Now try with confirmation
    print("\nTesting with confirmation...")
    response = requests.post(
        f"{api_url}/api/cleanup/vector-db",
        headers=headers,
        json={"confirm": True}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_direct_cleanup():
    """Test the cleanup functionality directly"""
    print("\n=== Testing Direct Vector Database Cleanup ===\n")
    
    # Import cleanup module
    from data_pipeline.cleanup import VectorDBCleanup
    
    # Create cleanup manager
    cleanup = VectorDBCleanup()
    
    # Confirm with the user
    print("⚠️  WARNING: This will DELETE ALL VECTOR DATABASE DATA! ⚠️")
    confirmation = input("Are you sure you want to proceed? (yes/no): ")
    
    if confirmation.lower() != "yes":
        print("Operation cancelled.")
        return
    
    # Perform cleanup
    print("Performing cleanup...")
    result = cleanup.cleanup_all()
    
    # Print result
    print("\nCleanup completed:")
    print(f"Collections cleared: {result['collections_cleared']}")
    if 'cleared_collections' in result:
        print(f"Collections: {', '.join(result['cleared_collections'])}")
    print(f"S3 objects deleted: {result['s3_objects_deleted']}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test vector database cleanup")
    parser.add_argument("--api", action="store_true", help="Test cleanup via API")
    parser.add_argument("--direct", action="store_true", help="Test cleanup directly")
    parser.add_argument("--api-url", type=str, default="http://localhost:5000", 
                        help="API URL for testing")
    parser.add_argument("--admin-token", type=str, 
                        help="Admin API token (or set ADMIN_API_TOKEN environment variable)")
    
    args = parser.parse_args()
    
    # Default to direct test if no option specified
    if not (args.api or args.direct):
        args.direct = True
    
    # Get admin token from args or environment
    admin_token = args.admin_token or os.environ.get("ADMIN_API_TOKEN")
    
    # Run tests
    if args.api:
        if not admin_token:
            print("ERROR: Admin API token required for API test.")
            print("Set --admin-token or ADMIN_API_TOKEN environment variable.")
            return
        
        test_api_cleanup(args.api_url, admin_token)
    
    if args.direct:
        test_direct_cleanup()

if __name__ == "__main__":
    main() 