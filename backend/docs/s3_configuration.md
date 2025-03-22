# S3-Only Storage Configuration

This document explains how the system is configured to use AWS S3 as the primary storage for vector databases, without maintaining a local ChromaDB database.

## Overview

The application is configured to use AWS S3 as the only persistent storage for ChromaDB vector databases:

1. ChromaDB collections are loaded from S3 on startup
2. New data is immediately saved to S3 after modifications
3. Local storage is only used as a temporary workspace

## Configuration

To use S3-only storage, ensure your `.env` file has the following settings:

```
# S3 must be enabled for this configuration
S3_ENABLED=True

# AWS credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
S3_PREFIX=vector_db/

# Optional: Set a shorter sync interval for more frequent S3 saves
S3_SYNC_INTERVAL=60
```

## How It Works

1. **In-Memory ChromaDB**: The application uses ChromaDB's in-memory client instead of the persistent client.

2. **S3 Workflow**:
   - On startup, the application downloads all collections from S3
   - When documents are added, the collection is immediately saved to S3
   - When searching, the application uses the in-memory collection (which was loaded from S3)
   - Collections can be manually synced with the `/api/s3/sync` endpoint

3. **Temporary Storage**: A temporary directory is used only for intermediate file operations when downloading/uploading to S3.

## Benefits

- **True Cloud Storage**: No reliance on local disk space for persistence
- **High Availability**: The vector database can be recovered from S3 if the server crashes
- **Scalability**: Multiple instances can share the same vector database by syncing with S3
- **Backup & Migration**: The database is automatically backed up in S3 and can be migrated to new servers

## Running the Application

Use the special runner script that initializes the S3-only environment:

```bash
python3 scripts/run_app.py
```

This script sets up the temporary workspace and starts the application with S3 as the primary storage. 