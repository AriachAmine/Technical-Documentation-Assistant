"""
Vector database management using ChromaDB for semantic search and retrieval.
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import uuid

from .config import settings

logger = logging.getLogger(__name__)


class VectorDatabase:
    """Manages the vector database for semantic search and retrieval."""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory,
                settings=ChromaSettings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="documentation_chunks",
                metadata={"description": "Technical documentation chunks with embeddings"}
            )
            
            logger.info(f"Vector database initialized with {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Error initializing vector database: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document dictionaries with content and metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return False
            
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            metadatas = []
            documents_text = []
            
            for doc in documents:
                # Generate unique ID
                doc_id = str(uuid.uuid4())
                ids.append(doc_id)
                
                # Extract content and create embedding
                content = doc.get('content', '')
                if not content:
                    logger.warning(f"Empty content for document: {doc.get('source', 'unknown')}")
                    continue
                
                # Create embedding
                embedding = self.embedding_model.encode(content).tolist()
                embeddings.append(embedding)
                
                # Prepare metadata
                metadata = {
                    'source': doc.get('source', ''),
                    'status': doc.get('status', ''),
                    'chunk_index': doc.get('chunk_index', 0),
                    'total_chunks': doc.get('total_chunks', 1),
                    'doc_type': doc.get('doc_type', 'unknown'),
                    **doc.get('metadata', {})
                }
                metadatas.append(metadata)
                documents_text.append(content)
            
            if not ids:
                logger.warning("No valid documents to add after processing")
                return False
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents_text,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(ids)} documents to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector database: {str(e)}")
            return False
    
    def search(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using semantic similarity.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant document chunks with scores
        """
        try:
            if not query:
                return []
            
            # Create query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                result = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': 1 - results['distances'][0][i],  # Convert distance to similarity score
                    'distance': results['distances'][0][i]
                }
                formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} relevant documents for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database collection."""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection.name,
                'embedding_model': settings.embedding_model
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}
    
    def delete_collection(self) -> bool:
        """Delete the entire collection (use with caution)."""
        try:
            self.client.delete_collection(name="documentation_chunks")
            logger.info("Collection deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            return False
    
    def reset_database(self) -> bool:
        """Reset the entire database (use with caution)."""
        try:
            self.client.reset()
            self._initialize()
            logger.info("Database reset successfully")
            return True
        except Exception as e:
            logger.error(f"Error resetting database: {str(e)}")
            return False


class DocumentChunker:
    """Handles document chunking for efficient processing and retrieval."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split a document into chunks for processing.
        
        Args:
            document: Document dictionary with content and metadata
            
        Returns:
            List of document chunks
        """
        content = document.get('content', '')
        if not content:
            return []
        
        # Split content into chunks
        chunks = self._split_text(content)
        
        # Create chunk documents
        chunk_documents = []
        for i, chunk in enumerate(chunks):
            chunk_doc = {
                'content': chunk,
                'source': document.get('source', ''),
                'status': document.get('status', ''),
                'chunk_index': i,
                'total_chunks': len(chunks),
                'doc_type': self._determine_doc_type(document.get('source', '')),
                'metadata': {
                    **document.get('metadata', {}),
                    'original_length': len(content),
                    'chunk_length': len(chunk)
                }
            }
            chunk_documents.append(chunk_doc)
        
        return chunk_documents
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                search_start = max(start + self.chunk_size - 100, start)
                search_end = min(end + 100, len(text))
                
                for punct in ['. ', '.\n', '!\n', '?\n']:
                    last_punct = text.rfind(punct, search_start, search_end)
                    if last_punct != -1:
                        end = last_punct + len(punct)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def _determine_doc_type(self, source: str) -> str:
        """Determine document type from source."""
        source_lower = source.lower()
        
        if any(ext in source_lower for ext in ['.md', '.markdown']):
            return 'markdown'
        elif any(ext in source_lower for ext in ['.html', '.htm']):
            return 'html'
        elif '.pdf' in source_lower:
            return 'pdf'
        elif any(ext in source_lower for ext in ['.json', '.yaml', '.yml']):
            if 'openapi' in source_lower or 'swagger' in source_lower:
                return 'api_spec'
            return 'config'
        elif source_lower.startswith('http'):
            return 'web'
        else:
            return 'text'
