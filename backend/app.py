#!/usr/bin/env python3
"""
Legal Research API

This Flask application exposes the legal research pipeline as a REST API.
It processes legal queries through:
1. Client Understanding (Model A)
2. Legal Research (Model B)
3. Final Response Generation

Usage:
  python app.py
"""

import os
import json
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Check required environment variables
required_env_vars = ['COHERE_API_KEY', 'SERPAPI_KEY']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("Please set them in your .env file or export them in your shell.")
    exit(1)

# Import services
from services.client_agent import client_agent
from services.research_agent import research_agent
from services.vector_db_service import vector_db_service

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store in-memory results (in production, use a database)
query_results = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a legal query through the pipeline"""
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400
    
    query = data['query']
    query_id = f"query_{int(time.time())}"
    
    try:
        logger.info(f"Processing new query: '{query}'")
        
        # Start timing
        start_time = time.time()
        
        # Step 1: Client Understanding
        client_understanding = run_client_understanding(query)
        
        # Step 2: Legal Research
        research_results = run_legal_research(query)
        
        # Step 3: Generate Final Response
        final_response = generate_final_response(query, client_understanding, research_results)
        
        # Calculate timing
        execution_time = time.time() - start_time
        
        # Create complete result object
        result = {
            "query_id": query_id,
            "query": query,
            "client_understanding": client_understanding,
            "research": research_results,
            "final_response": final_response,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store result for later retrieval (keep this for persistence)
        query_results[query_id] = result
        
        # Save to file for persistence (keep this too)
        save_result_to_file(result)
        
        logger.info(f"Pipeline completed in {execution_time:.2f} seconds")
        
        # Format the final response as clean markdown before sending to frontend
        result = prepare_markdown_response(result)
        
        # Return the COMPLETE result to the client
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return jsonify({
            "query_id": query_id,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/results/<query_id>', methods=['GET'])
def get_result(query_id):
    """Get the detailed results for a specific query"""
    if query_id not in query_results:
        # Try to load from file if not in memory
        try:
            result = load_result_from_file(query_id)
            if result:
                return jsonify(result)
        except:
            pass
            
        return jsonify({"error": "Query ID not found"}), 404
    
    return jsonify(query_results[query_id])

@app.route('/api/vector-search', methods=['POST'])
def vector_search():
    """Search the vector database directly"""
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400
    
    query = data['query']
    limit = data.get('limit', 5)
    
    try:
        # Use vector_db_service to search
        results = vector_db_service.search(query, limit=limit)
        return jsonify({"results": results})
        
    except Exception as e:
        logger.error(f"Error in vector search: {str(e)}")
        return jsonify({"error": str(e)}), 500

def run_client_understanding(query):
    """Run the client understanding agent (Model A)"""
    try:
        # The client agent might return different formats, handle both possibilities
        understanding = client_agent.understand_query(query)
        
        # Check if understanding is a string (error message)
        if isinstance(understanding, str):
            return {"error": understanding}
            
        # If it's a dict with these keys, it's the standard response format
        if isinstance(understanding, dict) and all(key in understanding for key in ["original_query", "analysis"]):
            return understanding
            
        # Otherwise wrap it in a standard format
        return {
            "original_query": query,
            "analysis": understanding
        }
    except Exception as e:
        logger.error(f"Error in client understanding: {str(e)}")
        return {"error": str(e)}

def run_legal_research(query):
    """Run the legal research agent (Model B)"""
    try:
        logger.info(f"Starting research for query: {query}")
        
        # Use a try/except block specifically for the research_agent call
        try:
            research = research_agent.conduct_research(query)
            logger.info("Research agent returned successfully")
            
            # Validate the research result structure
            if not isinstance(research, dict):
                logger.warning(f"Warning: research_agent returned non-dict type: {type(research)}")
                return {"error": f"Invalid research result type: {type(research)}"}
            
            # Check for critical fields
            vector_results = research.get('vector_results', [])
            internet_results = research.get('internet_results', [])
            synthesis = research.get('synthesis', '')
            
            logger.info(f"Vector results: {len(vector_results)}, Internet results: {len(internet_results)}")
            logger.info(f"Synthesis length: {len(synthesis)}")
            
            return research
            
        except Exception as inner_e:
            logger.error(f"Inner exception in research agent: {str(inner_e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": f"Research agent error: {str(inner_e)}"}
            
    except Exception as e:
        logger.error(f"Error in legal research: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}

def generate_final_response(query, client_understanding, research_results):
    """Generate the final response by combining client understanding and research"""
    try:
        # Extract analysis from client understanding
        analysis = client_understanding.get("analysis", "")
        
        # Extract primary concerns - handle both string and dict formats
        if isinstance(analysis, dict) and "primary_concerns" in analysis:
            primary_concerns = ", ".join(analysis.get("primary_concerns", []))
        else:
            # Try to extract concerns from text analysis
            primary_concerns = "understanding legal requirements"
        
        # Get research synthesis
        synthesis = research_results.get("synthesis", "")
        
        # Create a context that combines the research and understanding
        combined_context = f"""
Client Query: {query}

Primary Client Concerns: {primary_concerns}

Legal Research Findings:
{synthesis}
        """
        
        # Generate response
        try:
            response = client_agent.respond_to_client(query, [combined_context])
            return response
        except Exception as e:
            logger.error(f"Error from client agent: {str(e)}")
            # Fallback to simple format if client agent fails
            return {
                "response": f"Based on our research: {synthesis[:500]}..."
            }
            
    except Exception as e:
        logger.error(f"Error generating final response: {str(e)}")
        return {"error": str(e)}

def save_result_to_file(result):
    """Save a result to a JSON file for persistence"""
    try:
        # Create directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        
        query_id = result["query_id"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/{query_id}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
            
        logger.info(f"Saved result to {filename}")
        
    except Exception as e:
        logger.error(f"Error saving result to file: {str(e)}")

def load_result_from_file(query_id):
    """Try to load a result from a JSON file"""
    try:
        # Find files matching the query ID pattern
        import glob
        files = glob.glob(f"results/{query_id}_*.json")
        
        if not files:
            return None
            
        # Use the most recent file
        filename = sorted(files)[-1]
        
        with open(filename, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Error loading result from file: {str(e)}")
        return None

def prepare_markdown_response(result):
    """Format the final response as clean markdown before sending to frontend."""
    if not result:
        return result
        
    # Check if final_response exists and is a dictionary
    if 'final_response' not in result:
        return result
    
    # If final_response is already a dictionary, return as is
    if isinstance(result['final_response'], dict):
        return result
    
    # Only process if final_response is a string
    response_text = result['final_response']
    if not isinstance(response_text, str):
        return result
    
    # Now that we're sure it's a string, we can proceed with formatting
    # Remove any trailing ellipses and complete sentences
    if response_text.strip().endswith('...'):
        response_text = response_text.strip()[:-3] + '.'
    
    # Clean up formatting artifacts
    # Remove excess asterisks but preserve proper markdown
    response_text = re.sub(r'\*\*([^*]+)\*\*\*+:\*\*', r'**\1:** ', response_text)
    response_text = re.sub(r'\*{3,}', '', response_text)
    
    # Ensure proper headings
    response_text = re.sub(r'##(?=\S)', r'## ', response_text)
    
    # Ensure proper list formatting with newlines
    response_text = re.sub(r'(\n\s*-\s+)', r'\n\n- ', response_text)
    
    # Cleanup any broken markdown
    response_text = re.sub(r'\|\|', '', response_text)
    
    result['final_response'] = response_text
    return result

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    logger.info(f"Starting Legal Research API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)  