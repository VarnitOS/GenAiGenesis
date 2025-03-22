"""
API endpoints for the Legal Research Agent.
Handles document lookup, web search, and research synthesis.
"""

import os
import json
import logging
import traceback
from typing import List, Dict, Any, Optional
from flask import Blueprint, request, jsonify
from datetime import datetime

# Import Model B components
from ..models.cohere_chat import CohereChat
from ..models.research_synthesis import ResearchSynthesisChain
from ..data_pipeline.pipeline import DataPipeline
from ..data_pipeline.web_search import WebSearch

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Blueprint
research_agent_bp = Blueprint('research_agent', __name__, url_prefix='/api/research')

# Initialize components
try:
    cohere_chat = CohereChat()
    synthesis_chain = ResearchSynthesisChain(cohere_chat=cohere_chat)
    data_pipeline = DataPipeline()
    web_search = WebSearch()
    logger.info("Research agent components initialized")
except Exception as e:
    logger.error(f"Error initializing research agent components: {str(e)}")
    logger.error(traceback.format_exc())
    # Still define the variables to avoid NameErrors, but they'll be reinitialized on first request
    cohere_chat = None
    synthesis_chain = None
    data_pipeline = None
    web_search = None

# Helper function to ensure components are initialized
def ensure_initialized():
    """Ensure all components are initialized."""
    global cohere_chat, synthesis_chain, data_pipeline, web_search
    
    if cohere_chat is None:
        cohere_chat = CohereChat()
    
    if synthesis_chain is None:
        synthesis_chain = ResearchSynthesisChain(cohere_chat=cohere_chat)
    
    if data_pipeline is None:
        data_pipeline = DataPipeline()
    
    if web_search is None:
        web_search = WebSearch()
    
    return cohere_chat, synthesis_chain, data_pipeline, web_search

@research_agent_bp.route('/query', methods=['POST'])
def research_query():
    """
    Process a research query using the legal research agent.
    
    Request JSON:
    {
        "query": "What is the standard for...",
        "collections": ["case_law", "statutes"],
        "use_web_search": true,
        "max_web_results": 5,
        "context": "Optional additional context about the query",
        "conversation_id": "optional-conversation-id"
    }
    """
    try:
        # Ensure components are initialized
        cohere_chat, synthesis_chain, data_pipeline, web_search = ensure_initialized()
        
        # Parse request
        data = request.json
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing required parameter: query",
                "status": "error"
            }), 400
        
        query = data.get('query')
        collections = data.get('collections', ['case_law', 'statutes', 'regulations'])
        use_web_search = data.get('use_web_search', True)
        max_web_results = data.get('max_web_results', 5)
        context = data.get('context')
        conversation_id = data.get('conversation_id')
        
        # If conversation_id is provided, try to use the same conversation
        if conversation_id and conversation_id != cohere_chat.conversation_id:
            cohere_chat.conversation_id = conversation_id
        
        # Step 1: Search vector database for relevant documents
        vector_results = []
        for collection in collections:
            try:
                results = data_pipeline.search_documents(query, collection=collection, limit=10)
                if results:
                    vector_results.extend(results)
                    logger.info(f"Found {len(results)} results in collection {collection}")
            except Exception as e:
                logger.warning(f"Error searching collection {collection}: {str(e)}")
        
        # Step 2: Optionally perform web search if requested and if vector results are insufficient
        web_results = []
        if use_web_search and (len(vector_results) < 3 or len(query.split()) > 4):
            try:
                search_results = web_search.search(query, max_results=max_web_results)
                for result in search_results:
                    try:
                        content = web_search.get_content(result['url'])
                        if content:
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
                    except Exception as e:
                        logger.warning(f"Error processing web result {result.get('url')}: {str(e)}")
                
                logger.info(f"Added {len(web_results)} web search results")
            except Exception as e:
                logger.warning(f"Error performing web search: {str(e)}")
        
        # Combine results
        all_documents = vector_results + web_results
        
        # Step 3: Synthesize research if we have documents
        if all_documents:
            synthesis_result = synthesis_chain.synthesize_research(
                query=query,
                documents=all_documents,
                user_context=context
            )
            
            # Prepare the response
            response = {
                "research": synthesis_result.get("synthesis"),
                "sources": synthesis_result.get("sources", []),
                "query": query,
                "conversation_id": cohere_chat.conversation_id,
                "document_count": len(all_documents),
                "vector_count": len(vector_results),
                "web_count": len(web_results),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        else:
            # No documents found, use Cohere Chat directly
            chat_response = cohere_chat.generate_chat_message(
                message=f"Research Query: {query}\n\nI couldn't find any specific legal documents related to this query. Please provide a general response based on your knowledge.",
                system_prompt="You are a legal research assistant. The system couldn't find relevant documents for this query. Provide a helpful response based on general legal knowledge, but make it clear that you're not citing specific legal documents."
            )
            
            response = {
                "research": chat_response.get("text"),
                "sources": [],
                "query": query,
                "conversation_id": cohere_chat.conversation_id,
                "document_count": 0,
                "vector_count": 0,
                "web_count": 0,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "note": "No specific legal documents were found. Providing a general response."
            }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error processing research query: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@research_agent_bp.route('/chat', methods=['POST'])
def research_chat():
    """
    Chat with the legal research agent.
    
    Request JSON:
    {
        "message": "I have a question about...",
        "conversation_id": "optional-id",
        "system_prompt": "optional custom system prompt",
        "include_context": true
    }
    """
    try:
        # Ensure components are initialized
        cohere_chat, _, _, _ = ensure_initialized()
        
        # Parse request
        data = request.json
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing required parameter: message",
                "status": "error"
            }), 400
        
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        system_prompt = data.get('system_prompt')
        include_context = data.get('include_context', True)
        
        # If conversation_id is provided, try to use the same conversation
        if conversation_id and conversation_id != cohere_chat.conversation_id:
            cohere_chat.conversation_id = conversation_id
        
        # Generate chat response
        response = cohere_chat.generate_chat_message(
            message=message,
            system_prompt=system_prompt,
            include_context=include_context
        )
        
        # Prepare API response
        api_response = {
            "text": response.get("text"),
            "conversation_id": cohere_chat.conversation_id,
            "citations": response.get("citations", []),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        return jsonify(api_response)
    
    except Exception as e:
        logger.error(f"Error in research chat: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@research_agent_bp.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get the chat history for a conversation."""
    try:
        # Ensure components are initialized
        cohere_chat, _, _, _ = ensure_initialized()
        
        # Check if this is the current conversation
        if conversation_id != cohere_chat.conversation_id:
            return jsonify({
                "error": f"Conversation {conversation_id} not found or not active",
                "status": "error"
            }), 404
        
        # Get chat history
        chat_history = cohere_chat.get_chat_history()
        
        return jsonify({
            "conversation_id": conversation_id,
            "chat_history": chat_history,
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@research_agent_bp.route('/conversation/<conversation_id>', methods=['DELETE'])
def clear_conversation(conversation_id):
    """Clear the chat history for a conversation."""
    try:
        # Ensure components are initialized
        cohere_chat, _, _, _ = ensure_initialized()
        
        # Check if this is the current conversation
        if conversation_id != cohere_chat.conversation_id:
            return jsonify({
                "error": f"Conversation {conversation_id} not found or not active",
                "status": "error"
            }), 404
        
        # Clear chat history
        cohere_chat.clear_chat_history()
        
        return jsonify({
            "conversation_id": conversation_id,
            "message": "Conversation history cleared",
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@research_agent_bp.route('/context', methods=['POST'])
def add_research_context():
    """
    Add research context to the current conversation.
    
    Request JSON:
    {
        "context": "string or list of document objects",
        "conversation_id": "optional-id"
    }
    """
    try:
        # Ensure components are initialized
        cohere_chat, _, _, _ = ensure_initialized()
        
        # Parse request
        data = request.json
        if not data or 'context' not in data:
            return jsonify({
                "error": "Missing required parameter: context",
                "status": "error"
            }), 400
        
        context = data.get('context')
        conversation_id = data.get('conversation_id')
        
        # If conversation_id is provided, try to use the same conversation
        if conversation_id and conversation_id != cohere_chat.conversation_id:
            cohere_chat.conversation_id = conversation_id
        
        # Add context
        cohere_chat.add_research_context(context)
        
        return jsonify({
            "conversation_id": cohere_chat.conversation_id,
            "message": "Research context added",
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Error adding research context: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@research_agent_bp.route('/context', methods=['DELETE'])
def clear_research_context():
    """
    Clear research context from the current conversation.
    
    Request JSON:
    {
        "conversation_id": "optional-id"
    }
    """
    try:
        # Ensure components are initialized
        cohere_chat, _, _, _ = ensure_initialized()
        
        # Parse request
        data = request.json or {}
        conversation_id = data.get('conversation_id')
        
        # If conversation_id is provided, try to use the same conversation
        if conversation_id and conversation_id != cohere_chat.conversation_id:
            cohere_chat.conversation_id = conversation_id
        
        # Clear context
        cohere_chat.clear_research_context()
        
        return jsonify({
            "conversation_id": cohere_chat.conversation_id,
            "message": "Research context cleared",
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Error clearing research context: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500 