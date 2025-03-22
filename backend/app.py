from flask import Flask, request, jsonify
from services.vector_db_service import vector_db_service
from services.client_agent import client_agent
from services.research_agent import research_agent
from services.embedding_service import embedding_service, S3_ENABLED
import os

app = Flask(__name__)

@app.route('/api/search', methods=['POST'])
def search():
    """
    Search for similar documents in the vector database.
    
    POST request with JSON body:
    {
        "query": "Your search query",
        "collection": "case_law", // Optional, default is "case_law"
        "top_k": 5 // Optional, default is 5
    }
    """
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({"error": "Query is required"}), 400
    
    query = data['query']
    collection = data.get('collection', 'case_law')
    top_k = data.get('top_k', 5)
    
    # Validate collection name
    valid_collections = ['case_law', 'statutes', 'regulations']
    if collection not in valid_collections:
        return jsonify({
            "error": f"Invalid collection. Must be one of: {', '.join(valid_collections)}"
        }), 400
    
    try:
        results = vector_db_service.search(
            query=query,
            collection_name=collection,
            top_k=top_k
        )
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the vector databases."""
    try:
        stats = vector_db_service.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/client/understand', methods=['POST'])
def understand_client():
    """Process and understand a client query using Model A"""
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({"error": "Query is required"}), 400
    
    query = data['query']
    
    try:
        # Get understanding using client agent (Model A)
        understanding = client_agent.understand_query(query)
        
        return jsonify(understanding)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/research', methods=['POST'])
def research():
    """Conduct legal research using Model B (Legal Research Agent)"""
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({"error": "Query is required"}), 400
    
    query = data['query']
    collections = data.get('collections', None)  # Optional collections to search
    top_k = data.get('top_k', 3)  # Default to 3 results per collection
    
    try:
        # Conduct research using research agent (Model B)
        results = research_agent.conduct_research(
            query=query,
            collections=collections,
            top_k=top_k
        )
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/s3/sync', methods=['POST'])
def sync_with_s3():
    """
    Manually trigger synchronization with S3 storage
    
    POST request with optional JSON body:
    {
        "collection": "case_law" // Optional, if not provided all collections will be synced
    }
    """
    if not S3_ENABLED:
        return jsonify({
            "error": "S3 storage is not enabled. Set S3_ENABLED=True in .env"
        }), 400
    
    data = request.json or {}
    collection = data.get('collection')
    
    try:
        if collection:
            # Sync specific collection
            from services.s3_vector_store import s3_vector_store
            result = s3_vector_store.sync_collection(collection)
            return jsonify({
                "success": result,
                "collection": collection
            })
        else:
            # Sync all collections
            result = embedding_service.sync_all_with_s3()
            return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Home page with basic info."""
    endpoints = [
        {
            "path": "/api/search",
            "method": "POST",
            "description": "Search for similar documents"
        },
        {
            "path": "/api/stats",
            "method": "GET",
            "description": "Get statistics about the vector databases"
        },
        {
            "path": "/api/client/understand",
            "method": "POST",
            "description": "Process and understand a client query using Model A"
        },
        {
            "path": "/api/research",
            "method": "POST",
            "description": "Conduct legal research using Model B"
        }
    ]
    
    # Add S3 endpoints if enabled
    if S3_ENABLED:
        endpoints.append({
            "path": "/api/s3/sync",
            "method": "POST",
            "description": "Manually sync with S3 storage"
        })
    
    return jsonify({
        "message": "Legal AI API is running",
        "s3_enabled": S3_ENABLED,
        "endpoints": endpoints
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port) 