import os
import json
import requests
from typing import Dict, List, Any, Optional
import cohere
from dotenv import load_dotenv
from services.vector_db_service import vector_db_service
from services.embedding_service import embedding_service

# Load environment variables
load_dotenv()

# Authorized legal sources
AUTHORIZED_SOURCES = [
    "law.cornell.edu",
    "supremecourt.gov",
    "uscourts.gov",
    "justice.gov",
    "eeoc.gov",
    "nlrb.gov",
    "ada.gov",
    "courtlistener.com",
    "casetext.com",
    "findlaw.com",
    "justia.com",
    "lexisnexis.com",
    "westlaw.com",
    "hud.gov",
    "dol.gov"
]

class ResearchSynthesisChain:
    """
    B3: Research Synthesis Chain
    Analyzes and synthesizes information from multiple sources
    """
    def __init__(self, cohere_client):
        self.co = cohere_client
        
    def run(self, query: str, documents: List[Dict[str, Any]], internet_results: List[Dict[str, Any]]) -> str:
        """Run the synthesis chain with documents and search results"""
        # Format documents for context
        doc_context = ""
        if documents:
            doc_context = "\n\n".join([
                f"DOCUMENT {i+1}:\nTitle/Source: {doc.get('metadata', {}).get('source', 'Unknown')}\n{doc['document'][:1000]}..."
                for i, doc in enumerate(documents)
            ])
        
        # Format internet results
        internet_context = ""
        if internet_results:
            internet_context = "\n\n".join([
                f"WEB SOURCE {i+1}:\nURL: {result['url']}\nTitle: {result['title']}\nExcerpt: {result['snippet']}"
                for i, result in enumerate(internet_results)
            ])
        
        # Structured prompt for synthesizing information
        synthesis_prompt = f"""
        You are a specialized legal research AI that synthesizes information from legal databases and authorized sources.
        
        CLIENT QUERY: {query}
        
        INTERNAL DATABASE SOURCES:
        {doc_context}
        
        AUTHORIZED INTERNET SOURCES:
        {internet_context}
        
        Based on these sources, provide a comprehensive analysis that:
        1. Identifies the relevant legal principles, statutes, regulations, or cases
        2. Explains how these apply to the client's situation
        3. Synthesizes information from multiple sources into coherent legal analysis
        4. Acknowledges any limitations or areas where further research may be needed
        5. Provides practical next steps or considerations for the client
        
        Your synthesis should be factual, balanced, and properly source all information.
        """
        
        # B1: Use Cohere Chat to generate synthesis
        response = self.co.chat(
            message=synthesis_prompt,
            model="command-r-plus",
            temperature=0.2,
            citation_quality="accurate",
            connectors=[{"id": "web-search"}]
        )
        
        return response.text

class LegalWebSearch:
    """
    Web search component specifically for legal information
    Ensures only authorized sources are used
    """
    def __init__(self):
        self.api_key = os.environ.get('SERPAPI_KEY')
        if not self.api_key:
            raise ValueError("SERPAPI_KEY environment variable not set")
        
        self.base_url = "https://serpapi.com/search"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search for legal information from authorized sources"""
        # Add site: operators to restrict to authorized domains
        site_operators = " OR ".join([f"site:{site}" for site in AUTHORIZED_SOURCES])
        legal_query = f"({query}) ({site_operators})"
        
        # Call search API
        params = {
            "q": legal_query,
            "api_key": self.api_key,
            "num": num_results * 3,  # Request more to filter
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            results = response.json()
            
            # Extract and filter organic results
            organic_results = results.get("organic_results", [])
            filtered_results = []
            
            for result in organic_results:
                # Check if from authorized domain
                domain = self._extract_domain(result.get("link", ""))
                if any(auth_domain in domain for auth_domain in AUTHORIZED_SOURCES):
                    filtered_results.append({
                        "url": result.get("link"),
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "source": domain
                    })
                
                if len(filtered_results) >= num_results:
                    break
            
            return filtered_results
        except Exception as e:
            print(f"Error in web search: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        
        # Simple domain extraction
        try:
            if url.startswith("http"):
                domain = url.split("//")[1].split("/")[0]
                return domain
            return url.split("/")[0]
        except Exception:
            return url

class LegalResearchAgent:
    """
    Model B: Legal Research Agent
    Handles legal research, document search, and synthesis
    Components:
    - B1: Cohere Chat
    - B2: Vector Search Engine
    - B3: Research Synthesis Chain
    """
    
    def __init__(self):
        # Initialize Cohere client
        api_key = os.environ.get('COHERE_API_KEY')
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")
            
        # B1: Cohere Chat
        self.co = cohere.Client(api_key)
        
        # B2: Vector Search Engine uses existing service
        self.vector_db = vector_db_service
        
        # Web search component
        try:
            self.web_search = LegalWebSearch()
            self.web_search_enabled = True
        except Exception as e:
            print(f"Web search disabled: {e}")
            self.web_search_enabled = False
        
        # B3: Create synthesis chain
        self.synthesis_chain = ResearchSynthesisChain(self.co)
    
    def conduct_research(self, query: str, collections: List[str] = None, top_k: int = 3) -> Dict[str, Any]:
        """Conduct comprehensive legal research on a query"""
        if not collections:
            collections = ["case_law", "statutes", "regulations"]
        
        # Process query to identify research focus
        research_focus = self._determine_research_focus(query)
        
        # Determine if this is a local/municipal law query (parking, local ordinances, etc.)
        municipal_keywords = ['parking', 'ticket', 'fine', 'city', 'municipal', 'ordinance', 
                              'local law', 'bylaw', 'citation', 'meter', 'street', 'sidewalk',
                              'permit', 'zone', 'tow', 'impound']
        
        is_municipal_query = any(keyword in query.lower() for keyword in municipal_keywords)
        
        # Phase 1: Search vector databases (B2)
        # For municipal queries, we still search but will prioritize web results later
        vector_results = []
        for collection in collections:
            try:
                results = self.vector_db.search(
                    query=query,
                    collection_name=collection,
                    top_k=top_k
                )
                vector_results.extend(results.get("results", []))
            except Exception as e:
                print(f"Error searching {collection}: {e}")
        
        # Phase 2: Search authorized internet sources
        # Increase web search results for municipal queries
        internet_results = []
        if self.web_search_enabled:
            try:
                # Use more web results for municipal queries
                web_results_count = top_k * 2 if is_municipal_query else top_k
                internet_results = self.web_search.search(query, num_results=web_results_count)
                
                # Log the web search activity
                print(f"Performed web search for query: {query}")
                print(f"Found {len(internet_results)} web results")
                
                # Print the first few results for debugging
                for i, result in enumerate(internet_results[:3]):
                    print(f"Web result {i+1}: {result.get('title')} - {result.get('url')}")
                    
            except Exception as e:
                print(f"Error in web search: {e}")
        
        # For municipal queries, prioritize web results over vector results
        if is_municipal_query and internet_results:
            print(f"Municipal query detected: {query}")
            print("Prioritizing web search results over vector database results")
            
            # Adjust synthesis to focus more on web results for municipal queries
            synthesis = self.synthesis_chain.run(
                query=query,
                documents=vector_results,
                internet_results=internet_results
            )
        else:
            # Regular synthesis for non-municipal queries
            synthesis = self.synthesis_chain.run(
                query=query,
                documents=vector_results,
                internet_results=internet_results
            )
        
        # Format response
        response = {
            "query": query,
            "research_focus": research_focus,
            "vector_results": vector_results,
            "internet_results": internet_results,
            "synthesis": synthesis,
            "is_municipal_query": is_municipal_query
        }
        
        # Clean up S3 bucket after generating response
        try:
            from data_pipeline.cleanup import VectorDBCleanup
            cleanup = VectorDBCleanup()
            cleanup.clear_s3_bucket()
            print("S3 bucket cleared after generating response")
        except Exception as e:
            print(f"Failed to clear S3 bucket: {str(e)}")
        
        return response
    
    def _determine_research_focus(self, query: str) -> Dict[str, Any]:
        """Determine the focus areas for research based on the query"""
        focus_prompt = f"""
        Analyze this legal query and identify:
        1. The primary legal domains involved (e.g., employment law, property law)
        2. Specific legal concepts that need research
        3. Potential keywords for searching legal databases
        
        Query: {query}
        
        Provide your analysis as a structured JSON with these keys.
        """
        
        try:
            response = self.co.chat(
                message=focus_prompt,
                model="command-light",
                temperature=0.1
            )
            
            # Try to parse as JSON
            try:
                return json.loads(response.text)
            except:
                # If not valid JSON, return as text
                return {
                    "domains": [],
                    "concepts": [],
                    "keywords": [],
                    "raw_analysis": response.text
                }
                
        except Exception as e:
            print(f"Error determining research focus: {e}")
            return {
                "domains": [],
                "concepts": [],
                "keywords": []
            }

# Create a singleton instance
research_agent = LegalResearchAgent() 