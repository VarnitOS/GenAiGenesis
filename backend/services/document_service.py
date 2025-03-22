import os
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.cohere_client import cohere_client
from services.embedding_service import embedding_service

class DocumentService:
    """Service to process and analyze legal documents"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        self.document_classifiers = [
            {"text": "This is a legal contract between parties", "label": "contract"},
            {"text": "IN THE COURT OF", "label": "court_filing"},
            {"text": "NOTICE OF MOTION", "label": "motion"},
            {"text": "AFFIDAVIT OF", "label": "affidavit"},
            {"text": "CRIMINAL CODE OF CANADA", "label": "statute"},
            {"text": "IN THE MATTER OF AN APPEAL", "label": "appeal"}
        ]
    
    def process_document(self, text, metadata=None):
        """Process a document by splitting, classifying, and embedding it"""
        # Split document into chunks
        splits = self.text_splitter.split_text(text)
        
        # Classify document type
        doc_type = self._classify_document(text[:1000])  # Use first 1000 chars for classification
        
        # Create metadata for each chunk
        if metadata is None:
            metadata = {}
        
        # Add document type to metadata
        metadata["doc_type"] = doc_type
        
        # Create metadata for each chunk
        metadatas = []
        for i, _ in enumerate(splits):
            chunk_meta = metadata.copy()
            chunk_meta["chunk_index"] = i
            chunk_meta["chunk_count"] = len(splits)
            metadatas.append(chunk_meta)
        
        # Store in appropriate vector store based on doc_type
        store_type = self._determine_store_type(doc_type)
        
        # Embed and store document chunks
        embedding_service.embed_documents(splits, metadatas, store_type=store_type)
        
        return {
            "doc_type": doc_type,
            "chunks": len(splits),
            "store_type": store_type
        }
    
    def _classify_document(self, text_sample):
        """Classify document type using Cohere's classify endpoint"""
        try:
            classification = cohere_client.classify(
                inputs=[text_sample],
                examples=self.document_classifiers
            )
            return classification.classifications[0].prediction
        except Exception as e:
            print(f"Classification error: {e}")
            return "unknown"
    
    def _determine_store_type(self, doc_type):
        """Determine the appropriate vector store type based on document type"""
        # Map document types to store types
        store_map = {
            "statute": "statutes",
            "regulation": "regulations",
            "unknown": "case_law"
        }
        
        # Default to case_law for most document types
        return store_map.get(doc_type, "case_law")
    
    def analyze_document(self, text):
        """Analyze a legal document and extract key information"""
        # Process document
        doc_info = self.process_document(text)
        
        # Generate summary and analysis
        analysis = cohere_client.chat(
            message="Analyze this legal document and extract key information including parties, dates, legal issues, and important clauses.",
            preamble="You are a legal document analyzer. Provide a concise, structured analysis.",
            documents=[{"title": "Document", "snippet": text[:4000]}],  # Use first 4000 chars for analysis
        )
        
        return {
            "doc_type": doc_info["doc_type"],
            "analysis": analysis.text,
            "processed_info": doc_info
        }

# Create a singleton instance
document_service = DocumentService() 