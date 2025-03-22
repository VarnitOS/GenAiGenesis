import os
import json
from typing import Dict, List, Any, Optional
import cohere

class ClientUnderstandingChain:
    """
    A3: Client Understanding Chain
    Analyzes client queries and understands their legal needs
    """
    def __init__(self, cohere_client):
        self.co = cohere_client
        self.chat_history = []
        
    def run(self, query: str) -> str:
        """Run the understanding chain with the query"""
        # Format chat history for context
        history_text = ""
        if self.chat_history:
            history_text = "\n".join([f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}" 
                               for i, msg in enumerate(self.chat_history)])
        
        # Structured prompt for understanding legal queries
        understanding_prompt = f"""
        You are a specialized legal AI assistant, trained to understand client inquiries and provide helpful responses.
        
        Based on the client's query, identify:
        1. The main legal topic(s) involved
        2. The specific question or concern
        3. Any relevant jurisdictions mentioned
        4. Any time constraints or deadlines mentioned
        5. The client's apparent level of understanding of the topic
        
        Chat History:
        {history_text}
        
        Client Query: {query}
        
        Your analysis of the query:
        """
        
        # A1: Use Cohere Command to generate understanding
        response = self.co.generate(
            prompt=understanding_prompt,
            model="command",
            max_tokens=300,
            temperature=0.7
        )
        
        understanding = response.generations[0].text
        
        # Update chat history
        self.chat_history.append(query)
        self.chat_history.append(understanding)
        
        return understanding

class ClientConsultationAgent:
    """
    Model A: Client Consultation Agent
    Handles client interaction, query understanding, and initial consultation
    Components:
    - A1: Cohere Command
    - A2: Cohere Embed
    - A3: Client Understanding Chain
    """
    
    def __init__(self):
        # Initialize Cohere client
        api_key = os.environ.get('COHERE_API_KEY')
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")
            
        # A1: Cohere Command
        self.co = cohere.Client(api_key)
        
        # A3: Create understanding chain
        self.understanding_chain = ClientUnderstandingChain(self.co)
    
    def embed_query(self, query: str) -> List[float]:
        """A2: Cohere Embed - Generate embeddings for client query"""
        response = self.co.embed(
            texts=[query], 
            model="embed-english-v3.0",
            input_type="search_query"
        )
        return response.embeddings[0]
    
    def understand_query(self, query: str) -> Dict[str, Any]:
        """Process and understand a client query using the Client Understanding Chain (A3)"""
        # Get the understanding chain output
        understanding = self.understanding_chain.run(query=query)
        
        # Generate embeddings for the query (A2)
        embeddings = self.embed_query(query)
        
        # Structure response
        response = {
            "original_query": query,
            "analysis": understanding,
            "embeddings": embeddings[:5] + ["..."]  # Truncated for readability
        }
        
        return response
    
    def respond_to_client(self, query: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate a response to a client query"""
        # First understand the query (A3)
        understanding = self.understand_query(query)
        
        # Construct prompt with understanding and context
        prompt = f"""
        You are a legal assistant helping a client with a query. 
        
        Client query: {query}
        
        Your understanding of the query:
        {understanding['analysis']}
        """
        
        if context:
            prompt += f"\n\nRelevant context:\n" + "\n".join(context)
        
        # Generate the response using Cohere Command (A1)
        response = self.co.generate(
            prompt=prompt,
            model="command",
            max_tokens=500,
            temperature=0.7
        )
        
        return {
            "query": query,
            "understanding": understanding["analysis"],
            "response": response.generations[0].text,
            "consultation_complete": self._is_consultation_complete(query)
        }
    
    def _is_consultation_complete(self, query: str) -> bool:
        """Determine if the consultation phase is complete"""
        # Simple implementation - could be expanded with more sophisticated logic
        completion_indicators = [
            "thank you",
            "thanks for your help",
            "that's all",
            "goodbye"
        ]
        
        return any(indicator in query.lower() for indicator in completion_indicators)

# Create a singleton instance
client_agent = ClientConsultationAgent() 