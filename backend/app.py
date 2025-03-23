from flask import Flask, request, jsonify, send_from_directory
from services.vector_db_service import vector_db_service
from services.client_agent import client_agent
from services.research_agent import research_agent
from services.embedding_service import embedding_service, S3_ENABLED
import os
import logging
from flask_cors import CORS
import cohere
from dotenv import load_dotenv

load_dotenv()    

# Import search override to ensure it patches the vector_db_service
from services import search_override
from services.client_agent import client_agent
from services.vector_db_service import vector_db_service
# Import document data for recreation
from scripts.fix_embeddings import CASE_LAW_DOCUMENTS, STATUTE_DOCUMENTS, REGULATION_DOCUMENTS



# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Cohere client
co = cohere.Client(os.environ.get('COHERE_API_KEY'))

# Enable CORS
CORS(app)

# Register blueprints

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


@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Welcome to the LegalMind AI API"
    })

@app.route('/test')
def test():
    return jsonify({
        "status": "success",
        "data": {
            "name": "LegalMind AI",
            "version": "0.1.0"
        }
    })

@app.route('/api/embed', methods=['POST'])
def embed_text():
    """Generate embeddings for the provided text"""
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: text"
            }), 400
        
        # Clean input text
        text = data['text'].strip()
        
        # Generate embeddings - Use model parameter correctly
        response = co.embed(
            texts=[text],
            model="embed-english-v3.0",  # Keep the model parameter but ensure text is clean
            input_type="search_query"
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "embeddings": response.embeddings[0][:10] + ["..."],  # Truncated for readability
                "model": "embed-english-v3.0"
            }
        })
    except Exception as e:
        logger.error(f"Error in /api/embed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate_text():
    """Generate text based on the provided prompt"""
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: prompt"
            }), 400
        
        # Clean input prompt
        prompt = data['prompt'].strip()
        
        # Set parameters with defaults
        max_tokens = int(data.get('max_tokens', 300))
        temperature = float(data.get('temperature', 0.7))
        
        # Generate text
        response = co.generate(
            prompt=prompt,
            model="command",
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "text": response.generations[0].text,
                "model": "command"
            }
        })
    except Exception as e:
        logger.error(f"Error in /api/generate: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/client/understand', methods=['POST'])
def understand_client():
    """Process and understand a client query"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: query"
            }), 400
        
        # Clean input query
        query = data['query'].strip()
        
        # Get understanding using client agent
        understanding = client_agent.understand_query(query)
        
        return jsonify({
            "query": understanding["original_query"],
            "analysis": understanding["analysis"],
            "embedding_sample": understanding["embeddings"]
        })
    except Exception as e:
        logger.error(f"Error in /api/client/understand: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/client/respond', methods=['POST'])
def respond_to_client():
    """Generate a response to a client query"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: query"
            }), 400
        
        # Clean input query
        query = data['query'].strip()
        
        # Get optional context
        context = data.get('context')
        if context:
            # Ensure context is a list and clean items
            if not isinstance(context, list):
                context = [context]
            context = [c.strip() for c in context]
        
        # Generate response using client agent
        response = client_agent.respond_to_client(query, context)
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in /api/client/respond: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Vector Database Endpoints

@app.route('/api/vector-db/stats', methods=['GET'])
def vector_db_stats():
    """Get statistics about the vector databases"""
    try:
        stats = vector_db_service.get_db_stats()
        return jsonify({
            "status": "success",
            "data": stats
        })
    except Exception as e:
        logger.error(f"Error in /api/vector-db/stats: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/vector-db/search/case-law', methods=['POST'])
def search_case_law():
    """Search the case law vector database"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: query"
            }), 400
        
        # Clean input query
        query = data['query'].strip()
        
        # Get optional parameters
        limit = int(data.get('limit', 5))
        filters = data.get('filters')
        
        # Search the case law database
        results = vector_db_service.search_case_law(
            query=query,
            limit=limit,
            filters=filters
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "query": query,
                "result_count": len(results),
                "results": results
            }
        })
    except Exception as e:
        logger.error(f"Error in /api/vector-db/search/case-law: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/vector-db/search/statutes', methods=['POST'])
def search_statutes():
    """Search the statutes vector database"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: query"
            }), 400
        
        # Clean input query
        query = data['query'].strip()
        
        # Get optional parameters
        limit = int(data.get('limit', 5))
        filters = data.get('filters')
        
        # Search the statutes database
        results = vector_db_service.search_statutes(
            query=query,
            limit=limit,
            filters=filters
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "query": query,
                "result_count": len(results),
                "results": results
            }
        })
    except Exception as e:
        logger.error(f"Error in /api/vector-db/search/statutes: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/vector-db/search', methods=['POST'])
def search_all():
    """Search both case law and statutes databases"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: query"
            }), 400
        
        # Clean input query
        query = data['query'].strip()
        
        # Get optional parameters
        limit = int(data.get('limit', 3))  # Lower default since searching both DBs
        filters = data.get('filters')
        
        # Search both databases
        case_law_results = vector_db_service.search_case_law(
            query=query,
            limit=limit,
            filters=filters.get('case_law') if filters else None
        )
        
        statute_results = vector_db_service.search_statutes(
            query=query,
            limit=limit,
            filters=filters.get('statutes') if filters else None
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "query": query,
                "case_law": {
                    "result_count": len(case_law_results),
                    "results": case_law_results
                },
                "statutes": {
                    "result_count": len(statute_results),
                    "results": statute_results
                }
            }
        })
    except Exception as e:
        logger.error(f"Error in /api/vector-db/search: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    # Get port from environment or use default
    # port = int(os.environ.get('PORT', 5000))
    port = int(os.environ.get('PORT', 8081))
    
    # Run app
    app.run(host='0.0.0.0', port=port) 