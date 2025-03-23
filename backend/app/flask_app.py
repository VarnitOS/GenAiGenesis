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
# Import the vector database service
from services.vector_db_service import vector_db_service

# Initialize the Flask app
app = Flask(__name__)

# Initialize Cohere client
co = cohere.Client(os.environ.get('COHERE_API_KEY'))



if __name__ == '__main__':
    # Get port from environment variable with fallback to 8081 to avoid conflicts
    port = int(os.environ.get('PORT', 8081))
    
    # Log the configuration
    logger.info(f"Starting LegalMind AI API on port {port}")
    logger.info(f"Redis config: host={os.environ.get('REDIS_HOST', 'localhost')}, port={os.environ.get('REDIS_PORT', 6379)}")

    app.run(debug=True, host='0.0.0.0', port=port) 