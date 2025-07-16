"""
FastAPI application for the Technical Documentation Assistant.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from pydantic import BaseModel
import uvicorn

from .config import settings
from .document_processor import DocumentProcessor
from .vector_database import VectorDatabase, DocumentChunker
from .groq_client import GroqClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-driven system for parsing technical documentation and providing contextual answers"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
doc_processor = DocumentProcessor()
vector_db = VectorDatabase()
chunker = DocumentChunker()
groq_client = GroqClient()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Pydantic models
class QueryRequest(BaseModel):
    question: str
    language: Optional[str] = None
    max_results: Optional[int] = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
    tokens_used: int
    model: str


class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    processed_files: int
    total_chunks: int


class DatabaseStats(BaseModel):
    total_documents: int
    collection_name: str
    embedding_model: str


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/query", response_model=QueryResponse)
async def query_documentation(query: QueryRequest):
    """
    Query the documentation with a natural language question.
    """
    try:
        if not query.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Search for relevant documents
        relevant_docs = vector_db.search(
            query=query.question,
            n_results=query.max_results or 5
        )
        
        if not relevant_docs:
            return QueryResponse(
                answer="I couldn't find any relevant documentation for your question. Please make sure you have uploaded some documentation files first.",
                sources=[],
                confidence=0.0,
                tokens_used=0,
                model=settings.groq_model
            )
        
        # Generate answer
        if query.language or "code" in query.question.lower() or "example" in query.question.lower():
            # Generate code example
            result = groq_client.generate_code_example(
                question=query.question,
                context_documents=relevant_docs,
                language=query.language
            )
            return QueryResponse(
                answer=result["code_example"],
                sources=result["sources"],
                confidence=vector_db.search(query.question, 1)[0].get('score', 0.0) if relevant_docs else 0.0,
                tokens_used=result["tokens_used"],
                model=result["model"]
            )
        else:
            # Generate regular answer
            result = groq_client.generate_answer(
                question=query.question,
                context_documents=relevant_docs
            )
            return QueryResponse(
                answer=result["answer"],
                sources=result["sources"],
                confidence=result["confidence"],
                tokens_used=result["tokens_used"],
                model=result["model"]
            )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/api/upload", response_model=DocumentUploadResponse)
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    urls: Optional[str] = Form(None)
):
    """
    Upload and process documentation files or URLs.
    """
    try:
        processed_files = 0
        total_chunks = 0
        
        # Process uploaded files
        if files:
            for file in files:
                if file.filename:
                    # Save uploaded file temporarily
                    temp_path = f"temp_{file.filename}"
                    with open(temp_path, "wb") as buffer:
                        content = await file.read()
                        buffer.write(content)
                    
                    # Process the file
                    result = doc_processor.process_file(temp_path)
                    if result['content']:
                        # Chunk the document
                        chunks = chunker.chunk_document(result)
                        if chunks:
                            # Add to vector database
                            vector_db.add_documents(chunks)
                            processed_files += 1
                            total_chunks += len(chunks)
                    
                    # Clean up temp file
                    os.remove(temp_path)
        
        # Process URLs if provided
        if urls:
            url_list = [url.strip() for url in urls.split('\n') if url.strip()]
            for url in url_list:
                result = doc_processor.process_url(url)
                if result['content']:
                    chunks = chunker.chunk_document(result)
                    if chunks:
                        vector_db.add_documents(chunks)
                        processed_files += 1
                        total_chunks += len(chunks)
        
        return DocumentUploadResponse(
            success=True,
            message=f"Successfully processed {processed_files} files/URLs with {total_chunks} chunks",
            processed_files=processed_files,
            total_chunks=total_chunks
        )
    
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading documents: {str(e)}")


@app.post("/api/upload-directory")
async def upload_directory(directory_path: str = Form(...)):
    """
    Process all supported files in a directory.
    """
    try:
        if not os.path.exists(directory_path):
            raise HTTPException(status_code=400, detail="Directory path does not exist")
        
        # Process directory
        results = doc_processor.process_directory(directory_path)
        
        processed_files = 0
        total_chunks = 0
        
        for result in results:
            if result['content']:
                chunks = chunker.chunk_document(result)
                if chunks:
                    vector_db.add_documents(chunks)
                    processed_files += 1
                    total_chunks += len(chunks)
        
        return DocumentUploadResponse(
            success=True,
            message=f"Successfully processed {processed_files} files from directory with {total_chunks} chunks",
            processed_files=processed_files,
            total_chunks=total_chunks
        )
    
    except Exception as e:
        logger.error(f"Error processing directory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing directory: {str(e)}")


@app.get("/api/stats", response_model=DatabaseStats)
async def get_database_stats():
    """
    Get statistics about the current knowledge base.
    """
    try:
        stats = vector_db.get_collection_stats()
        return DatabaseStats(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.delete("/api/reset")
async def reset_database():
    """
    Reset the entire knowledge base (use with caution).
    """
    try:
        success = vector_db.reset_database()
        if success:
            return {"success": True, "message": "Database reset successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset database")
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")


@app.get("/api/search")
async def search_documents(q: str, limit: int = 5):
    """
    Search for documents without generating an answer.
    """
    try:
        results = vector_db.search(query=q, n_results=limit)
        return {
            "query": q,
            "results": [
                {
                    "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    "source": doc["metadata"].get("source", "Unknown"),
                    "score": doc["score"]
                }
                for doc in results
            ]
        }
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
