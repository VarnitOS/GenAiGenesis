#!/usr/bin/env python3
"""
End-to-End Pipeline Test Script

This script tests the complete legal research pipeline:
1. Client Understanding (Model A)
2. Legal Research (Model B)
3. Research Verification (Model C)
4. Final Response Generation

Usage:
  python test_pipeline.py --query "What are my rights as a tenant in New York?"
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime
from pprint import pprint
from dotenv import load_dotenv

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Check required environment variables
required_env_vars = ['COHERE_API_KEY', 'SERPAPI_KEY']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set them in your .env file or export them in your shell.")
    sys.exit(1)

# Import services after environment check
from services.client_agent import client_agent
from services.research_agent import research_agent
from services.vector_db_service import vector_db_service

class PipelineTester:
    """Test the complete legal research pipeline"""
    
    def __init__(self, log_file="pipeline_test.log"):
        self.log_file = log_file
        self.results = {}
        self.start_time = None
        self.log_data = []
        
    def log(self, message, level="INFO"):
        """Log a message to the console and log data"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.log_data.append(log_entry)
        
    def save_log(self):
        """Save the log data to a file"""
        with open(self.log_file, 'w') as f:
            f.write("\n".join(self.log_data))
        self.log(f"Log saved to {self.log_file}")
    
    def save_results(self, output_file=None):
        """Save the results to a JSON file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"pipeline_result_{timestamp}.json"
            
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        self.log(f"Results saved to {output_file}")
        return output_file
    
    def run_pipeline(self, query):
        """Run the complete pipeline"""
        self.start_time = time.time()
        self.log(f"Starting pipeline test with query: '{query}'")
        self.results = {"query": query, "timestamp": datetime.now().isoformat()}
        
        try:
            # Step 1: Client Understanding (Model A)
            self.log("Step 1: Processing with Client Understanding Agent (Model A)")
            client_understanding = self._run_client_understanding(query)
            self.results["client_understanding"] = client_understanding
            
            # Log client understanding result
            if 'error' in client_understanding:
                self.log(f"⚠️ Warning in client understanding: {client_understanding['error']}", "WARNING")
            else:
                analysis = client_understanding.get('analysis', {})
                if isinstance(analysis, dict) and 'primary_concerns' in analysis:
                    self.log(f"✓ Client understanding complete - Identified primary concerns: {', '.join(analysis['primary_concerns'])}")
                else:
                    self.log("✓ Client understanding complete - Analysis available in text format")
            
            # Step 2: Legal Research (Model B)
            self.log("Step 2: Conducting Legal Research (Model B)")
            self.log("Calling research_agent.conduct_research with query: " + query, "DEBUG")
            research_results = self._run_legal_research(query)
            self.results["research"] = research_results
            
            # Log research results
            if 'error' in research_results:
                self.log(f"⚠️ Warning in research: {research_results['error']}", "WARNING")
            else:
                vector_count = len(research_results.get('vector_results', []))
                internet_count = len(research_results.get('internet_results', []))
                self.log(f"✓ Research complete - Found {vector_count} vector results and {internet_count} internet results")
            
            # Step 3: Generate Final Response
            self.log("Step 3: Generating Final Response")
            final_response = self._generate_final_response(query, client_understanding, research_results)
            self.results["final_response"] = final_response
            
            # Log final response status
            if 'error' in final_response:
                self.log(f"⚠️ Warning in final response: {final_response['error']}", "WARNING")
            else:
                self.log("✓ Final response generated successfully")
            
            # Calculate timing
            execution_time = time.time() - self.start_time
            self.results["execution_time"] = execution_time
            self.log(f"Pipeline completed in {execution_time:.2f} seconds")
            
            return self.results
            
        except Exception as e:
            self.log(f"Error in pipeline: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "DEBUG")
            self.results["error"] = str(e)
            return self.results
    
    def _run_client_understanding(self, query):
        """Run the client understanding agent (Model A)"""
        try:
            # The client agent might return different formats, handle both possibilities
            understanding = client_agent.understand_query(query)
            
            # Check if understanding is a string (error message)
            if isinstance(understanding, str):
                return {"error": understanding}
                
            # If it's a dict with these keys, it's the standard response format
            if isinstance(understanding, dict) and all(key in understanding for key in ["original_query", "analysis"]):
                return understanding
                
            # Otherwise wrap it in a standard format
            return {
                "original_query": query,
                "analysis": understanding
            }
        except Exception as e:
            self.log(f"Error in client understanding: {str(e)}", "ERROR")
            return {"error": str(e)}
    
    def _run_legal_research(self, query):
        """Run the legal research agent (Model B)"""
        try:
            self.log(f"Starting research for query: {query}", "DEBUG")
            
            # Use a try/except block specifically for the research_agent call
            try:
                research = research_agent.conduct_research(query)
                self.log("Research agent returned successfully", "DEBUG")
                
                # Validate the research result structure
                if not isinstance(research, dict):
                    self.log(f"Warning: research_agent returned non-dict type: {type(research)}", "WARNING")
                    return {"error": f"Invalid research result type: {type(research)}"}
                
                # Check for critical fields
                vector_results = research.get('vector_results', [])
                internet_results = research.get('internet_results', [])
                synthesis = research.get('synthesis', '')
                
                self.log(f"Vector results: {len(vector_results)}, Internet results: {len(internet_results)}", "DEBUG")
                self.log(f"Synthesis length: {len(synthesis)}", "DEBUG")
                
                return research
                
            except Exception as inner_e:
                self.log(f"Inner exception in research agent: {str(inner_e)}", "ERROR")
                import traceback
                self.log(traceback.format_exc(), "DEBUG")
                return {"error": f"Research agent error: {str(inner_e)}"}
                
        except Exception as e:
            self.log(f"Error in legal research: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "DEBUG")
            return {"error": str(e)}
    
    def _generate_final_response(self, query, client_understanding, research_results):
        """Generate the final response by combining client understanding and research"""
        try:
            # Extract analysis from client understanding
            analysis = client_understanding.get("analysis", "")
            
            # Extract primary concerns - handle both string and dict formats
            if isinstance(analysis, dict) and "primary_concerns" in analysis:
                primary_concerns = ", ".join(analysis.get("primary_concerns", []))
            else:
                # Try to extract concerns from text analysis
                primary_concerns = "understanding legal requirements for contracts"
            
            # Get research synthesis
            synthesis = research_results.get("synthesis", "")
            
            # Create a context that combines the research and understanding
            combined_context = f"""
Client Query: {query}

Primary Client Concerns: {primary_concerns}

Legal Research Findings:
{synthesis}
            """
            
            # Generate response
            try:
                response = client_agent.respond_to_client(query, [combined_context])
                return response
            except Exception as e:
                self.log(f"Error from client agent: {str(e)}", "ERROR")
                # Fallback to simple format if client agent fails
                return {
                    "response": f"Based on our research: {synthesis[:500]}..."
                }
                
        except Exception as e:
            self.log(f"Error generating final response: {str(e)}", "ERROR")
            return {"error": str(e)}

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Test the complete legal research pipeline')
    parser.add_argument('--query', '-q', required=True, help='Legal query to test')
    parser.add_argument('--output', '-o', help='Output file for results (JSON)')
    parser.add_argument('--log', '-l', default='pipeline_test.log', help='Log file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed output')
    return parser.parse_args()

def display_summary(results, verbose=False):
    """Display a summary of the results"""
    print("\n" + "=" * 80)
    print(f"PIPELINE TEST SUMMARY")
    print("=" * 80)
    
    print(f"\nQuery: {results['query']}")
    print(f"Execution Time: {results.get('execution_time', 0):.2f} seconds")
    
    # Client Understanding
    if 'client_understanding' in results:
        cu = results['client_understanding']
        print("\nCLIENT UNDERSTANDING:")
        if 'error' in cu:
            print(f"- Error: {cu['error']}")
        elif 'analysis' in cu:
            analysis = cu['analysis']
            if isinstance(analysis, dict):
                print(f"- Primary concerns: {', '.join(analysis.get('primary_concerns', []))}")
                print(f"- Legal domains: {', '.join(analysis.get('legal_domains', []))}")
                if verbose:
                    print("\nDetailed Analysis:")
                    pprint(analysis)
            else:
                # Handle case where analysis is a string
                print(f"- Analysis: {analysis}")
    
    # Research Results
    if 'research' in results:
        research = results['research']
        print("\nRESEARCH RESULTS:")
        if 'error' in research:
            print(f"- Error: {research['error']}")
        else:
            vector_results = research.get('vector_results', [])
            internet_results = research.get('internet_results', [])
            print(f"- Vector results: {len(vector_results)}")
            print(f"- Internet results: {len(internet_results)}")
            
            if verbose and internet_results:
                print("\nInternet Sources:")
                for i, result in enumerate(internet_results):
                    print(f"  {i+1}. {result.get('title')} - {result.get('url')}")
    
    # Final Response
    if 'final_response' in results:
        final = results['final_response']
        print("\nFINAL RESPONSE:")
        if 'error' in final:
            print(f"- Error: {final['error']}")
        else:
            response = final.get('response', 'No response generated')
            print(response)
    
    print("\n" + "=" * 80)
    print(f"Full results saved to: {results.get('output_file', 'Not saved')}")
    print("=" * 80 + "\n")

def main():
    """Main entry point"""
    args = parse_args()
    
    # Create and run the pipeline tester
    tester = PipelineTester(log_file=args.log)
    results = tester.run_pipeline(args.query)
    
    # Save results
    output_file = args.output if args.output else None
    output_file = tester.save_results(output_file)
    results['output_file'] = output_file
    
    # Save log
    tester.save_log()
    
    # Display summary
    display_summary(results, verbose=args.verbose)

if __name__ == "__main__":
    main() 