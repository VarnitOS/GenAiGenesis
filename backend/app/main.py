from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import services
from services.embedding_service import embedding_service
from services.document_service import document_service
from utils.cohere_client import cohere_client

# Create FastAPI app
app = FastAPI(
    title="Legal AI Assistant",
    description="AI-powered legal advisory system using Cohere",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    store_type: Optional[str] = "case_law"
    num_results: Optional[int] = 5

class DocumentRequest(BaseModel):
    text: str
    metadata: Optional[Dict] = None

class EmbeddingResponse(BaseModel):
    embedding: List[float]

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Legal AI Assistant API"}

@app.post("/api/query/embed")
async def embed_query(query: str):
    """Generate an embedding for a query"""
    try:
        embedding = embedding_service.direct_embed(query, input_type="search_query")
        return {"embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query/search")
async def search_query(request: QueryRequest):
    """Search for relevant documents"""
    try:
        results = embedding_service.search(
            query=request.query,
            store_type=request.store_type,
            k=request.num_results
        )
        
        # Format results
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return {"results": formatted_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/document/process")
async def process_document(request: DocumentRequest):
    """Process and store a document"""
    try:
        result = document_service.process_document(request.text, request.metadata)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/document/analyze")
async def analyze_document(request: DocumentRequest):
    """Analyze a document and extract key information"""
    try:
        result = document_service.analyze_document(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 