"""
Cohere Chat integration for the Legal Research Agent.
Handles conversation with Cohere's chat models and manages research context.
"""

import os
import json
import logging
import cohere
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class CohereChat:
    """Interface for Cohere's chat models with specialized legal research capabilities."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "command",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        conversation_id: Optional[str] = None
    ):
        """
        Initialize the Cohere Chat interface.
        
        Args:
            api_key: Cohere API key (defaults to COHERE_API_KEY env variable)
            model: Cohere model to use (command, command-light, etc.)
            temperature: Sampling temperature for response generation
            max_tokens: Maximum tokens to generate in responses
            conversation_id: ID for conversation tracking
        """
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("Cohere API key is required. Set COHERE_API_KEY environment variable.")
        
        self.client = cohere.Client(self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conversation_id = conversation_id or f"legal-research-{datetime.now().timestamp()}"
        self.chat_history = []
        self.research_context = []
        
        logger.info(f"Initialized Cohere Chat with model: {model}")
    
    def add_research_context(self, context: Union[str, List[Dict[str, Any]]]):
        """
        Add research context that will be included with future chat messages.
        
        Args:
            context: Either a string or a list of document dictionaries with 
                    text and metadata to be used as context
        """
        if isinstance(context, str):
            self.research_context.append({"text": context, "source": "research"})
        elif isinstance(context, list):
            for doc in context:
                if isinstance(doc, dict) and "text" in doc:
                    self.research_context.append({
                        "text": doc["text"],
                        "source": doc.get("source", "unknown"),
                        "metadata": doc.get("metadata", {})
                    })
                else:
                    logger.warning(f"Skipping invalid document in context: {doc}")
        else:
            logger.warning(f"Invalid context format: {type(context)}")
        
        # Keep context under a reasonable size
        if len(self.research_context) > 20:
            self.research_context = self.research_context[-20:]
            
        logger.info(f"Added research context. Total context items: {len(self.research_context)}")
    
    def clear_research_context(self):
        """Clear all research context."""
        self.research_context = []
        logger.info("Research context cleared")
    
    def generate_chat_message(
        self, 
        message: str, 
        system_prompt: Optional[str] = None,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a response using Cohere's chat endpoint.
        
        Args:
            message: User message to respond to
            system_prompt: Optional system prompt to override the default
            include_context: Whether to include research context
            
        Returns:
            Dict containing the response and additional info
        """
        # Default legal research system prompt if none provided
        preamble = system_prompt if system_prompt else (
            "You are a legal research assistant specializing in case law, statutes, and regulations."
        )
        
        # Prepare context for the API call - limiting to just a few for testing
        documents = []
        if include_context and self.research_context and len(self.research_context) > 0:
            # Just use the first item to avoid context length issues
            ctx = self.research_context[0]
            documents.append({
                "text": ctx["text"][:1000],  # Limit text length
                "source": ctx.get("source", "legal_document")
            })
        
        try:
            # Make the API call with simplified parameters
            response = self.client.chat(
                message=message,
                model=self.model,
                temperature=self.temperature,
                preamble=preamble
            )
            
            # Update chat history
            self.chat_history.append({"role": "USER", "message": message})
            self.chat_history.append({"role": "CHATBOT", "message": response.text})
            
            # Format the result
            result = {
                "text": response.text,
                "conversation_id": self.conversation_id,
                "citations": response.citations if hasattr(response, "citations") else [],
                "tokens_used": {
                    "prompt": response.token_count.prompt if hasattr(response, "token_count") else None,
                    "response": response.token_count.completion if hasattr(response, "token_count") else None
                }
            }
            
            logger.info(f"Generated chat response")
            return result
            
        except Exception as e:
            logger.error(f"Error generating chat message: {str(e)}")
            return {
                "text": f"Error generating response: {str(e)}",
                "error": str(e),
                "conversation_id": self.conversation_id
            }
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Return the current chat history."""
        return self.chat_history
    
    def clear_chat_history(self):
        """Clear the chat history while maintaining the conversation ID."""
        self.chat_history = []
        logger.info(f"Chat history cleared for conversation {self.conversation_id}")
    
    def save_conversation(self, file_path: str):
        """
        Save the current conversation to a file.
        
        Args:
            file_path: Path to save the conversation
        """
        data = {
            "conversation_id": self.conversation_id,
            "model": self.model,
            "chat_history": self.chat_history,
            "research_context": self.research_context,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Conversation saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            return False
    
    def load_conversation(self, file_path: str):
        """
        Load a conversation from a file.
        
        Args:
            file_path: Path to load the conversation from
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.conversation_id = data.get("conversation_id", self.conversation_id)
            self.model = data.get("model", self.model)
            self.chat_history = data.get("chat_history", [])
            self.research_context = data.get("research_context", [])
            
            logger.info(f"Conversation loaded from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Create a chat instance
    chat = CohereChat(model="command")
    
    # Add some research context
    chat.add_research_context("The Fourth Amendment protects individuals from unreasonable searches and seizures.")
    
    # Generate a response
    response = chat.generate_chat_message(
        "What is the standard for a reasonable search under the Fourth Amendment?"
    )
    
    print(f"Response: {response['text']}")
    print(f"Citations: {response['citations']}") 