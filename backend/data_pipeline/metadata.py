#!/usr/bin/env python3
"""
Metadata extraction and enrichment module.

This module handles:
1. Extracting structured metadata from documents
2. Enriching metadata with additional information
3. Standardizing metadata format
"""

import re
import hashlib
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("MetadataExtractor")

class MetadataExtractor:
    """Extract and enrich metadata from documents"""
    
    def __init__(self):
        # Patterns for extracting legal document metadata
        self.patterns = {
            # Citation patterns
            "citation": [
                r"(\d+\s+U\.S\.\s+\d+)",  # US Reports
                r"(\d+\s+S\.Ct\.\s+\d+)",  # Supreme Court Reporter
                r"(\d+\s+F\.\d+d\s+\d+)",  # Federal Reporter
                r"(\d+\s+F\.\s+Supp\.\s+\d+)",  # Federal Supplement
            ],
            # Date patterns
            "date": [
                r"Decided:\s+([A-Za-z]+\s+\d+,\s+\d{4})",
                r"Date:\s+([A-Za-z]+\s+\d+,\s+\d{4})",
                r"(\d{1,2}/\d{1,2}/\d{2,4})",
                r"(\d{4}-\d{2}-\d{2})",
            ],
            # Court or jurisdiction patterns
            "court": [
                r"(Supreme Court of the United States)",
                r"(United States Court of Appeals for the \w+ Circuit)",
                r"(United States District Court for the \w+ District of \w+)",
            ],
            # Case name or title patterns
            "case_name": [
                r"^([A-Za-z\s\.,]+)\s+v\.\s+([A-Za-z\s\.,]+)",
                r"In re\s+([A-Za-z\s\.,]+)",
                r"Ex parte\s+([A-Za-z\s\.,]+)",
            ]
        }
        
        # Document type mapping
        self.doc_type_indicators = {
            "opinion": ["opinion", "decision", "order", "judgment"],
            "statute": ["act", "code", "statute", "law", "section", "§"],
            "regulation": ["regulation", "rule", "c.f.r", "administrative", "federal register"],
            "brief": ["brief", "memorandum", "motion", "petition"],
            "contract": ["contract", "agreement", "lease", "license"],
        }
    
    def extract(self, text: str, base_metadata: Dict[str, Any], collection: str) -> Dict[str, Any]:
        """
        Extract and enrich metadata from document text
        
        Args:
            text: The document text
            base_metadata: Metadata already extracted during document processing
            collection: The collection this document belongs to
            
        Returns:
            Enriched metadata dictionary
        """
        # Start with base metadata
        metadata = base_metadata.copy()
        
        # Add collection
        metadata["collection"] = collection
        
        # Add timestamp
        metadata["processed_at"] = datetime.now().isoformat()
        
        # Generate content hash
        content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        metadata["content_hash"] = content_hash
        
        # Extract document type
        doc_type = self._extract_document_type(text, metadata)
        metadata["document_type"] = doc_type
        
        # Extract entities
        entities = self._extract_entities(text)
        if entities:
            # Convert list to string to avoid ChromaDB metadata issues
            metadata["entities"] = ", ".join(entities)
        
        # Extract dates
        dates = self._extract_dates(text)
        if dates:
            # Convert list to string to avoid ChromaDB metadata issues
            metadata["dates"] = ", ".join(dates)
            if "date" not in metadata and dates:
                metadata["date"] = dates[0]
        
        # Extract citations
        citations = self._extract_citations(text)
        if citations:
            # Convert list to string to avoid ChromaDB metadata issues
            metadata["citations"] = ", ".join(citations)
            if "citation" not in metadata and citations:
                metadata["citation"] = citations[0]
        
        # Extract specific legal metadata based on document type
        if doc_type == "case_law" or doc_type == "opinion":
            self._extract_case_law_metadata(text, metadata)
        elif doc_type == "statute":
            self._extract_statute_metadata(text, metadata)
        elif doc_type == "regulation":
            self._extract_regulation_metadata(text, metadata)
        
        # Calculate word count and other stats
        word_count = len(text.split())
        metadata["word_count"] = word_count
        metadata["character_count"] = len(text)
        metadata["sentence_count"] = text.count(". ") + text.count(".\n") + text.count("? ") + text.count("! ")
        
        # Quality metrics
        metadata["quality_score"] = self._calculate_quality_score(text, metadata)
        
        # Make sure all metadata values are compatible with ChromaDB
        metadata = self._normalize_metadata_values(metadata)
        
        return metadata
    
    def _extract_document_type(self, text: str, metadata: Dict[str, Any]) -> str:
        """Determine document type based on content and metadata"""
        # First, check if a document type is already in metadata
        if "document_type" in metadata:
            return metadata["document_type"]
        
        # Try to determine from collection
        collection = metadata.get("collection", "")
        if collection == "case_law":
            return "case_law"
        elif collection == "statutes":
            return "statute"
        elif collection == "regulations":
            return "regulation"
        
        # Try to determine from content
        lower_text = text.lower()
        for doc_type, indicators in self.doc_type_indicators.items():
            for indicator in indicators:
                if indicator.lower() in lower_text:
                    return doc_type
        
        # Try to determine from file metadata
        content_type = metadata.get("content_type", "")
        if "pdf" in content_type and "court" in lower_text:
            return "case_law"
        
        # Default
        return "unknown"
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract legal entities from text"""
        entities = []
        
        # Simple pattern for entity extraction
        # This could be replaced with NER from spaCy or other NLP tools
        entity_patterns = [
            r"(?:plaintiff|defendant|petitioner|respondent|appellant|appellee)s?\s+([A-Z][A-Za-z\s\.,]+)",
            r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,5}),\s+(?:Inc\.|LLC|Corp\.|Corporation|Company)",
            r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,5})\s+(?:Department|Agency|Commission|Board)"
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, text)
            entities.extend([match.strip() for match in matches if match.strip()])
        
        # Remove duplicates
        return list(set(entities))
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        dates = []
        
        for pattern in self.patterns["date"]:
            matches = re.findall(pattern, text)
            dates.extend([match.strip() for match in matches if match.strip()])
        
        # Remove duplicates
        return list(set(dates))
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract legal citations from text"""
        citations = []
        
        for pattern in self.patterns["citation"]:
            matches = re.findall(pattern, text)
            citations.extend([match.strip() for match in matches if match.strip()])
        
        # Extract statutory citations
        statutory_patterns = [
            r"(\d+\s+U\.S\.C\.\s+§\s+\d+(?:\([a-z]\))?)",
            r"(Section\s+\d+\s+of\s+the\s+[A-Za-z\s]+\s+Act)"
        ]
        
        for pattern in statutory_patterns:
            matches = re.findall(pattern, text)
            citations.extend([match.strip() for match in matches if match.strip()])
        
        # Remove duplicates
        return list(set(citations))
    
    def _extract_case_law_metadata(self, text: str, metadata: Dict[str, Any]) -> None:
        """Extract case law specific metadata"""
        # Extract case name
        for pattern in self.patterns["case_name"]:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    if len(matches[0]) == 2:
                        metadata["case_name"] = f"{matches[0][0]} v. {matches[0][1]}"
                    else:
                        metadata["case_name"] = " ".join(matches[0])
                else:
                    metadata["case_name"] = matches[0]
                break
        
        # Extract court
        for pattern in self.patterns["court"]:
            matches = re.findall(pattern, text)
            if matches:
                metadata["court"] = matches[0]
                break
        
        # Extract judges
        judge_pattern = r"(?:Judge|Justice|Chief Judge|Chief Justice)\s+([A-Z][A-Za-z\s\.,]+)"
        matches = re.findall(judge_pattern, text)
        if matches:
            # Convert judges list to string to avoid ChromaDB metadata issues
            metadata["judges"] = ", ".join(list(set([match.strip() for match in matches if match.strip()])))
    
    def _extract_statute_metadata(self, text: str, metadata: Dict[str, Any]) -> None:
        """Extract statute specific metadata"""
        # Extract title/section
        title_patterns = [
            r"TITLE\s+(\d+)[\.\-—]\s*(.*?)(?:\n|$)",
            r"Title\s+(\d+)[\.\-—]\s*(.*?)(?:\n|$)",
            r"SECTION\s+(\d+)[\.\-—]\s*(.*?)(?:\n|$)",
            r"Section\s+(\d+)[\.\-—]\s*(.*?)(?:\n|$)"
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text)
            if matches:
                metadata["title_number"] = matches[0][0]
                metadata["title_name"] = matches[0][1].strip()
                break
        
        # Extract effective date
        date_patterns = [
            r"Effective Date[:\s]*([A-Za-z]+\s+\d+,\s+\d{4})",
            r"effective\s+(?:on|as of)\s+([A-Za-z]+\s+\d+,\s+\d{4})"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                metadata["effective_date"] = matches[0]
                break
    
    def _extract_regulation_metadata(self, text: str, metadata: Dict[str, Any]) -> None:
        """Extract regulation specific metadata"""
        # Extract CFR title/part
        cfr_patterns = [
            r"(\d+)\s+CFR\s+(?:Part\s+)?(\d+)(?:\.(\d+))?",
            r"Title\s+(\d+),\s+Code\s+of\s+Federal\s+Regulations,\s+(?:Part|§)\s+(\d+)(?:\.(\d+))?"
        ]
        
        for pattern in cfr_patterns:
            matches = re.findall(pattern, text)
            if matches:
                metadata["cfr_title"] = matches[0][0]
                metadata["cfr_part"] = matches[0][1]
                if len(matches[0]) > 2 and matches[0][2]:
                    metadata["cfr_section"] = matches[0][2]
                break
        
        # Extract agency
        agency_patterns = [
            r"([A-Z][A-Za-z\s]+(?:Department|Agency|Administration|Commission))",
            r"AGENCY:\s+(.*?)(?:\n|$)"
        ]
        
        for pattern in agency_patterns:
            matches = re.findall(pattern, text)
            if matches:
                metadata["agency"] = matches[0].strip()
                break
    
    def _calculate_quality_score(self, text: str, metadata: Dict[str, Any]) -> float:
        """Calculate document quality score based on metadata richness and content"""
        score = 0.0
        
        # Check for minimum content length
        word_count = metadata.get("word_count", 0)
        if word_count > 100:
            score += 0.2
        if word_count > 500:
            score += 0.2
        
        # Check for key metadata fields presence
        key_fields = ["title", "date", "document_type"]
        for field in key_fields:
            if field in metadata and metadata[field]:
                score += 0.1
        
        # Check for document type specific fields
        doc_type = metadata.get("document_type", "unknown")
        if doc_type == "case_law" or doc_type == "opinion":
            if "case_name" in metadata:
                score += 0.1
            if "court" in metadata:
                score += 0.1
            if "citation" in metadata:
                score += 0.1
        elif doc_type == "statute":
            if "title_number" in metadata:
                score += 0.15
            if "effective_date" in metadata:
                score += 0.15
        elif doc_type == "regulation":
            if "cfr_title" in metadata:
                score += 0.15
            if "agency" in metadata:
                score += 0.15
        
        # Add points for extracted entities and citations
        if "entities" in metadata and len(metadata["entities"]) > 0:
            score += min(0.1, len(metadata["entities"]) * 0.02)
        
        if "citations" in metadata and len(metadata["citations"]) > 0:
            score += min(0.1, len(metadata["citations"]) * 0.02)
        
        return min(1.0, score)
    
    def _normalize_metadata_values(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure metadata values are compatible with ChromaDB (str, int, float, bool)"""
        normalized = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                normalized[key] = value
            elif isinstance(value, list):
                normalized[key] = ", ".join(str(item) for item in value)
            elif isinstance(value, dict):
                normalized[key] = json.dumps(value)
            elif value is None:
                pass  # Skip None values
            else:
                normalized[key] = str(value)
        return normalized 