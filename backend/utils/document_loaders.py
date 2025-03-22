import os
import json
import csv
import re
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import TextLoader, PDFMinerLoader, CSVLoader
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LegalDocumentLoader:
    """A utility for loading legal documents from various sources"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
    def load_case_law(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Load case law documents from either text or PDF files"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        base_metadata = metadata or {}
        base_metadata["source_type"] = "case_law"
        base_metadata["source_file"] = os.path.basename(file_path)
        
        # Extract case citation if available in filename
        filename = os.path.basename(file_path)
        citation_match = re.search(r"\[(.*?)\]", filename)
        if citation_match:
            base_metadata["citation"] = citation_match.group(1)
            
        # Load based on file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self._load_pdf(file_path, base_metadata)
        elif ext == ".txt":
            return self._load_text(file_path, base_metadata)
        elif ext == ".json":
            return self._load_json_case(file_path, base_metadata)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
    def load_statute(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Load statute documents from either text, CSV or JSON files"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        base_metadata = metadata or {}
        base_metadata["source_type"] = "statute"
        base_metadata["source_file"] = os.path.basename(file_path)
        
        # Extract statute name from filename
        filename = os.path.basename(file_path)
        statute_name = os.path.splitext(filename)[0]
        base_metadata["statute_name"] = statute_name
            
        # Load based on file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".txt":
            return self._load_text(file_path, base_metadata)
        elif ext == ".json":
            return self._load_json_statute(file_path, base_metadata)
        elif ext == ".csv":
            return self._load_csv_statute(file_path, base_metadata)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _load_text(self, file_path: str, metadata: Dict[str, Any]) -> List[Document]:
        """Load and process a text file"""
        loader = TextLoader(file_path)
        documents = loader.load()
        
        # Add metadata to each document
        for doc in documents:
            doc.metadata.update(metadata)
            
        # Split documents into chunks
        return self.text_splitter.split_documents(documents)
    
    def _load_pdf(self, file_path: str, metadata: Dict[str, Any]) -> List[Document]:
        """Load and process a PDF file"""
        loader = PDFMinerLoader(file_path)
        documents = loader.load()
        
        # Add metadata to each document
        for doc in documents:
            doc.metadata.update(metadata)
            
        # Split documents into chunks
        return self.text_splitter.split_documents(documents)
    
    def _load_json_case(self, file_path: str, metadata: Dict[str, Any]) -> List[Document]:
        """Load case law from a JSON file with expected fields:
        {
            "case_name": "...",
            "citation": "...",
            "jurisdiction": "...",
            "date": "...",
            "text": "..."
        }
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Extract key information
        case_metadata = metadata.copy()
        case_metadata.update({
            "case_name": data.get("case_name", ""),
            "citation": data.get("citation", ""),
            "jurisdiction": data.get("jurisdiction", ""),
            "date": data.get("date", ""),
        })
        
        # Create document
        doc = Document(page_content=data["text"], metadata=case_metadata)
            
        # Split document into chunks
        return self.text_splitter.split_documents([doc])
    
    def _load_json_statute(self, file_path: str, metadata: Dict[str, Any]) -> List[Document]:
        """Load statute from a JSON file with expected fields:
        {
            "statute_name": "...",
            "jurisdiction": "...",
            "effective_date": "...",
            "sections": [
                {"section_number": "1", "title": "...", "text": "..."},
                ...
            ]
        }
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        documents = []
        base_metadata = metadata.copy()
        base_metadata.update({
            "statute_name": data.get("statute_name", ""),
            "jurisdiction": data.get("jurisdiction", ""),
            "effective_date": data.get("effective_date", ""),
        })
        
        # Create a document for each section
        for section in data.get("sections", []):
            section_metadata = base_metadata.copy()
            section_metadata.update({
                "section_number": section.get("section_number", ""),
                "section_title": section.get("title", ""),
            })
            
            # Create a descriptive header
            header = f"Section {section.get('section_number', '')}: {section.get('title', '')}"
            content = f"{header}\n\n{section.get('text', '')}"
            
            doc = Document(page_content=content, metadata=section_metadata)
            documents.append(doc)
            
        # Split documents into chunks
        return self.text_splitter.split_documents(documents)
    
    def _load_csv_statute(self, file_path: str, metadata: Dict[str, Any]) -> List[Document]:
        """Load statute from a CSV file with expected columns:
        section_number, title, text
        """
        documents = []
        base_metadata = metadata.copy()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                section_metadata = base_metadata.copy()
                section_metadata.update({
                    "section_number": row.get("section_number", ""),
                    "section_title": row.get("title", ""),
                })
                
                # Create a descriptive header
                header = f"Section {row.get('section_number', '')}: {row.get('title', '')}"
                content = f"{header}\n\n{row.get('text', '')}"
                
                doc = Document(page_content=content, metadata=section_metadata)
                documents.append(doc)
                
        # Split documents into chunks
        return self.text_splitter.split_documents(documents)

# Create a singleton instance
legal_document_loader = LegalDocumentLoader() 