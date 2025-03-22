#!/usr/bin/env python3
"""
Test script for the data pipeline.

This script demonstrates how to use the data pipeline to process legal documents
and store their embeddings in a vector database.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import data pipeline
from data_pipeline import DataPipeline

def create_test_documents(output_dir: str, num_docs: int = 3) -> None:
    """Create test documents for pipeline testing"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Sample court case text
    case_text = """
    SUPREME COURT OF THE UNITED STATES
    
    ACME CORPORATION v. SMITH ENTERPRISES
    
    Decided: January 15, 2023
    
    JUSTICE ROBERTS delivered the opinion of the Court.
    
    This case concerns the interpretation of Section 230 of the Communications Decency Act. 
    The question presented is whether an internet platform can be held liable for content 
    created by its users when the platform has used algorithmic processes to promote that content.
    
    We hold that Section 230 immunity applies even when a platform uses algorithms to recommend content, 
    so long as the underlying content was created by a third party. The judgment of the Court of Appeals 
    is affirmed.
    
    Citation: 590 U.S. 45 (2023)
    """
    
    # Sample statute text
    statute_text = """
    TITLE 15 - COMMERCE AND TRADE
    
    SECTION 45 - UNFAIR METHODS OF COMPETITION UNLAWFUL; PREVENTION BY COMMISSION
    
    (a) Declaration of unlawfulness; power to prohibit unfair practices
    (1) Unfair methods of competition in or affecting commerce, and unfair or deceptive acts 
    or practices in or affecting commerce, are hereby declared unlawful.
    
    (2) The Commission is hereby empowered and directed to prevent persons, partnerships, or 
    corporations from using unfair methods of competition in or affecting commerce and unfair 
    or deceptive acts or practices in or affecting commerce.
    
    Effective Date: January 1, 1914
    """
    
    # Sample regulation text
    regulation_text = """
    TITLE 12 - BANKS AND BANKING
    
    CHAPTER II - FEDERAL RESERVE SYSTEM
    
    PART 226 - TRUTH IN LENDING (REGULATION Z)
    
    § 226.1 Authority, purpose, coverage, organization, enforcement, and liability.
    
    (a) Authority. This regulation, known as Regulation Z, is issued by the Board of Governors 
    of the Federal Reserve System to implement the Federal Truth in Lending Act, which is 
    contained in title I of the Consumer Credit Protection Act, as amended (15 U.S.C. 1601 et seq.).
    
    AGENCY: Federal Reserve System
    """
    
    # Create test files
    for i in range(num_docs):
        # Case law document
        with open(os.path.join(output_dir, f"case_{i}.txt"), "w") as f:
            f.write(case_text.replace("ACME CORPORATION", f"COMPANY {i}"))
        
        # Statute document
        with open(os.path.join(output_dir, f"statute_{i}.txt"), "w") as f:
            f.write(statute_text.replace("SECTION 45", f"SECTION {45 + i}"))
        
        # Regulation document
        with open(os.path.join(output_dir, f"regulation_{i}.txt"), "w") as f:
            f.write(regulation_text.replace("PART 226", f"PART {226 + i}"))
    
    print(f"Created {num_docs * 3} test documents in {output_dir}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test the legal document data pipeline")
    parser.add_argument("--create-test-docs", action="store_true", 
                        help="Create test documents before processing")
    parser.add_argument("--test-dir", type=str, default="test_docs",
                        help="Directory for test documents")
    parser.add_argument("--collection", type=str, default="test_collection",
                        help="Collection name for test documents")
    parser.add_argument("--analyze", action="store_true",
                        help="Analyze collection after processing")
    
    args = parser.parse_args()
    
    # Create test documents if requested
    if args.create_test_docs:
        create_test_documents(args.test_dir)
    
    # Initialize pipeline
    pipeline = DataPipeline()
    
    # Process documents
    print(f"Processing documents from {args.test_dir} into collection {args.collection}")
    stats = pipeline.process_documents(
        source_dir=args.test_dir,
        collection=args.collection,
        batch_size=5,
        recursive=True
    )
    
    # Print statistics
    print("\nProcessing Statistics:")
    print(f"Processed: {stats['processed']} documents")
    print(f"Succeeded: {stats['succeeded']} documents")
    print(f"Failed: {stats['failed']} documents")
    print(f"Time: {stats['start_time']} to {stats['end_time']}")
    
    # Analyze collection if requested
    if args.analyze:
        print("\nAnalyzing collection...")
        analysis = pipeline.analyze_collection(args.collection)
        print(json.dumps(analysis, indent=2))

if __name__ == "__main__":
    main() 