from flask import Flask, request, jsonify
import os
import cohere
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import the client agent
from services.client_agent import client_agent

# Initialize the Flask app
app = Flask(__name__)

# Initialize Cohere client
co = cohere.Client(os.environ.get('COHERE_API_KEY'))

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

if __name__ == '__main__':
    # Get port from environment variable with fallback to 8081 to avoid conflicts
    port = int(os.environ.get('PORT', 8081))
    
    # Log the configuration
    logger.info(f"Starting LegalMind AI API on port {port}")
    logger.info(f"Redis config: host={os.environ.get('REDIS_HOST', 'localhost')}, port={os.environ.get('REDIS_PORT', 6379)}")

    app.run(debug=True, host='0.0.0.0', port=port) 