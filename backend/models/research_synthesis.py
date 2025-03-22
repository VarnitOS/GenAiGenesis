"""
Research Synthesis Chain for the Legal Research Agent.
Processes retrieved documents, extracts key insights, and synthesizes coherent responses.
"""

import os
import json
import logging
import redis
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
from .cohere_chat import CohereChat
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ResearchSynthesisChain:
    """
    Chain that processes retrieved legal documents, extracts key insights,
    and synthesizes them into coherent responses for the user.
    """
    
    def __init__(
        self,
        cohere_chat: Optional[CohereChat] = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: Optional[str] = None,
        cache_expiration: int = 3600  # 1 hour
    ):
        """
        Initialize the Research Synthesis Chain.
        
        Args:
            cohere_chat: CohereChat instance for generating responses
            redis_host: Redis host for caching
            redis_port: Redis port
            redis_password: Redis password if required
            cache_expiration: Cache expiration time in seconds
        """
        # Initialize Cohere Chat if not provided
        if cohere_chat:
            self.cohere_chat = cohere_chat
        else:
            self.cohere_chat = CohereChat()
        
        # Setup Redis for caching
        try:
            self.redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True
            )
            self.redis.ping()  # Test connection
            self.cache_available = True
            self.cache_expiration = cache_expiration
            logger.info("Redis cache connected for research synthesis")
        except Exception as e:
            logger.warning(f"Redis cache not available: {str(e)}")
            self.cache_available = False
        
        logger.info("Research Synthesis Chain initialized")
    
    def _get_cache_key(self, query: str, sources: List[str]) -> str:
        """Generate a deterministic cache key from query and sources."""
        # Sort sources to ensure consistent key
        sorted_sources = sorted(sources) if sources else []
        key_data = f"{query.lower().strip()}:{','.join(sorted_sources)}"
        return f"research_synthesis:{hash(key_data)}"
    
    def _get_from_cache(self, query: str, sources: List[str]) -> Optional[Dict[str, Any]]:
        """Retrieve results from cache if available."""
        if not self.cache_available:
            return None
        
        cache_key = self._get_cache_key(query, sources)
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            try:
                return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Error parsing cached result: {str(e)}")
        
        return None
    
    def _save_to_cache(self, query: str, sources: List[str], result: Dict[str, Any]):
        """Save results to cache."""
        if not self.cache_available:
            return
        
        cache_key = self._get_cache_key(query, sources)
        try:
            self.redis.setex(
                cache_key,
                self.cache_expiration,
                json.dumps(result)
            )
            logger.debug(f"Saved synthesis to cache: {cache_key}")
        except Exception as e:
            logger.warning(f"Error saving to cache: {str(e)}")
    
    def prioritize_documents(self, documents: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Prioritize documents based on relevance, recency, and authority.
        
        Args:
            documents: List of documents with text and metadata
            query: The original research query
            
        Returns:
            Prioritized list of documents
        """
        if not documents:
            return []
        
        # Calculate a priority score for each document
        for doc in documents:
            metadata = doc.get("metadata", {})
            
            # Base score
            score = 1.0
            
            # Adjust by document type
            doc_type = metadata.get("type", "").lower()
            if doc_type == "case_law":
                score *= 1.2
            elif doc_type == "statute":
                score *= 1.3
            elif doc_type == "regulation":
                score *= 1.1
            elif doc_type == "web_content":
                score *= 0.8  # Lower priority for web content
            
            # Adjust by jurisdiction level
            jurisdiction = metadata.get("jurisdiction", "").lower()
            if "supreme" in jurisdiction:
                score *= 1.5
            elif "federal" in jurisdiction:
                score *= 1.3
            elif "appellate" in jurisdiction:
                score *= 1.2
            
            # Adjust by date (newer = higher priority)
            if "date" in metadata:
                try:
                    date_str = metadata["date"]
                    if isinstance(date_str, str):
                        # Simple parsing - assumes format like "2023-01-01" or year only
                        year = int(date_str[:4]) if len(date_str) >= 4 else 0
                        current_year = datetime.now().year
                        if year > 0:
                            # Scale: 1.0 for current year, down to 0.5 for 50+ years old
                            age_factor = max(0.5, 1.0 - (current_year - year) / 100)
                            score *= age_factor
                except Exception:
                    # If date parsing fails, don't adjust score
                    pass
            
            # Store the score
            doc["priority_score"] = score
        
        # Sort by priority score (highest first)
        sorted_docs = sorted(documents, key=lambda x: x.get("priority_score", 0), reverse=True)
        return sorted_docs
    
    def extract_key_points(self, documents: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Extract key points from documents relevant to the query.
        
        Args:
            documents: List of documents with text and metadata
            query: The original research query
            
        Returns:
            List of documents with extracted key points
        """
        system_prompt = (
            "You are a legal research assistant extracting key points from legal documents. "
            "For each document, identify the most important legal points relevant to the query. "
            "Focus on extracting factual information, legal principles, rulings, and precedents. "
            "Do not include opinions or interpretations. Maintain the original legal meaning."
        )
        
        for doc in documents:
            # Skip if already processed
            if "key_points" in doc:
                continue
                
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            
            # Skip if empty text
            if not text.strip():
                doc["key_points"] = []
                continue
            
            # Prepare a prompt for extracting key points
            extraction_prompt = (
                f"Extract 3-5 key legal points from this document that are relevant to the query: \"{query}\"\n\n"
                f"Document type: {metadata.get('type', 'legal document')}\n"
                f"Title/Source: {metadata.get('title', 'Unnamed')}\n\n"
                f"Document text:\n{text[:4000]}..."  # Limit text length
            )
            
            try:
                # Use Cohere to extract key points
                response = self.cohere_chat.generate_chat_message(
                    message=extraction_prompt,
                    system_prompt=system_prompt,
                    include_context=False  # No need to include context for extraction
                )
                
                # Process the response to extract key points
                key_points_text = response.get("text", "")
                key_points = []
                
                # Simple parsing - split by numbers or bullet points
                for line in key_points_text.split("\n"):
                    line = line.strip()
                    if line and (line[0].isdigit() or line[0] in ["•", "-", "*"]):
                        # Clean up the line
                        point = line[1:].strip() if line[0].isdigit() else line[1:].strip()
                        if point:
                            key_points.append(point)
                
                # If parsing failed, try to use the whole response
                if not key_points and key_points_text:
                    key_points = [key_points_text]
                
                doc["key_points"] = key_points
                
            except Exception as e:
                logger.error(f"Error extracting key points: {str(e)}")
                doc["key_points"] = []
        
        return documents
    
    def synthesize_research(
        self, 
        query: str, 
        documents: List[Dict[str, Any]],
        user_context: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Synthesize research from documents into a coherent response.
        
        Args:
            query: Research query
            documents: List of documents with text and metadata
            user_context: Additional context about the user's needs
            use_cache: Whether to use cache for synthesis
            
        Returns:
            Dictionary with synthesized research and metadata
        """
        # Check cache if enabled
        if use_cache:
            doc_sources = [doc.get("metadata", {}).get("source", "unknown") for doc in documents]
            cached_result = self._get_from_cache(query, doc_sources)
            if cached_result:
                logger.info(f"Using cached synthesis for query: {query}")
                return cached_result
        
        # Prepare documents
        if not documents:
            return {
                "synthesis": "No documents were found for this research query.",
                "query": query,
                "sources": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 1: Prioritize documents
        prioritized_docs = self.prioritize_documents(documents, query)
        
        # Step 2: Extract key points from documents
        processed_docs = self.extract_key_points(prioritized_docs, query)
        
        # Step 3: Organize sources for citation
        sources = []
        for doc in processed_docs:
            metadata = doc.get("metadata", {})
            sources.append({
                "title": metadata.get("title", "Untitled Document"),
                "type": metadata.get("type", "legal document"),
                "date": metadata.get("date", "Unknown date"),
                "jurisdiction": metadata.get("jurisdiction", "Unknown jurisdiction"),
                "source": metadata.get("source", "Unknown source"),
                "key_points": doc.get("key_points", [])
            })
        
        # Step 4: Prepare context for synthesis
        # Add processed documents as context for the chat model
        self.cohere_chat.clear_research_context()
        
        # Add top documents as context (limited to top 10 to avoid context limits)
        for doc in processed_docs[:10]:
            self.cohere_chat.add_research_context({
                "text": doc.get("text", ""),
                "source": doc.get("metadata", {}).get("source", "legal document"),
                "metadata": doc.get("metadata", {})
            })
        
        # Step 5: Generate the synthesis
        system_prompt = (
            "You are a legal research specialist synthesizing information from multiple legal sources. "
            "Provide a comprehensive, well-structured response that addresses the research query. "
            "Cite specific cases, statutes, and regulations where appropriate. "
            "Organize information logically with clear headings. "
            "Present balanced perspectives on issues with conflicting precedents. "
            "Your synthesis should be factual, precise, and demonstrate legal expertise."
        )
        
        synthesis_prompt = f"Research Query: {query}\n\n"
        
        if user_context:
            synthesis_prompt += f"Additional Context: {user_context}\n\n"
        
        synthesis_prompt += (
            "Based on the legal documents provided, synthesize a comprehensive response "
            "that addresses the research query. Include relevant legal principles, "
            "cite specific cases and statutes, and provide a clear analysis."
        )
        
        response = self.cohere_chat.generate_chat_message(
            message=synthesis_prompt,
            system_prompt=system_prompt,
            include_context=True  # Include all the documents we added as context
        )
        
        # Step 6: Prepare the result
        result = {
            "synthesis": response.get("text", "Error generating synthesis"),
            "query": query,
            "sources": sources,
            "citations": response.get("citations", []),
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the result
        if use_cache:
            doc_sources = [doc.get("metadata", {}).get("source", "unknown") for doc in documents]
            self._save_to_cache(query, doc_sources, result)
        
        return result
    
    def save_synthesis(self, synthesis: Dict[str, Any], file_path: str) -> bool:
        """
        Save a research synthesis to a file.
        
        Args:
            synthesis: The synthesis result dictionary
            file_path: Path to save the synthesis
            
        Returns:
            Success status
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(synthesis, f, indent=2)
            logger.info(f"Synthesis saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving synthesis: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.append("../")
    from data_pipeline.pipeline import DataPipeline
    
    # Test documents
    test_docs = [
        {
            "text": "The Fourth Amendment protects individuals from unreasonable searches and seizures. "
                   "In Terry v. Ohio, the Supreme Court established that police officers may conduct "
                   "a brief investigatory stop when they have reasonable suspicion of criminal activity.",
            "metadata": {
                "title": "Terry v. Ohio",
                "type": "case_law",
                "date": "1968-06-10",
                "jurisdiction": "Supreme Court",
                "source": "392 U.S. 1"
            }
        },
        {
            "text": "Under the exclusionary rule, evidence obtained through an illegal search or seizure "
                   "is generally inadmissible in court proceedings. However, exceptions exist, including "
                   "the good faith exception established in United States v. Leon.",
            "metadata": {
                "title": "United States v. Leon",
                "type": "case_law",
                "date": "1984-07-05",
                "jurisdiction": "Supreme Court",
                "source": "468 U.S. 897"
            }
        }
    ]
    
    # Initialize the research synthesis chain
    synthesis_chain = ResearchSynthesisChain()
    
    # Synthesize research
    result = synthesis_chain.synthesize_research(
        query="What is the standard for a reasonable search under the Fourth Amendment?",
        documents=test_docs
    )
    
    # Print the result
    print("Research Synthesis:")
    print(result["synthesis"])
    print("\nSources:")
    for source in result["sources"]:
        print(f"- {source['title']} ({source['date']}, {source['jurisdiction']})")
        if source['key_points']:
            print("  Key points:")
            for point in source['key_points']:
                print(f"  * {point}")
    
    # Save the synthesis
    synthesis_chain.save_synthesis(result, "research_synthesis_example.json") 