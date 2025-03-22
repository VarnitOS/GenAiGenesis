"""
Test script for the Legal Research Agent.
Tests the complete Model B workflow including vector search, web search, and research synthesis.
"""

import os
import sys
import json
import argparse
import logging
import tempfile
from datetime import datetime

# Set up path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Model B components
from models.cohere_chat import CohereChat
from models.research_synthesis import ResearchSynthesisChain
from data_pipeline.pipeline import DataPipeline
from data_pipeline.web_search import WebSearch

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_cohere_chat():
    """Test the Cohere Chat component."""
    logger.info("Testing Cohere Chat...")
    
    try:
        # Initialize Cohere Chat
        chat = CohereChat()
        
        # Test a simple query
        test_query = "What is the difference between state and federal courts?"
        
        logger.info(f"Sending test query: {test_query}")
        response = chat.generate_chat_message(test_query)
        
        logger.info(f"Response received. Tokens used: {response.get('tokens_used', {})}")
        print("\n=== Cohere Chat Response ===\n")
        print(response.get("text"))
        print("\n===========================\n")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Cohere Chat: {str(e)}")
        return False

def test_web_search(query="Fourth Amendment reasonable search"):
    """Test the Web Search component."""
    logger.info("Testing Web Search...")
    
    try:
        # Initialize Web Search
        web_search = WebSearch()
        
        # Test search
        logger.info(f"Searching for: {query}")
        search_results = web_search._search_google(query, max_results=3)
        
        if not search_results:
            logger.warning("No search results found")
            return False
        
        logger.info(f"Found {len(search_results)} search results")
        
        # Get content from first result
        first_result = search_results[0]
        logger.info(f"Getting content from URL: {first_result.get('url')}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            content_files = web_search._download_content(first_result.get('url'), temp_dir)
            if content_files:
                with open(content_files[0], 'r') as f:
                    content = f.read()
            else:
                content = ""
        
        if not content:
            logger.warning("No content extracted")
            return False
        
        # Print summary
        print("\n=== Web Search Results ===\n")
        for result in search_results:
            print(f"Title: {result.get('title')}")
            print(f"URL: {result.get('url')}")
            print(f"Snippet: {result.get('snippet', '')[:100]}...")
            print()
        
        print(f"Content excerpt from first result ({len(content)} chars):")
        print(content[:500] + "...")
        print("\n==========================\n")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Web Search: {str(e)}")
        return False

def test_research_synthesis(query="What are the elements of a valid contract?"):
    """Test the Research Synthesis component with sample documents."""
    logger.info("Testing Research Synthesis...")
    
    try:
        # Sample documents
        sample_docs = [
            {
                "text": "A contract is formed when there is an offer, acceptance of that offer, and consideration. "
                       "Courts have consistently held that all three elements must be present for a contract to be valid.",
                "metadata": {
                    "title": "Contract Law Fundamentals",
                    "type": "legal_document",
                    "date": "2022-01-15",
                    "jurisdiction": "General",
                    "source": "Legal Encyclopedia"
                }
            },
            {
                "text": "Consideration in contract law refers to what each party gives or promises in exchange. "
                       "Without consideration, a promise is generally not enforceable as a contract.",
                "metadata": {
                    "title": "Consideration in Contract Law",
                    "type": "case_law",
                    "date": "2019-03-22",
                    "jurisdiction": "Federal",
                    "source": "Legal Journal"
                }
            }
        ]
        
        # Initialize Research Synthesis
        cohere_chat = CohereChat()
        synthesis_chain = ResearchSynthesisChain(cohere_chat=cohere_chat)
        
        # Run synthesis
        logger.info(f"Running synthesis for query: {query}")
        result = synthesis_chain.synthesize_research(query=query, documents=sample_docs)
        
        # Print results
        print("\n=== Research Synthesis ===\n")
        print(f"Query: {query}")
        print("\nSynthesis:")
        print(result.get("synthesis"))
        
        print("\nSources:")
        for source in result.get("sources", []):
            print(f"- {source.get('title')} ({source.get('date')})")
            if source.get('key_points'):
                print("  Key points:")
                for point in source.get('key_points'):
                    print(f"  * {point}")
        
        print("\n=========================\n")
        
        # Clear S3 bucket after generating response
        try:
            from data_pipeline.cleanup import VectorDBCleanup
            cleanup = VectorDBCleanup()
            cleanup.clear_s3_bucket()
            logger.info("S3 bucket cleared after generating response")
        except Exception as e:
            logger.warning(f"Failed to clear S3 bucket: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Research Synthesis: {str(e)}")
        return False

def test_vector_search(query="Fourth Amendment rights", collection="case_law"):
    """Test vector search functionality."""
    logger.info("Testing Vector Search...")
    
    try:
        # Initialize Data Pipeline
        pipeline = DataPipeline()
        
        # Search for documents - use proper method based on your implementation
        logger.info(f"Searching for '{query}' in collection '{collection}'")
        
        # Try to get the vector db service from the pipeline
        if hasattr(pipeline, 'vector_db_service') and hasattr(pipeline.vector_db_service, 'search'):
            results = pipeline.vector_db_service.search(query, collection=collection, limit=5)
        else:
            # Fallback to using embedding service directly if available
            from services.embedding_service import embedding_service
            results = embedding_service.similarity_search(query, collection, top_k=5)
        
        if not results:
            logger.warning(f"No results found in collection {collection}")
            return False
        
        logger.info(f"Found {len(results)} results")
        
        # Print results
        print(f"\n=== Vector Search Results ({collection}) ===\n")
        for i, doc in enumerate(results):
            metadata = doc.get("metadata", {})
            text = doc.get("text", doc.get("document", ""))  # Try both field names
            print(f"Result {i+1}:")
            print(f"Title: {metadata.get('title', 'Untitled')}")
            print(f"Source: {metadata.get('source', 'Unknown')}")
            print(f"Date: {metadata.get('date', 'Unknown')}")
            print(f"Excerpt: {text[:200]}...")
            print()
        
        print("===============================\n")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Vector Search: {str(e)}")
        return False

def test_complete_workflow(query, use_web_search=True):
    """Test the complete Model B workflow."""
    logger.info("Testing complete Model B workflow...")
    logger.info(f"Query: {query}")
    
    try:
        # Initialize components
        cohere_chat = CohereChat()
        synthesis_chain = ResearchSynthesisChain(cohere_chat=cohere_chat)
        data_pipeline = DataPipeline()
        
        # Always use web search for more accurate results
        use_web_search = True
        web_search = WebSearch() if use_web_search else None
        
        # Step 1: Search vector database
        vector_results = []
        collections = ["case_law", "statutes", "regulations"]
        
        for collection in collections:
            try:
                # Try to get the vector db service from the pipeline
                if hasattr(data_pipeline, 'vector_db_service') and hasattr(data_pipeline.vector_db_service, 'search'):
                    results = data_pipeline.vector_db_service.search(query, collection=collection, limit=3)
                else:
                    # Fallback to using embedding service directly if available
                    from services.embedding_service import embedding_service
                    results = embedding_service.similarity_search(query, collection, top_k=3)
                
                if results:
                    vector_results.extend(results)
                    logger.info(f"Found {len(results)} results in collection {collection}")
            except Exception as e:
                logger.warning(f"Error searching collection {collection}: {str(e)}")
        
        # Step 2: Always perform web search for accurate information
        web_results = []
        if web_search:
            try:
                # Force web search for accurate information
                logger.info("Performing web search for accurate information")
                search_results = web_search._search_google(query, max_results=5)  # Increased from 3 to 5
                
                for result in search_results:
                    try:
                        logger.info(f"Processing web result: {result.get('url')}")
                        with tempfile.TemporaryDirectory() as temp_dir:
                            content_files = web_search._download_content(result.get('url'), temp_dir)
                            if content_files:
                                with open(content_files[0], 'r') as f:
                                    content = f.read()
                                    
                                # Process and add to results
                                doc = {
                                    "text": content,
                                    "metadata": {
                                        "title": result.get('title', 'Web Document'),
                                        "type": "web_content",
                                        "date": datetime.now().strftime("%Y-%m-%d"),
                                        "jurisdiction": "Unknown",
                                        "source": result.get('url'),
                                        "snippet": result.get('snippet', '')
                                    }
                                }
                                web_results.append(doc)
                                logger.info(f"Added web content from {result.get('url')}")
                    except Exception as e:
                        logger.warning(f"Error processing web result {result.get('url')}: {str(e)}")
                
                logger.info(f"Added {len(web_results)} web search results")
            except Exception as e:
                logger.warning(f"Error performing web search: {str(e)}")
        
        # Combine results - prioritize web results for up-to-date information
        all_documents = web_results + vector_results
        
        # Step 3: Synthesize research
        if all_documents:
            logger.info(f"Synthesizing research with {len(all_documents)} documents")
            synthesis_result = synthesis_chain.synthesize_research(
                query=query,
                documents=all_documents,
                user_context="This is a test of the Legal Research Agent workflow."
            )
            
            # Print results
            print("\n=== Complete Workflow Results ===\n")
            print(f"Query: {query}")
            print(f"Documents: {len(all_documents)} ({len(vector_results)} from vector DB, {len(web_results)} from web)")
            
            print("\nSynthesis:")
            print(synthesis_result.get("synthesis"))
            
            print("\nSources:")
            for source in synthesis_result.get("sources", []):
                print(f"- {source.get('title')} ({source.get('date')})")
                if source.get('key_points'):
                    print("  Key points:")
                    for point in source.get('key_points'):
                        print(f"  * {point}")
            
            # Save to file
            output_file = f"research_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(synthesis_result, f, indent=2)
            logger.info(f"Results saved to {output_file}")
            
            print(f"\nResults saved to {output_file}")
            print("\n===============================\n")
            
            # Clear S3 bucket after generating response
            try:
                from data_pipeline.cleanup import VectorDBCleanup
                cleanup = VectorDBCleanup()
                cleanup.clear_s3_bucket()
                logger.info("S3 bucket cleared after generating response")
            except Exception as e:
                logger.warning(f"Failed to clear S3 bucket: {str(e)}")
            
            return True
        else:
            logger.warning("No documents found for synthesis")
            
            # Fall back to Cohere Chat
            logger.info("Falling back to Cohere Chat")
            response = cohere_chat.generate_chat_message(
                message=f"Research Query: {query}\n\nI couldn't find any specific legal documents related to this query. Please provide a general response based on your knowledge.",
                system_prompt="You are a legal research assistant. The system couldn't find relevant documents for this query. Provide a helpful response based on general legal knowledge, but make it clear that you're not citing specific legal documents."
            )
            
            print("\n=== Fallback Chat Response ===\n")
            print(response.get("text"))
            print("\n=============================\n")
            
            return True
    except Exception as e:
        logger.error(f"Error testing complete workflow: {str(e)}")
        return False

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description='Test the Legal Research Agent')
    parser.add_argument('--component', choices=['chat', 'web', 'synthesis', 'vector', 'all', 'workflow'], 
                        default='workflow', help='Component to test')
    parser.add_argument('--query', type=str, default="What are the key elements of a valid contract?",
                        help='Query to use for testing')
    parser.add_argument('--collection', type=str, default="case_law",
                        help='Collection to search for vector tests')
    parser.add_argument('--no-web', action='store_true', help='Disable web search in workflow test')
    
    args = parser.parse_args()
    
    if args.component == 'chat':
        test_cohere_chat()
    elif args.component == 'web':
        test_web_search(query=args.query)
    elif args.component == 'synthesis':
        test_research_synthesis(query=args.query)
    elif args.component == 'vector':
        test_vector_search(query=args.query, collection=args.collection)
    elif args.component == 'workflow':
        test_complete_workflow(query=args.query, use_web_search=not args.no_web)
    else:  # 'all'
        print("Testing all components...\n")
        test_cohere_chat()
        test_web_search(query=args.query)
        test_research_synthesis(query=args.query)
        test_vector_search(query=args.query, collection=args.collection)
        test_complete_workflow(query=args.query, use_web_search=not args.no_web)

if __name__ == "__main__":
    main() 