#!/usr/bin/env python3
"""
Web search module for retrieving legal documents from online sources.

This module handles:
1. Searching the web for legal information
2. Scraping content from search results
3. Processing and embedding the content
4. Storing in vector database with S3 persistence
"""

import os
import sys
import time
import json
import logging
import tempfile
import requests
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import pipeline components
from data_pipeline import DataPipeline

logger = logging.getLogger("WebSearch")

class WebSearch:
    """Search the web for legal documents and process them into the vector database"""
    
    def __init__(self, data_pipeline: Optional[DataPipeline] = None):
        """
        Initialize web search module
        
        Args:
            data_pipeline: Optional DataPipeline instance. If not provided, a new one will be created.
        """
        self.data_pipeline = data_pipeline or DataPipeline()
        self.search_engines = {
            "google": self._search_google,
            "bing": self._search_bing,
            "duckduckgo": self._search_duckduckgo,
            "google_scholar": self._search_google_scholar
        }
        self.authorized_domains = self._load_authorized_domains()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # Keep track of processed URLs to avoid duplicates
        self.processed_urls = set()
        
        # Stats
        self.stats = {
            "searches_performed": 0,
            "urls_found": 0,
            "pages_scraped": 0,
            "pages_failed": 0,
            "documents_processed": 0
        }
    
    def search_and_process(self, 
                          query: str, 
                          collection: str = "case_law",
                          search_engine: str = "google",
                          max_results: int = 10,
                          max_depth: int = 1,
                          follow_links: bool = False) -> Dict[str, Any]:
        """
        Search for legal documents and process them into the vector database
        
        Args:
            query: Search query
            collection: Collection to store documents in
            search_engine: Search engine to use
            max_results: Maximum number of search results to process
            max_depth: Maximum depth for following links
            follow_links: Whether to follow links on found pages
            
        Returns:
            Dictionary with search and processing statistics
        """
        logger.info(f"Searching for: {query} using {search_engine}")
        self.stats["searches_performed"] += 1
        
        # Perform search
        if search_engine not in self.search_engines:
            logger.error(f"Unsupported search engine: {search_engine}")
            return {"error": f"Unsupported search engine: {search_engine}"}
        
        try:
            # Get search results
            search_results = self.search_engines[search_engine](query, max_results)
            urls = [result["url"] for result in search_results]
            self.stats["urls_found"] += len(urls)
            
            if not urls:
                logger.warning(f"No results found for query: {query}")
                return {"error": "No results found", "stats": self.stats}
            
            # Scrape and process content
            processed_docs = self._scrape_and_process(
                urls=urls,
                collection=collection,
                max_depth=max_depth,
                follow_links=follow_links
            )
            
            # Return statistics
            return {
                "query": query,
                "search_engine": search_engine,
                "urls_processed": len(processed_docs),
                "collection": collection,
                "stats": self.stats
            }
            
        except Exception as e:
            logger.error(f"Error during search and process: {e}")
            return {"error": str(e), "stats": self.stats}
    
    def _scrape_and_process(self, 
                           urls: List[str], 
                           collection: str,
                           max_depth: int = 1,
                           follow_links: bool = False) -> List[Dict[str, Any]]:
        """
        Scrape and process content from URLs
        
        Args:
            urls: List of URLs to scrape
            collection: Collection to store documents in
            max_depth: Maximum depth for following links
            follow_links: Whether to follow links on found pages
            
        Returns:
            List of processed document info
        """
        # Filter URLs: eliminate duplicates and non-authorized domains
        urls = [url for url in urls if self._is_allowed_url(url) and url not in self.processed_urls]
        
        if not urls:
            return []
        
        # Create temporary directory for downloaded content
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download content from URLs
            downloaded_files = []
            
            # Use ThreadPoolExecutor for parallel downloads
            with ThreadPoolExecutor(max_workers=5) as executor:
                download_futures = {
                    executor.submit(self._download_content, url, temp_dir, 1, max_depth, follow_links): url 
                    for url in urls
                }
                
                for future in download_futures:
                    try:
                        files = future.result()
                        if files:
                            downloaded_files.extend(files)
                    except Exception as e:
                        url = download_futures[future]
                        logger.error(f"Error downloading {url}: {e}")
            
            if not downloaded_files:
                logger.warning("No content downloaded from URLs")
                return []
            
            # Process downloaded files
            logger.info(f"Processing {len(downloaded_files)} downloaded files")
            
            # Use DataPipeline to process the files
            stats = self.data_pipeline.process_documents(
                source_dir=temp_dir,
                collection=collection,
                batch_size=10,
                recursive=True
            )
            
            self.stats["documents_processed"] += stats.get("succeeded", 0)
            
            # Return processed documents information
            return [{"file": file, "status": "processed"} for file in downloaded_files]
    
    def _download_content(self, 
                         url: str, 
                         output_dir: str,
                         current_depth: int = 1,
                         max_depth: int = 1,
                         follow_links: bool = False) -> List[str]:
        """
        Download content from URL and save to file
        
        Args:
            url: URL to download
            output_dir: Directory to save downloaded content
            current_depth: Current link depth
            max_depth: Maximum depth for following links
            follow_links: Whether to follow links on found pages
            
        Returns:
            List of downloaded file paths
        """
        if url in self.processed_urls:
            return []
        
        self.processed_urls.add(url)
        downloaded_files = []
        
        try:
            logger.info(f"Downloading content from {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get("Content-Type", "").lower()
            
            if "text/html" in content_type:
                # Process HTML content
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract title
                title = soup.title.string if soup.title else "Unknown"
                safe_title = "".join(c if c.isalnum() else "_" for c in title)[:50]
                
                # Determine if this page is a legal document based on content
                doc_type = self._determine_document_type(soup)
                
                if doc_type:
                    # Save as HTML file
                    file_path = os.path.join(output_dir, f"{safe_title}_{doc_type}.html")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(response.text)
                    
                    downloaded_files.append(file_path)
                    self.stats["pages_scraped"] += 1
                
                # Follow links if requested and not at max depth
                if follow_links and current_depth < max_depth:
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        
                        # Convert relative URL to absolute
                        if not href.startswith(("http://", "https://")):
                            href = urljoin(url, href)
                        
                        # Check if URL is allowed
                        if self._is_allowed_url(href) and href not in self.processed_urls:
                            # Follow link and add any downloaded files
                            child_files = self._download_content(
                                href, output_dir, current_depth + 1, max_depth, follow_links)
                            downloaded_files.extend(child_files)
            
            elif "application/pdf" in content_type:
                # Save PDF
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename.endswith(".pdf"):
                    filename = f"document_{int(time.time())}.pdf"
                
                file_path = os.path.join(output_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                downloaded_files.append(file_path)
                self.stats["pages_scraped"] += 1
            
            else:
                # Unsupported content type
                logger.warning(f"Unsupported content type: {content_type} for {url}")
        
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            self.stats["pages_failed"] += 1
        
        return downloaded_files
    
    def _determine_document_type(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Determine document type from HTML content
        
        Args:
            soup: BeautifulSoup object of HTML content
            
        Returns:
            Document type or None if not a legal document
        """
        text = soup.get_text().lower()
        
        # Check for case law indicators
        case_indicators = [
            "v.", "versus", "plaintiff", "defendant", "appellant", "appellee",
            "court of appeals", "supreme court", "district court", "opinion", 
            "case no", "docket no"
        ]
        
        statute_indicators = [
            "public law", "statute", "section", "u.s.c.", "united states code",
            "legislative", "congress", "enacted", "chapter", "title"
        ]
        
        regulation_indicators = [
            "c.f.r.", "code of federal regulations", "final rule", "regulation",
            "federal register", "proposed rule", "agency", "department of"
        ]
        
        # Count indicators
        case_count = sum(1 for indicator in case_indicators if indicator in text)
        statute_count = sum(1 for indicator in statute_indicators if indicator in text)
        regulation_count = sum(1 for indicator in regulation_indicators if indicator in text)
        
        # Determine type based on highest count
        if case_count > max(statute_count, regulation_count) and case_count >= 3:
            return "case_law"
        elif statute_count > max(case_count, regulation_count) and statute_count >= 3:
            return "statute"
        elif regulation_count > max(case_count, statute_count) and regulation_count >= 3:
            return "regulation"
        elif case_count >= 2 or statute_count >= 2 or regulation_count >= 2:
            return "legal_document"
        
        return None
    
    def _is_allowed_url(self, url: str) -> bool:
        """
        Check if URL is from an authorized domain
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is allowed, False otherwise
        """
        # Allow all URLs if no authorized domains specified
        if not self.authorized_domains:
            return True
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Check if domain or any parent domain is in authorized domains
            domain_parts = domain.split(".")
            for i in range(len(domain_parts) - 1):
                check_domain = ".".join(domain_parts[i:])
                if check_domain in self.authorized_domains:
                    return True
            
            return False
        
        except Exception:
            return False
    
    def _load_authorized_domains(self) -> List[str]:
        """
        Load authorized domains from configuration
        
        Returns:
            List of authorized domains
        """
        # Default authorized legal domains
        default_domains = [
            "scholar.google.com",
            "caselaw.findlaw.com",
            "supreme.justia.com",
            "law.cornell.edu",
            "law.justia.com",
            "courtlistener.com",
            "leagle.com",
            "casetext.com",
            "govinfo.gov",
            "congress.gov",
            "uscourts.gov",
            "federalregister.gov",
            "supremecourt.gov",
            "findlaw.com",
            "lexisnexis.com",
            "westlaw.com"
        ]
        
        # Try to load from config file
        config_path = os.path.join(os.path.dirname(__file__), "config", "authorized_domains.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading authorized domains: {e}")
        
        return default_domains
    
    def _search_google(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Google
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        # Note: This is a simplified implementation
        # For production, you would need to use Google Custom Search API
        # or implement a more robust scraping mechanism
        
        # Add legal terms to query for better results
        legal_query = f"{query} legal case law statute regulation"
        search_url = f"https://www.google.com/search?q={legal_query.replace(' ', '+')}"
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            # Print response for debugging
            logging.debug(f"Google search response length: {len(response.text)}")
            
            # Extract search results - modern Google HTML structure
            for result in soup.select("div.tF2Cxc")[:max_results]:
                link = result.select_one("a")
                if not link or not link.get("href"):
                    continue
                
                href = link["href"]
                if href.startswith("/url?q="):
                    href = href.split("/url?q=")[1].split("&")[0]
                
                title = result.select_one("h3")
                title_text = title.get_text() if title else "Unknown"
                
                snippet = result.select_one("div.VwiC3b")
                snippet_text = snippet.get_text() if snippet else ""
                
                results.append({
                    "title": title_text,
                    "url": href,
                    "snippet": snippet_text
                })
            
            # Try different selectors if no results found
            if not results:
                # First alternative selector
                for result in soup.select("div.g")[:max_results]:
                    link = result.select_one("a")
                    if not link or not link.get("href"):
                        continue
                    
                    href = link["href"]
                    if href.startswith("/url?q="):
                        href = href.split("/url?q=")[1].split("&")[0]
                    
                    title = result.select_one("h3")
                    title_text = title.get_text() if title else "Unknown"
                    
                    snippet = result.select_one("div.IsZvec")
                    snippet_text = snippet.get_text() if snippet else ""
                    
                    results.append({
                        "title": title_text,
                        "url": href,
                        "snippet": snippet_text
                    })
            
            # Fallback to any link if still no results (less precise)
            if not results:
                for a_tag in soup.find_all("a", href=True)[:max_results * 2]:
                    href = a_tag["href"]
                    
                    # Only process search result links
                    if not href.startswith("/url?q="):
                        continue
                    
                    # Extract URL
                    url = href.split("/url?q=")[1].split("&")[0]
                    
                    # Skip Google's own services
                    if "google" in url.lower():
                        continue
                    
                    # Get title and snippet if available
                    title_text = a_tag.get_text() or "Unknown"
                    snippet_text = ""
                    
                    results.append({
                        "title": title_text,
                        "url": url,
                        "snippet": snippet_text
                    })
                    
                    if len(results) >= max_results:
                        break
            
            # Add fixed legal documents as fallback if no results from Google
            if not results:
                results = self._get_fallback_legal_documents(query)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching Google: {e}")
            # Return fallback legal documents on error
            return self._get_fallback_legal_documents(query)
    
    def _get_fallback_legal_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Return fallback legal documents when search fails
        
        Args:
            query: The original search query
            
        Returns:
            List of legal document URLs
        """
        logger.info("Using fallback legal documents")
        
        # Map of common legal topics to relevant documents
        topic_map = {
            "privacy": [
                "https://www.law.cornell.edu/constitution/fourth_amendment",
                "https://www.law.cornell.edu/wex/fourth_amendment",
                "https://supreme.justia.com/cases/federal/us/389/347/",  # Katz v. United States
            ],
            "first amendment": [
                "https://www.law.cornell.edu/constitution/first_amendment",
                "https://www.law.cornell.edu/wex/first_amendment",
                "https://supreme.justia.com/cases/federal/us/403/15/",  # Cohen v. California
            ],
            "fourth amendment": [
                "https://www.law.cornell.edu/constitution/fourth_amendment",
                "https://www.law.cornell.edu/wex/fourth_amendment",
                "https://supreme.justia.com/cases/federal/us/389/347/",  # Katz v. United States
            ],
            "due process": [
                "https://www.law.cornell.edu/constitution/fifth_amendment",
                "https://www.law.cornell.edu/constitution/amendmentxiv",
                "https://www.law.cornell.edu/wex/due_process",
            ],
            "equal protection": [
                "https://www.law.cornell.edu/constitution/amendmentxiv",
                "https://www.law.cornell.edu/wex/equal_protection",
                "https://supreme.justia.com/cases/federal/us/347/483/",  # Brown v. Board of Education
            ],
        }
        
        # Default documents
        default_docs = [
            "https://www.law.cornell.edu/wex/constitutional_law",
            "https://www.law.cornell.edu/wex/civil_rights",
            "https://www.law.cornell.edu/wex/criminal_law",
        ]
        
        # Check if query matches any topics
        query_lower = query.lower()
        for topic, urls in topic_map.items():
            if topic in query_lower:
                return [
                    {"title": f"Legal document about {topic}", "url": url, "snippet": f"Fallback document for {topic}"} 
                    for url in urls
                ]
        
        # Return default docs if no match
        return [
            {"title": "Constitutional Law", "url": url, "snippet": "Fallback legal document"}
            for url in default_docs
        ]
    
    def _search_bing(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Bing search implementation"""
        # Similar implementation to Google search
        # For production, use Bing Web Search API
        return []
    
    def _search_duckduckgo(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """DuckDuckGo search implementation"""
        # Similar implementation to Google search
        # For production, use DuckDuckGo API or scraping
        return []
    
    def _search_google_scholar(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Google Scholar for legal cases
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        search_url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            # Extract search results
            for result in soup.select(".gs_r.gs_or.gs_scl")[:max_results]:
                title_elem = result.select_one(".gs_rt")
                title = title_elem.get_text() if title_elem else "Unknown"
                
                link = None
                if title_elem and title_elem.select_one("a"):
                    link = title_elem.select_one("a")["href"]
                
                if not link:
                    continue
                
                snippet_elem = result.select_one(".gs_rs")
                snippet = snippet_elem.get_text() if snippet_elem else ""
                
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching Google Scholar: {e}")
            return []

# Command-line interface
if __name__ == "__main__":
    import argparse
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Search the web for legal documents and process them")
    parser.add_argument("--query", type=str, required=True, help="Search query")
    parser.add_argument("--collection", type=str, default="case_law", 
                        help="Collection to store documents in")
    parser.add_argument("--search-engine", type=str, default="google", 
                        choices=["google", "bing", "duckduckgo", "google_scholar"],
                        help="Search engine to use")
    parser.add_argument("--max-results", type=int, default=10,
                        help="Maximum number of search results to process")
    parser.add_argument("--max-depth", type=int, default=1,
                        help="Maximum depth for following links")
    parser.add_argument("--follow-links", action="store_true",
                        help="Follow links on found pages")
    
    args = parser.parse_args()
    
    # Create web search instance
    web_search = WebSearch()
    
    # Perform search and process
    result = web_search.search_and_process(
        query=args.query,
        collection=args.collection,
        search_engine=args.search_engine,
        max_results=args.max_results,
        max_depth=args.max_depth,
        follow_links=args.follow_links
    )
    
    # Print result
    print(json.dumps(result, indent=2)) 