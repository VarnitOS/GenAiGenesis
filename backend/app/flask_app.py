from flask import Flask, jsonify, request
import os
import sys
import cohere

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration for dotenv
from dotenv import load_dotenv
load_dotenv()

# Import services
from services.client_agent import client_agent

# Initialize Cohere client
co = cohere.Client(os.environ.get('COHERE_API_KEY'))

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Legal AI Assistant API"})

@app.route('/test')
def test():
    return jsonify({"status": "success", "data": {"name": "LegalMind AI", "version": "0.1.0"}})

@app.route('/api/embed', methods=['POST'])
def embed():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        # Generate embedding
        response = co.embed(texts=[data['text']], model="embed-english-v3.0", input_type="search_query")
        # Return the first embedding
        return jsonify({"embedding": response.embeddings[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400
    
    try:
        # Generate text
        response = co.generate(
            prompt=data['prompt'],
            model="command",
            max_tokens=data.get('max_tokens', 150),
            temperature=data.get('temperature', 0.7)
        )
        # Return the generated text
        return jsonify({"text": response.generations[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/client/understand', methods=['POST'])
def understand_client():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Use the client agent to understand the query
        understanding = client_agent.understand_query(data['query'])
        return jsonify({
            "query": understanding["original_query"],
            "analysis": understanding["analysis"],
            "embedding_sample": understanding["embeddings"]  # Sample of embeddings
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/client/respond', methods=['POST'])
def respond_to_client():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Get optional context if provided
        context = data.get('context', None)
        
        # Use the client agent to respond to the query
        response = client_agent.respond_to_client(data['query'], context)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 