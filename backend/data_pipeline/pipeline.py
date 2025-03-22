#!/usr/bin/env python3
"""
Core data pipeline for processing, embedding and storing legal documents.

This module provides the main DataPipeline class that orchestrates the entire
data flow from document ingestion to searchable vector embeddings.
"""

import os
import sys
import time
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import concurrent.futures
from functools import partial

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services
from services.embedding_service import embedding_service
from services.vector_db_service import vector_db_service

# Import pipeline components
from .processor import DocumentProcessor
from .embeddings import EmbeddingGenerator
from .metadata import MetadataExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("DataPipeline")

class DataPipeline:
    """
    Main pipeline for processing, embedding, and storing legal documents
    
    The pipeline handles the entire flow:
    1. Document processing - extract and preprocess text
    2. Metadata extraction - extract structured metadata
    3. Embedding generation - create vector embeddings
    4. Storage - store in ChromaDB with S3 sync
    5. Monitoring - track pipeline metrics
    
    Usage:
        pipeline = DataPipeline()
        pipeline.process_documents(
            source_dir="data/raw/case_law",
            collection="case_law",
            batch_size=10
        )
    """
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.metadata_extractor = MetadataExtractor()
        
        # Statistics tracking
        self.stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None,
            "errors": [],
            "collections": {}
        }
    
    def process_documents(self, source_dir: Union[str, Path], collection: str, 
                          batch_size: int = 10, max_workers: int = 4,
                          recursive: bool = True) -> Dict[str, Any]:
        """
        Process all documents in a directory and add them to a collection
        
        Args:
            source_dir: Directory containing documents
            collection: Name of the collection to add to
            batch_size: Number of documents to process in one batch
            max_workers: Maximum number of concurrent workers
            recursive: Whether to search subdirectories
            
        Returns:
            Statistics about the processing
        """
        source_dir = Path(source_dir)
        if not source_dir.exists():
            logger.error(f"Source directory {source_dir} does not exist")
            return {"error": f"Source directory {source_dir} does not exist"}
        
        # Reset statistics
        self.stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "errors": [],
            "collections": {collection: {"documents": 0, "embeddings": 0}}
        }
        
        logger.info(f"Starting pipeline for {source_dir} -> {collection}")
        
        # Find all files
        pattern = "**/*" if recursive else "*"
        all_files = list(source_dir.glob(pattern))
        files = [f for f in all_files if f.is_file() and f.suffix.lower() in self.document_processor.supported_extensions]
        
        logger.info(f"Found {len(files)} supported files out of {len(all_files)} total files")
        
        # Process files in batches
        batches = [files[i:i+batch_size] for i in range(0, len(files), batch_size)]
        
        for batch_num, batch in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} files)")
            
            # Process batch
            batch_results = self._process_batch(batch, collection, max_workers)
            
            # Update statistics
            self.stats["processed"] += len(batch)
            self.stats["succeeded"] += batch_results["succeeded"]
            self.stats["failed"] += batch_results["failed"]
            self.stats["errors"].extend(batch_results["errors"])
            self.stats["collections"][collection]["documents"] += batch_results["succeeded"]
            self.stats["collections"][collection]["embeddings"] += batch_results["succeeded"]
            
            # Save intermediate statistics
            self._save_stats(collection)
        
        # Update final statistics
        self.stats["end_time"] = datetime.now().isoformat()
        self._save_stats(collection)
        
        # Sync with S3 if available
        if hasattr(embedding_service, 'sync_all_with_s3'):
            logger.info("Syncing with S3...")
            embedding_service.sync_all_with_s3()
        
        logger.info(f"Pipeline completed: {self.stats['succeeded']} succeeded, {self.stats['failed']} failed")
        return self.stats
    
    def _process_batch(self, files: List[Path], collection: str, max_workers: int) -> Dict[str, Any]:
        """Process a batch of files"""
        batch_results = {
            "succeeded": 0,
            "failed": 0,
            "errors": []
        }
        
        # Prepare batch data
        documents = []
        metadatas = []
        ids = []
        
        # Process files with ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            process_func = partial(self._process_file, collection=collection)
            futures = {executor.submit(process_func, file): file for file in files}
            
            for future in concurrent.futures.as_completed(futures):
                file = futures[future]
                try:
                    result = future.result()
                    if result["success"]:
                        documents.append(result["document"])
                        metadatas.append(result["metadata"])
                        ids.append(result["id"])
                        batch_results["succeeded"] += 1
                    else:
                        batch_results["failed"] += 1
                        batch_results["errors"].append({
                            "file": str(file),
                            "error": result["error"]
                        })
                except Exception as e:
                    logger.error(f"Error processing {file}: {e}")
                    batch_results["failed"] += 1
                    batch_results["errors"].append({
                        "file": str(file),
                        "error": str(e)
                    })
        
        # Add documents to collection
        if documents:
            try:
                if collection == "case_law":
                    vector_db_service.import_case_law(
                        texts=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                elif collection == "statutes":
                    vector_db_service.import_statutes(
                        texts=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                elif collection == "regulations":
                    vector_db_service.import_regulations(
                        texts=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                else:
                    logger.error(f"Unknown collection: {collection}")
                    batch_results["failed"] += len(documents)
                    batch_results["succeeded"] -= len(documents)
                    batch_results["errors"].append({
                        "error": f"Unknown collection: {collection}"
                    })
            except Exception as e:
                logger.error(f"Error adding documents to collection {collection}: {e}")
                batch_results["failed"] += len(documents)
                batch_results["succeeded"] -= len(documents)
                batch_results["errors"].append({
                    "error": f"Error adding documents to collection {collection}: {e}"
                })
        
        return batch_results
    
    def _process_file(self, file_path: Path, collection: str) -> Dict[str, Any]:
        """Process a single file"""
        try:
            # Extract text and metadata
            text, extracted_metadata = self.document_processor.process(file_path)
            
            # Check if document extraction succeeded
            if not text:
                return {
                    "success": False,
                    "error": "Failed to extract text from file"
                }
            
            # Enrich metadata
            metadata = self.metadata_extractor.extract(text, extracted_metadata, collection)
            
            # Generate document ID
            doc_id = self._generate_document_id(file_path, metadata, collection)
            
            return {
                "success": True,
                "document": text,
                "metadata": metadata,
                "id": doc_id
            }
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_document_id(self, file_path: Path, metadata: Dict[str, Any], collection: str) -> str:
        """Generate a unique ID for a document"""
        # Use content hash if available
        if "content_hash" in metadata:
            return f"{collection}_{metadata['content_hash'][:10]}"
        
        # Otherwise, use file path and modification time
        file_hash = hashlib.md5(str(file_path).encode('utf-8')).hexdigest()[:10]
        mod_time = int(file_path.stat().st_mtime)
        return f"{collection}_{file_hash}_{mod_time}"
    
    def _save_stats(self, collection: str):
        """Save pipeline statistics"""
        stats_dir = "pipeline_stats"
        os.makedirs(stats_dir, exist_ok=True)
        
        # Save both collection-specific and overall stats
        filename = f"pipeline_stats_{collection}_{datetime.now().strftime('%Y%m%d')}.json"
        stats_path = os.path.join(stats_dir, filename)
        
        with open(stats_path, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def analyze_collection(self, collection: str) -> Dict[str, Any]:
        """
        Analyze a collection for quality and consistency
        
        Args:
            collection: Name of collection to analyze
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing collection {collection}")
        
        try:
            # Get collection
            collection_obj = None
            if collection == "case_law":
                collection_obj = embedding_service.case_law_collection
            elif collection == "statutes":
                collection_obj = embedding_service.statutes_collection
            elif collection == "regulations":
                collection_obj = embedding_service.regulations_collection
            else:
                logger.error(f"Unknown collection: {collection}")
                return {"error": f"Unknown collection: {collection}"}
            
            # Get collection data
            data = collection_obj.get()
            
            # Analyze collection
            analysis = {
                "collection": collection,
                "document_count": len(data.get("ids", [])),
                "embedding_dimensions": len(data.get("embeddings", [[]])[0]) if data.get("embeddings") and data.get("embeddings")[0] else 0,
                "document_types": {},
                "metadata_coverage": {},
                "embedding_stats": {},
                "recommendations": []
            }
            
            # Analyze document types and metadata
            if "metadatas" in data and data["metadatas"]:
                metadata_fields = set()
                for metadata in data["metadatas"]:
                    if metadata:
                        # Track document type
                        doc_type = metadata.get("document_type", "unknown")
                        analysis["document_types"][doc_type] = analysis["document_types"].get(doc_type, 0) + 1
                        
                        # Track metadata fields
                        for field in metadata:
                            metadata_fields.add(field)
                
                # Calculate metadata coverage
                for field in metadata_fields:
                    coverage = sum(1 for m in data["metadatas"] if m and field in m)
                    analysis["metadata_coverage"][field] = round(coverage / len(data["metadatas"]) * 100, 2)
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing collection {collection}: {e}")
            return {"error": str(e)}

# For command-line usage
def main():
    """Command line entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data pipeline for vector search engine')
    parser.add_argument('--source-dir', type=str, required=True,
                        help='Directory containing documents to process')
    parser.add_argument('--collection', choices=['case_law', 'statutes', 'regulations'], required=True,
                        help='Collection to add documents to')
    parser.add_argument('--batch-size', type=int, default=10,
                        help='Number of documents to process in one batch')
    parser.add_argument('--max-workers', type=int, default=4,
                        help='Maximum number of concurrent workers')
    parser.add_argument('--recursive', action='store_true',
                        help='Search subdirectories for documents')
    parser.add_argument('--analyze', action='store_true',
                        help='Analyze collection instead of processing documents')
    
    args = parser.parse_args()
    pipeline = DataPipeline()
    
    if args.analyze:
        # Analyze collection
        analysis = pipeline.analyze_collection(args.collection)
        print(json.dumps(analysis, indent=2))
    else:
        # Process documents
        stats = pipeline.process_documents(
            source_dir=args.source_dir,
            collection=args.collection,
            batch_size=args.batch_size,
            max_workers=args.max_workers,
            recursive=args.recursive
        )
        print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main() 