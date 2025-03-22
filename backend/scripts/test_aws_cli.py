#!/usr/bin/env python3
"""
Script to test AWS S3 access using AWS CLI
"""
import os
import subprocess
import tempfile
from dotenv import load_dotenv

def test_aws_cli():
    """Test AWS S3 access using AWS CLI"""
    print("\n🧪 Testing AWS S3 Access with AWS CLI\n")
    print("=" * 80)
    
    # Load environment variables from .env
    load_dotenv()
    
    # Get AWS credentials from environment
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    s3_bucket = os.getenv("S3_BUCKET_NAME")
    
    if not aws_access_key or not aws_secret_key or not s3_bucket:
        print("❌ Missing AWS credentials in environment variables")
        return
    
    # Create environment with AWS credentials
    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = aws_access_key
    env["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
    env["AWS_DEFAULT_REGION"] = aws_region
    
    # Create a temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    
    try:
        print("✅ Set up AWS credentials in environment")
        
        # Test AWS S3 commands
        print("\n🔄 Testing AWS S3 commands...\n")
        
        # 1. Test AWS CLI version
        print("1. AWS CLI Version:")
        subprocess.run(["aws", "--version"], env=env)
        
        # 2. Test listing S3 buckets
        print("\n2. Listing S3 buckets:")
        subprocess.run(["aws", "s3", "ls"], env=env)
        
        # 3. Test accessing the specific bucket
        print(f"\n3. Listing contents of bucket {s3_bucket}:")
        subprocess.run(["aws", "s3", "ls", f"s3://{s3_bucket}/"], env=env)
        
        # 4. Test creating a test file in the bucket
        print(f"\n4. Testing write access to bucket {s3_bucket}:")
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("This is a test file for S3 access")
        
        test_s3_key = "test_file.txt"
        subprocess.run(["aws", "s3", "cp", test_file, f"s3://{s3_bucket}/{test_s3_key}"], env=env)
        
        # 5. Test deleting the test file
        print(f"\n5. Testing delete access to bucket {s3_bucket}:")
        subprocess.run(["aws", "s3", "rm", f"s3://{s3_bucket}/{test_s3_key}"], env=env)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(test_file):
                os.unlink(test_file)
            os.rmdir(temp_dir)
        except:
            pass
    
    print("\n✅ AWS CLI test completed")
    print("\nBased on these results, you can determine if your AWS credentials:")
    print("1. Are valid (can list buckets)")
    print("2. Have access to the specified bucket")
    print("3. Have read/write permissions for the bucket")
    print("\nIf you see 'Access Denied' errors, you need to check your IAM permissions.")

if __name__ == "__main__":
    test_aws_cli() 