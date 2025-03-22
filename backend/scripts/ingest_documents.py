import os
import sys
import argparse
import json
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.vector_db_service import vector_db_service
from services.embedding_service import embedding_service
from services.s3_vector_store import s3_vector_store

def parse_args():
    parser = argparse.ArgumentParser(description='Ingest legal documents into vector databases')
    parser.add_argument('--source', choices=['case_law', 'statutes', 'regulations', 'all'], default='all',
                        help='Type of documents to ingest (default: all)')
    parser.add_argument('--directory', type=str, 
                        help='Directory containing documents to ingest (default: data/raw_documents/[source])')
    parser.add_argument('--reset', action='store_true',
                        help='Reset the database before ingesting')
    parser.add_argument('--force-sync', action='store_true',
                        help='Force sync with S3 after ingestion')
    return parser.parse_args()

def reset_database(db_type):
    """Reset vector databases by removing collections"""
    if db_type == 'case_law' or db_type == 'all':
        try:
            collection = embedding_service.case_law_collection
            # Get all document IDs
            result = collection.get()
            if result["ids"]:
                collection.delete(ids=result["ids"])
                print(f"Reset case law database")
                if hasattr(embedding_service, '_save_collection_to_s3'):
                    embedding_service._save_collection_to_s3('case_law')
        except Exception as e:
            print(f"Error resetting case law database: {e}")
            
    if db_type == 'statutes' or db_type == 'all':
        try:
            collection = embedding_service.statutes_collection
            # Get all document IDs
            result = collection.get()
            if result["ids"]:
                collection.delete(ids=result["ids"])
                print(f"Reset statutes database")
                if hasattr(embedding_service, '_save_collection_to_s3'):
                    embedding_service._save_collection_to_s3('statutes')
        except Exception as e:
            print(f"Error resetting statutes database: {e}")
        
    if db_type == 'regulations' or db_type == 'all':
        try:
            collection = embedding_service.regulations_collection
            # Get all document IDs
            result = collection.get()
            if result["ids"]:
                collection.delete(ids=result["ids"])
                print(f"Reset regulations database")
                if hasattr(embedding_service, '_save_collection_to_s3'):
                    embedding_service._save_collection_to_s3('regulations')
        except Exception as e:
            print(f"Error resetting regulations database: {e}")

def load_text_files(directory):
    """Load all text files from a directory and return their contents with metadata"""
    texts = []
    metadatas = []
    ids = []
    
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Error: Directory {dir_path} does not exist")
        return [], [], []
    
    file_count = 0
    for file_path in dir_path.glob("**/*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
                if text:
                    texts.append(text)
                    file_id = f"{file_path.stem}-{file_count}"
                    ids.append(file_id)
                    metadatas.append({
                        "source": str(file_path.relative_to(dir_path)),
                        "filename": file_path.name,
                        "file_path": str(file_path),
                        "file_type": "txt"
                    })
                    file_count += 1
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    
    print(f"Loaded {len(texts)} text files from {directory}")
    return texts, metadatas, ids

def ingest_case_law(directory=None):
    """Ingest case law documents into the vector database"""
    base_dir = Path(__file__).resolve().parent.parent
    if directory:
        source_dir = Path(directory)
    else:
        source_dir = base_dir / "data" / "raw_documents" / "case_law"
    
    if not source_dir.exists():
        print(f"Error: Directory {source_dir} does not exist")
        return False
    
    print(f"Ingesting case law documents from {source_dir}")
    texts, metadatas, ids = load_text_files(source_dir)
    
    if not texts:
        print("No documents found to ingest")
        return False
    
    # Import the documents
    documents_imported = vector_db_service.import_case_law(
        texts=texts,
        metadatas=metadatas,
        ids=ids
    )
    
    # Explicitly save to S3 after importing
    if hasattr(embedding_service, '_save_collection_to_s3'):
        embedding_service._save_collection_to_s3('case_law')
    
    # Print the result
    print(f"Ingestion complete. Successfully imported {documents_imported} documents.")
    
    # Print database stats
    stats = vector_db_service.get_stats()
    print(f"Case law database now contains {stats['case_law']['documents']} documents.")
    
    return documents_imported > 0

def ingest_statutes(directory=None):
    """Ingest statute documents into the vector database"""
    base_dir = Path(__file__).resolve().parent.parent
    if directory:
        source_dir = Path(directory)
    else:
        source_dir = base_dir / "data" / "raw_documents" / "statutes"
    
    if not source_dir.exists():
        print(f"Error: Directory {source_dir} does not exist")
        return False
    
    print(f"Ingesting statute documents from {source_dir}")
    texts, metadatas, ids = load_text_files(source_dir)
    
    if not texts:
        print("No documents found to ingest")
        return False
    
    # Import the documents
    documents_imported = vector_db_service.import_statutes(
        texts=texts,
        metadatas=metadatas,
        ids=ids
    )
    
    # Explicitly save to S3 after importing
    if hasattr(embedding_service, '_save_collection_to_s3'):
        embedding_service._save_collection_to_s3('statutes')
    
    # Print the result
    print(f"Ingestion complete. Successfully imported {documents_imported} documents.")
    
    # Print database stats
    stats = vector_db_service.get_stats()
    print(f"Statutes database now contains {stats['statutes']['documents']} documents.")
    
    return documents_imported > 0

def ingest_regulations(directory=None):
    """Ingest regulation documents into the vector database"""
    base_dir = Path(__file__).resolve().parent.parent
    if directory:
        source_dir = Path(directory)
    else:
        source_dir = base_dir / "data" / "raw_documents" / "regulations"
    
    if not source_dir.exists():
        print(f"Error: Directory {source_dir} does not exist")
        return False
    
    print(f"Ingesting regulation documents from {source_dir}")
    texts, metadatas, ids = load_text_files(source_dir)
    
    if not texts:
        print("No documents found to ingest")
        return False
    
    # Import the documents
    documents_imported = vector_db_service.import_regulations(
        texts=texts,
        metadatas=metadatas,
        ids=ids
    )
    
    # Explicitly save to S3 after importing
    if hasattr(embedding_service, '_save_collection_to_s3'):
        embedding_service._save_collection_to_s3('regulations')
    
    # Print the result
    print(f"Ingestion complete. Successfully imported {documents_imported} documents.")
    
    # Print database stats
    stats = vector_db_service.get_stats()
    print(f"Regulations database now contains {stats['regulations']['documents']} documents.")
    
    return documents_imported > 0

def force_s3_sync():
    """Force a sync with S3 for all collections"""
    print("Forcing sync with S3...")
    
    collections = ["case_law", "statutes", "regulations"]
    for collection_name in collections:
        if hasattr(embedding_service, '_save_collection_to_s3'):
            embedding_service._save_collection_to_s3(collection_name)
            print(f"Synced {collection_name} collection to S3")
        else:
            print(f"Warning: Embedding service doesn't have _save_collection_to_s3 method")
            break
    
    # Also use the S3 API endpoint if available
    try:
        import requests
        response = requests.post("http://localhost:5001/api/s3/sync")
        if response.status_code == 200:
            print("Called S3 sync endpoint successfully")
        else:
            print(f"Failed to call S3 sync endpoint: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error calling S3 sync endpoint: {e}")

def main():
    """Main entry point"""
    args = parse_args()
    
    # Reset databases if requested
    if args.reset:
        reset_database(args.source)
    
    # Ingest documents
    success = True
    if args.source == 'case_law' or args.source == 'all':
        success = ingest_case_law(args.directory) and success
    
    if args.source == 'statutes' or args.source == 'all':
        success = ingest_statutes(args.directory) and success
        
    if args.source == 'regulations' or args.source == 'all':
        success = ingest_regulations(args.directory) and success
    
    # Force a sync with S3 if requested
    if args.force_sync:
        force_s3_sync()
    
    # Print final status
    if success:
        print("Document ingestion completed successfully!")
    else:
        print("Document ingestion completed with errors.")
        sys.exit(1)

if __name__ == "__main__":
    main() 