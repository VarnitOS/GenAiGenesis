"""
Test script for the Legal Research Agent (Model B)
This script demonstrates how to use the research agent to conduct legal research.
"""

import sys
import os
import json
from time import time

# Add the parent directory to the path to import the services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.research_agent import research_agent

def test_research_agent():
    """Test the research agent with a sample query"""
    
    # Sample legal queries to test
    test_queries = [
        "What are the legal requirements for minimum wage in California?",
        "What are the tenant rights in New York for landlord entry?",
        "What are the requirements for forming an LLC in Delaware?",
        "What legal protections exist for whistleblowers in the financial industry?"
    ]
    
    # Select one query to test
    query = test_queries[0]
    
    print(f"\n🔍 Testing Research Agent with query: \"{query}\"\n")
    print("=" * 80)
    
    # Measure execution time
    start_time = time()
    
    # Run the research agent
    try:
        results = research_agent.conduct_research(
            query=query,
            collections=["statutes", "case_law"],
            top_k=2
        )
        
        # Calculate execution time
        execution_time = time() - start_time
        
        # Print results in a formatted way
        print(f"✅ Research completed in {execution_time:.2f} seconds\n")
        
        # Print research focus
        print("📊 RESEARCH FOCUS:")
        print("-" * 80)
        if isinstance(results["research_focus"], dict):
            for key, value in results["research_focus"].items():
                if isinstance(value, list):
                    print(f"{key.upper()}: {', '.join(value)}")
                else:
                    print(f"{key.upper()}: {value}")
        else:
            print(results["research_focus"])
        
        # Print vector search results
        print("\n📚 VECTOR DATABASE RESULTS:")
        print("-" * 80)
        if results["vector_results"]:
            for i, doc in enumerate(results["vector_results"]):
                print(f"Document {i+1}: {doc.get('metadata', {}).get('source', 'Unknown')}")
                print(f"Content: {doc['document'][:150]}...\n")
        else:
            print("No relevant documents found in vector database.")
        
        # Print internet results
        print("\n🌐 INTERNET RESULTS:")
        print("-" * 80)
        if results["internet_results"]:
            for i, result in enumerate(results["internet_results"]):
                print(f"Result {i+1}: {result['title']}")
                print(f"Source: {result['url']}")
                print(f"Excerpt: {result['snippet']}\n")
        else:
            print("No internet results. Make sure SERPAPI_KEY is configured correctly.")
        
        # Print synthesis
        print("\n🧠 RESEARCH SYNTHESIS:")
        print("-" * 80)
        print(results["synthesis"])
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        # Check if SERPAPI_KEY is missing
        if "SERPAPI_KEY environment variable not set" in str(e):
            print("\nTo fix this, add your SerpAPI key to the .env file:")
            print("SERPAPI_KEY=your_serpapi_key_here")
            print("\nGet a key at: https://serpapi.com/")
        
        # Check if COHERE_API_KEY is missing
        if "COHERE_API_KEY environment variable not set" in str(e):
            print("\nTo fix this, make sure your Cohere API key is in the .env file")

if __name__ == "__main__":
    test_research_agent() 