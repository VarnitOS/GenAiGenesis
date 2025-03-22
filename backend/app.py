from flask import Flask, request, jsonify, send_from_directory
from services.vector_db_service import vector_db_service
from services.client_agent import client_agent
from services.research_agent import research_agent
from services.embedding_service import embedding_service, S3_ENABLED
import os
import logging
from flask_cors import CORS

# Import search override to ensure it patches the vector_db_service
from services import search_override

# Import document data for recreation
from scripts.fix_embeddings import CASE_LAW_DOCUMENTS, STATUTE_DOCUMENTS, REGULATION_DOCUMENTS

# Import blueprints
from api.cleanup import cleanup_bp
from api.research_agent import research_agent_bp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS
CORS(app)

# Register blueprints
app.register_blueprint(cleanup_bp)
app.register_blueprint(research_agent_bp)

# Adding manual CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def recreate_collection(collection_name):
    """Recreate a collection with proper embeddings"""
    print(f"Recreating {collection_name} collection")
    
    try:
        # Choose the correct collection and documents
        if collection_name == "case_law":
            collection_obj = embedding_service.case_law_collection
            docs_data = CASE_LAW_DOCUMENTS
        elif collection_name == "statutes":
            collection_obj = embedding_service.statutes_collection
            docs_data = STATUTE_DOCUMENTS
        elif collection_name == "regulations":
            collection_obj = embedding_service.regulations_collection
            docs_data = REGULATION_DOCUMENTS
        else:
            raise ValueError(f"Unknown collection: {collection_name}")
        
        # Try to delete the collection (may fail if it doesn't exist)
        try:
            collection_obj.delete(where={"_id": {"$exists": True}})
        except Exception as e:
            print(f"Error deleting collection: {e}")
        
        # Prepare data
        documents = [doc["document"] for doc in docs_data]
        metadatas = [doc["metadata"] for doc in docs_data]
        ids = [doc["id"] for doc in docs_data]
        
        # Generate embeddings the same way
        embeddings = embedding_service.generate_embeddings(documents)
        
        # Add documents with embeddings
        collection_obj.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to {collection_name} collection")
        return True
    except Exception as e:
        print(f"Error recreating collection: {e}")
        return False

@app.route('/api/search', methods=['POST'])
def search():
    """Search the vector database"""
    try:
        data = request.json
        query = data.get('query', '')
        collection = data.get('collection', 'case_law')
        top_k = int(data.get('top_k', 5))
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embeddings([query])[0]
        
        # Get the appropriate collection
        if collection == "case_law":
            collection_obj = embedding_service.case_law_collection
        elif collection == "statutes":
            collection_obj = embedding_service.statutes_collection
        elif collection == "regulations":
            collection_obj = embedding_service.regulations_collection
        else:
            return jsonify({"error": f"Unknown collection: {collection}"}), 400
        
        # Check if collection has documents
        try:
            data = collection_obj.get()
            if len(data.get('ids', [])) == 0:
                # Collection is empty, recreate it
                success = recreate_collection(collection)
                if not success:
                    return jsonify({"error": f"Failed to recreate {collection} collection"}), 500
        except Exception as e:
            print(f"Error checking collection: {e}")
            # Try to recreate the collection
            success = recreate_collection(collection)
            if not success:
                return jsonify({"error": f"Failed to recreate {collection} collection"}), 500
        
        # Try direct search with the collection
        try:
            results = collection_obj.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results and 'ids' in results and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i] if 'documents' in results and results['documents'][0] else "",
                        "metadata": results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'][0] else {}
                    }
                    formatted_results.append(result)
            
            return jsonify({
                "query": query,
                "results": formatted_results
            })
        except Exception as e:
            error_msg = str(e).lower()
            # If we encounter a dimension mismatch, try to recreate the collection
            if "dimension" in error_msg and "match" in error_msg:
                print(f"Dimension mismatch detected. Recreating collection.")
                success = recreate_collection(collection)
                if not success:
                    return jsonify({"error": f"Failed to recreate {collection} collection"}), 500
                
                # Retry the search
                try:
                    results = collection_obj.query(
                        query_embeddings=[query_embedding],
                        n_results=top_k
                    )
                    
                    # Format results
                    formatted_results = []
                    if results and 'ids' in results and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
                        for i in range(len(results['ids'][0])):
                            result = {
                                "id": results['ids'][0][i],
                                "document": results['documents'][0][i] if 'documents' in results and results['documents'][0] else "",
                                "metadata": results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'][0] else {}
                            }
                            formatted_results.append(result)
                    
                    return jsonify({
                        "query": query,
                        "results": formatted_results
                    })
                except Exception as new_e:
                    return jsonify({"error": str(new_e)}), 500
            
            # For other errors, just return the error message
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the vector database"""
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
def sync_s3():
    """Force synchronization with S3"""
    try:
        if hasattr(embedding_service, 'sync_all_with_s3'):
            success = embedding_service.sync_all_with_s3()
        else:
            from services.s3_vector_store import s3_vector_store
            success = s3_vector_store.sync_all_collections()
        
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Home page redirects to the API documentation"""
    return send_from_directory('static', 'index.html')

# Health check
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy'
    })

# Error handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': str(error)
    }), 404

# Error handler
@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({
        'error': 'Server error',
        'message': str(error)
    }), 500

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run app
    app.run(host='0.0.0.0', port=port) 