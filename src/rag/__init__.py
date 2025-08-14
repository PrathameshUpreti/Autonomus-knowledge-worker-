"""
RAG (Retrieval-Augmented Generation) Package - Complete Implementation
Simple, beginner-friendly RAG implementation for the autonomous knowledge-worker agent.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from src.confrig.settings import settings

logger = logging.getLogger(__name__)

class RAGConfig:
    """
    Complete configuration for RAG system components.
    Centralizes all RAG-related settings.
    """
    
    def __init__(self):
        # Vector Store Settings
        self.vector_store_path = Path(settings.vector_store_dir)
        self.collection_name = settings.vector_db_name
        self.vector_store_type = "chromadb"
        
        # Embedding Settings
        self.embedding_model_name = settings.embedding_model
        self.embedding_dimension = 384
        
        # Document Processing Settings
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.max_chunks_per_doc = 100
        
        # Retrieval Settings
        self.default_top_k = 5
        self.similarity_threshold = 0.7
        self.max_query_length = 500
        
        # Supported file formats
        self.supported_formats = [".txt", ".md", ".pdf", ".docx", ".html"]
        
        self.setup_directories()
        logger.info("🔍 RAG configuration initialized")
    
    def setup_directories(self):
        """Create necessary directories for RAG system"""
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
    
    def get_config_dict(self) -> Dict:
        """Get RAG configuration as dictionary"""
        return {
            "vector_store_path": str(self.vector_store_path),
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "top_k": self.default_top_k,
            "similarity_threshold": self.similarity_threshold
        }

# Global RAG configuration
rag_config = RAGConfig()

# Import all RAG components
from .embedding import EmbeddingModel, create_embedding_model
from .vector_store import VectorStore, create_vector_store
from .document_loader import DocumentLoader, create_document_loader
from .chunk_processor import ChunkProcessor, create_chunk_processor  # ✅ NEW
from .retriever import RAGRetriever, create_retriever  # ✅ NEW

class RAGSystem:
    """
    Complete RAG system that combines all components.
    Provides high-level interface for RAG operations.
    """
    
    def __init__(self):
        self.document_loader = create_document_loader()
        self.chunk_processor = create_chunk_processor()
        self.embedding_model = create_embedding_model()
        self.vector_store = create_vector_store()
        self.retriever = create_retriever()
        
        print("🎯 Complete RAG system initialized")
    
    def index_documents(self, directory_path: str) -> bool:
        """End-to-end document indexing"""
        try:
            # 1. Load documents
            documents = self.document_loader.load_directory(directory_path)
            if not documents:
                print("❌ No documents found to index")
                return False
            
            # 2. Process into chunks
            chunks = self.chunk_processor.process_multiple_documents(documents)
            if not chunks:
                print("❌ No chunks created from documents")
                return False
            
            # 3. Index chunks
            success = self.retriever.index_chunks(chunks)
            return success
            
        except Exception as e:
            logger.error(f"Error in document indexing: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search indexed documents"""
        return self.retriever.retrieve(query, top_k=top_k)

def setup_rag_system() -> RAGSystem:
    """Setup complete RAG system"""
    return RAGSystem()

__all__ = [
    'RAGConfig',
    'rag_config',
    'EmbeddingModel',
    'VectorStore', 
    'DocumentLoader',
    'ChunkProcessor',  
    'RAGRetriever',    # ✅ NEW
    'RAGSystem',       # ✅ NEW
    'create_embedding_model',
    'create_vector_store',
    'create_document_loader',
    'create_chunk_processor',  # ✅ NEW
    'create_retriever',        # ✅ NEW
    'setup_rag_system'         # ✅ NEW
]
