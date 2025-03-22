# Backend Troubleshooting Guide

This document provides solutions for common issues with the backend application.

## ChromaDB Database Schema Issues

### Symptoms

If you encounter errors like:

```
sqlite3.OperationalError: no such column: collections.topic
```

This indicates a ChromaDB schema incompatibility issue.

### Solution

1. **Clear the ChromaDB data directory**: 
   - The ChromaDB database files may be corrupted or using an incompatible schema
   - Run the provided script to clean the environment:
   ```bash
   python3 scripts/run_app.py
   ```

   This script:
   - Removes all files and directories in the `data/vector_db` folder
   - Starts the application with a clean ChromaDB environment

2. **Ensure compatible ChromaDB version**:
   - If issues persist, ensure you're using ChromaDB 0.4.22:
   ```bash
   pip install chromadb==0.4.22
   ```

## AWS S3 Integration Issues

### Symptoms

If you see access denied errors when trying to use S3 storage:

```
An error occurred (AccessDenied) when calling the CreateSession operation: Access Denied
```

### Solution

1. **Disable S3 temporarily**:
   - Set `S3_ENABLED=False` in your `.env` file until permissions are fixed
   
2. **Check AWS credentials**:
   - Verify your AWS credentials have the necessary permissions
   - See detailed instructions in the [aws_troubleshooting.md](aws_troubleshooting.md) document

## Running the Application

For normal operation:
```bash
python3 app.py
```

For a clean start (clearing ChromaDB data):
```bash
python3 scripts/run_app.py
```

For debugging environment variables:
```bash
python3 scripts/debug_env.py
``` 