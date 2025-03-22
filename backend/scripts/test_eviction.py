#!/usr/bin/env python3
"""
Test script for tenant eviction scenario with the research agent.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Set up path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Model B components
from models.cohere_chat import CohereChat
from models.research_synthesis import ResearchSynthesisChain
from services.research_agent import LegalResearchAgent, LegalWebSearch
from data_pipeline.cleanup import VectorDBCleanup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_eviction_query():
    """Test the research agent with a tenant eviction query."""
    query = "I'm a tenant facing eviction because my landlord claims my apartment violates health codes, but the issues are actually maintenance problems that I've repeatedly reported and the landlord has neglected. What are my legal rights and defenses?"
    
    logger.info(f"Testing research agent with eviction query: {query}")
    
    try:
        # Initialize research agent
        research_agent = LegalResearchAgent()
        
        # Verify web search is enabled
        if not research_agent.web_search_enabled:
            logger.error("Web search is not enabled. This test requires web search.")
            return False
        
        # Run research
        logger.info("Running research...")
        result = research_agent.conduct_research(query=query)
        
        # Print results
        print("\n=== Tenant Eviction Query Results ===\n")
        print(f"Query: {query}")
        print(f"Web results: {len(result.get('internet_results', []))}")
        print(f"Vector DB results: {len(result.get('vector_results', []))}")
        
        print("\nSynthesis:")
        print(result.get("synthesis", "No synthesis generated"))
        
        print("\nWeb Sources:")
        for i, source in enumerate(result.get("internet_results", [])):
            print(f"{i+1}. {source.get('title')} - {source.get('url')}")
        
        # Save result to file
        output_file = f"eviction_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Results saved to {output_file}")
        
        print(f"\nResults saved to {output_file}")
        print("\n============================\n")
        
        return True
    except Exception as e:
        logger.error(f"Error testing eviction query: {str(e)}")
        return False

def main():
    """Main function."""
    # Test eviction query
    result = test_eviction_query()
    
    # Always clean up S3 bucket at the end
    try:
        logger.info("Cleaning up S3 bucket...")
        cleanup = VectorDBCleanup()
        deleted_objects = cleanup.clear_s3_bucket()
        logger.info(f"Deleted {len(deleted_objects)} objects from S3 bucket")
    except Exception as e:
        logger.error(f"Error cleaning up S3 bucket: {str(e)}")
    
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main()) 