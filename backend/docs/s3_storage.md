# S3 Vector Storage for ChromaDB

This document explains how to use AWS S3 storage for your vector database collections in GenAI Genesis.

## Overview

The S3 Vector Storage solution allows you to:

1. Store your ChromaDB vector collections in AWS S3 for persistence
2. Synchronize between local and cloud storage
3. Automatically back up your vector database
4. Share vector databases across multiple instances

## Setup Instructions

### 1. AWS Account Setup

You'll need an AWS account with S3 access:

1. Create an AWS account if you don't have one: [AWS Console](https://aws.amazon.com/console/)
2. Create an IAM user with programmatic access and attach the `AmazonS3FullAccess` policy
3. Take note of the Access Key ID and Secret Access Key

### 2. Create an S3 Bucket

1. Go to the S3 service in AWS Console
2. Click "Create bucket"
3. Choose a unique name for your bucket
4. Select a region close to your users
5. Configure other settings as needed (default settings are fine for testing)
6. Click "Create bucket"

### 3. Configure Your .env File

Update your `.env` file with the following settings:

```
# AWS S3 Configuration
S3_ENABLED=True
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your-bucket-name
S3_PREFIX=vector_db/
S3_SYNC_INTERVAL=600  # Seconds between auto-sync
```

### 4. Test the S3 Integration

Run the included test script to verify your S3 setup:

```bash
cd /path/to/GenAIGenesis/backend
python scripts/test_s3_storage.py
```

If successful, you'll see information about your S3 connection and a test upload/download of collections.

## How It Works

The S3 Vector Storage solution works as follows:

1. **Local First**: ChromaDB collections are stored locally first, with periodic uploads to S3
2. **Automatic Sync**: Collections are automatically synced with S3 based on the `S3_SYNC_INTERVAL`
3. **Manual Sync**: You can trigger a manual sync via the API
4. **Disaster Recovery**: If local data is lost, it can be restored from S3

## API Endpoints

### Sync with S3

Endpoint: `POST /api/s3/sync`

This endpoint manually triggers synchronization with S3.

**Request Body (optional):**
```json
{
  "collection": "case_law"
}
```

If `collection` is provided, only that collection is synced. Otherwise, all collections are synced.

**Response:**
```json
{
  "success": true,
  "collection": "case_law"
}
```

## Usage Best Practices

1. **Set an Appropriate Sync Interval**: The default is 10 minutes (600 seconds). Adjust based on your update frequency and S3 costs.

2. **S3 Lifecycle Rules**: Consider setting up S3 lifecycle rules to manage storage costs, such as:
   - Moving older backups to Glacier storage
   - Setting expiration policies for very old backups

3. **Security**: Use IAM roles with minimal permissions required for S3 access.

4. **Multiple Instances**: If running multiple instances that share the same vector database:
   - Increase the sync frequency
   - Implement a locking mechanism for writes
   - Consider using a centralized database instead for frequent multi-instance access

## Troubleshooting

### Common Issues

**Unable to connect to AWS S3**
- Check your AWS credentials
- Verify network connectivity and firewall settings
- Ensure the S3 bucket exists and is accessible

**Sync fails with permission errors**
- Verify IAM permissions for the provided access key
- Check bucket policy restrictions

**High S3 costs**
- Lower the sync frequency
- Implement S3 lifecycle rules
- Monitor S3 usage in AWS Cost Explorer

## Support

For issues with the S3 Vector Storage solution:
1. Check the application logs for errors
2. Review AWS CloudTrail logs for S3 access issues
3. Test connectivity with the `test_s3_storage.py` script 