#!/usr/bin/env python3
"""
Demo script for the web search and data pipeline integration.

This script demonstrates how to search the web for legal information,
download and process the content, and store it in the vector database.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import data pipeline and web search
from data_pipeline import DataPipeline
from data_pipeline.web_search import WebSearch

def search_and_process_query(query, collection, search_engine, max_results, follow_links):
    """Search for query and process results into vector database"""
    # Initialize data pipeline
    pipeline = DataPipeline()
    
    # Initialize web search with the pipeline
    web_search = WebSearch(data_pipeline=pipeline)
    
    # Print configuration
    print(f"\n{'='*80}")
    print(f"Web Search Demo: {query}")
    print(f"{'='*80}")
    print(f"Collection: {collection}")
    print(f"Search Engine: {search_engine}")
    print(f"Max Results: {max_results}")
    print(f"Follow Links: {follow_links}")
    print(f"{'-'*80}\n")
    
    # Perform search and process
    print(f"Searching for '{query}'...")
    result = web_search.search_and_process(
        query=query,
        collection=collection,
        search_engine=search_engine,
        max_results=max_results,
        max_depth=2 if follow_links else 1,
        follow_links=follow_links
    )
    
    # Print results
    print("\nSearch and Processing Complete!")
    print(f"{'-'*80}")
    print(f"URLs Found: {result['stats']['urls_found']}")
    print(f"Pages Scraped: {result['stats']['pages_scraped']}")
    print(f"Documents Processed: {result['stats']['documents_processed']}")
    
    # Analyze collection
    print("\nAnalyzing Collection...")
    analysis = pipeline.analyze_collection(collection)
    print(f"{'-'*80}")
    if "error" in analysis:
        print(f"Error: {analysis['error']}")
    else:
        print(f"Collection: {analysis['collection']}")
        print(f"Document Count: {analysis['document_count']}")
        
        if "document_types" in analysis and analysis["document_types"]:
            print("\nDocument Types:")
            for doc_type, count in analysis["document_types"].items():
                print(f"  - {doc_type}: {count}")
        
        if "metadata_coverage" in analysis and analysis["metadata_coverage"]:
            print("\nTop Metadata Fields:")
            sorted_metadata = sorted(
                analysis["metadata_coverage"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            for field, coverage in sorted_metadata:
                print(f"  - {field}: {coverage}%")
    
    return result

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Demo for web search and data pipeline integration")
    parser.add_argument("--query", type=str, required=True, 
                        help="Search query for legal information")
    parser.add_argument("--collection", type=str, default="web_search",
                        help="Collection name for storing documents")
    parser.add_argument("--search-engine", type=str, default="google_scholar",
                        choices=["google", "google_scholar"],
                        help="Search engine to use")
    parser.add_argument("--max-results", type=int, default=5,
                        help="Maximum number of search results to process")
    parser.add_argument("--follow-links", action="store_true",
                        help="Follow links on found pages")
    
    args = parser.parse_args()
    
    # Run the demo
    search_and_process_query(
        query=args.query,
        collection=args.collection,
        search_engine=args.search_engine,
        max_results=args.max_results,
        follow_links=args.follow_links
    )

if __name__ == "__main__":
    main() 