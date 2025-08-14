"""
RAG Retriever for semantic search and document retrieval.
Handles query processing and similarity-based document retrieval.
"""

import logging
from typing import List, Dict, Optional, Union
import numpy as np
from . import rag_config
from .embedding import create_embedding_model
from .vector_store import create_vector_store

logger = logging.getLogger(__name__)

class RAGRetriever:
    """
    RAG retriever that handles semantic search and document retrieval.
    Combines embedding model and vector store for intelligent document search.
    """
    
    def __init__(self, 
                 collection_name: Optional[str] = None,
                 embedding_model_name: Optional[str] = None):
        self.collection_name = collection_name or rag_config.collection_name
        self.embedding_model_name = embedding_model_name or rag_config.embedding_model_name
        
        # Initialize components
        self.embedding_model = None
        self.vector_store = None
        self.is_ready = False
        
        # Retrieval settings
        self.default_top_k = rag_config.default_top_k
        self.similarity_threshold = rag_config.similarity_threshold
        self.max_query_length = rag_config.max_query_length
        
        self.setup_retriever()
    
    def setup_retriever(self):
        """Initialize embedding model and vector store"""
        try:
            print(f"🔍 Setting up RAG retriever")
            
            # Initialize embedding model
            print(f"🤖 Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = create_embedding_model(self.embedding_model_name)
            
            # Initialize vector store
            print(f"🗃️ Connecting to vector store: {self.collection_name}")
            self.vector_store = create_vector_store(self.collection_name)
            
            self.is_ready = True
            print(f"✅ RAG retriever ready for queries")
            
        except Exception as e:
            logger.error(f"Error setting up RAG retriever: {e}")
            print(f"❌ RAG retriever setup failed: {e}")
            self.is_ready = False
    
    def index_chunks(self, chunks: List[Dict]) -> bool:
        """
        Index chunks into the vector store for retrieval.
        
        Args:
            chunks: List of chunk dictionaries with 'content' and 'metadata'
            
        Returns:
            True if indexing successful, False otherwise
        """
        if not self.is_ready:
            logger.error("RAG retriever not ready - setup failed")
            return False
        
        if not chunks:
            logger.warning("No chunks provided for indexing")
            return False
        
        try:
            print(f"📇 Indexing {len(chunks)} chunks into vector store")
            
            # Extract text content and metadata
            texts = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                if 'content' not in chunk:
                    logger.warning("Chunk missing content field, skipping")
                    continue
                
                content = chunk['content']
                if not content or not content.strip():
                    continue
                
                texts.append(content)
                metadatas.append(chunk.get('metadata', {}))
                
                # Generate ID from metadata or create one
                chunk_id = chunk.get('metadata', {}).get('chunk_id')
                if not chunk_id:
                    chunk_id = f"chunk_{len(ids)}"
                ids.append(chunk_id)
            
            if not texts:
                logger.error("No valid text content found in chunks")
                return False
            
            # Generate embeddings for all texts
            print(f"🔢 Generating embeddings for {len(texts)} chunks")
            embeddings = self.embedding_model.encode_text(texts)
            
            # Add to vector store
            success = self.vector_store.add_documents(
                documents=texts,
                embeddings=embeddings,
                metadata=metadatas,
                ids=ids
            )
            
            if success:
                print(f"✅ Successfully indexed {len(texts)} chunks")
                return True
            else:
                print(f"❌ Failed to index chunks")
                return False
                
        except Exception as e:
            logger.error(f"Error indexing chunks: {e}")
            print(f"❌ Indexing failed: {e}")
            return False
    
    def retrieve(self, 
                query: str, 
                top_k: Optional[int] = None,
                similarity_threshold: Optional[float] = None,
                filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant document chunks with similarity scores
        """
        if not self.is_ready:
            logger.error("RAG retriever not ready")
            return []
        
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        # Set defaults
        top_k = top_k or self.default_top_k
        similarity_threshold = similarity_threshold or self.similarity_threshold
        
        try:
            # Clean and truncate query
            cleaned_query = self._clean_query(query)
            if len(cleaned_query) > self.max_query_length:
                cleaned_query = cleaned_query[:self.max_query_length]
                logger.warning(f"Query truncated to {self.max_query_length} characters")
            
            print(f"🔍 Searching for: '{cleaned_query[:100]}{'...' if len(cleaned_query) > 100 else ''}'")
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode_query(cleaned_query)
            
            # Search vector store
            similar_docs = self.vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            # Process and rank results
            processed_results = self._process_search_results(
                similar_docs, 
                query, 
                filter_metadata
            )
            
            print(f"✅ Found {len(processed_results)} relevant documents")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            print(f"❌ Retrieval failed: {e}")
            return []
    
    def retrieve_with_context(self, 
                             query: str, 
                             conversation_history: Optional[List[str]] = None,
                             **kwargs) -> Dict:
        """
        Retrieve documents with additional context and metadata.
        
        Args:
            query: Search query
            conversation_history: Previous conversation for context
            **kwargs: Additional arguments for retrieve()
            
        Returns:
            Dictionary with results, query info, and retrieval metadata
        """
        # Enhance query with conversation context if provided
        enhanced_query = self._enhance_query_with_context(query, conversation_history)
        
        # Perform retrieval
        results = self.retrieve(enhanced_query, **kwargs)
        
        # Prepare response with metadata
        return {
            "query": query,
            "enhanced_query": enhanced_query if enhanced_query != query else None,
            "results": results,
            "total_results": len(results),
            "retrieval_metadata": {
                "embedding_model": self.embedding_model_name,
                "collection_name": self.collection_name,
                "similarity_threshold": kwargs.get('similarity_threshold', self.similarity_threshold),
                "top_k": kwargs.get('top_k', self.default_top_k)
            }
        }
    
    def _process_search_results(self, 
                               similar_docs: List[Dict], 
                               original_query: str,
                               filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """Process and filter search results"""
        processed_results = []
        
        for doc in similar_docs:
            # Apply metadata filters if provided
            if filter_metadata:
                doc_metadata = doc.get('metadata', {})
                should_include = True
                
                for key, value in filter_metadata.items():
                    if key not in doc_metadata or doc_metadata[key] != value:
                        should_include = False
                        break
                
                if not should_include:
                    continue
            
            # Create result with enhanced information
            result = {
                'content': doc.get('document', ''),
                'metadata': doc.get('metadata', {}),
                'similarity_score': doc.get('similarity_score', 0.0),
                'distance': doc.get('distance', 0.0),
                'relevance_rank': len(processed_results) + 1,
                'query_match_info': self._analyze_query_match(
                    doc.get('document', ''), 
                    original_query
                )
            }
            
            processed_results.append(result)
        
        return processed_results
    
    def _enhance_query_with_context(self, 
                                   query: str, 
                                   conversation_history: Optional[List[str]] = None) -> str:
        """Enhance query with conversation context"""
        if not conversation_history:
            return query
        
        # Simple context enhancement - add recent context
        recent_context = " ".join(conversation_history[-2:])  # Last 2 messages
        
        if len(recent_context) > 200:  # Limit context length
            recent_context = recent_context[:200]
        
        enhanced_query = f"Context: {recent_context}\nQuery: {query}"
        return enhanced_query
    
    def _analyze_query_match(self, document: str, query: str) -> Dict:
        """Analyze how the query matches the document"""
        doc_lower = document.lower()
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Find exact word matches
        exact_matches = [word for word in query_words if word in doc_lower]
        
        # Calculate match statistics
        match_info = {
            'exact_word_matches': len(exact_matches),
            'total_query_words': len(query_words),
            'match_percentage': len(exact_matches) / len(query_words) if query_words else 0,
            'matched_words': exact_matches
        }
        
        return match_info
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize query text"""
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Remove special characters that might interfere with search
        import re
        query = re.sub(r'[^\w\s.,!?]', ' ', query)
        
        return query.strip()
    
    def get_retriever_stats(self) -> Dict:
        """Get statistics about the retriever and vector store"""
        if not self.is_ready:
            return {"status": "not_ready"}
        
        vector_stats = self.vector_store.get_collection_stats()
        embedding_info = self.embedding_model.get_model_info()
        
        return {
            "status": "ready",
            "vector_store": vector_stats,
            "embedding_model": embedding_info,
            "retrieval_settings": {
                "default_top_k": self.default_top_k,
                "similarity_threshold": self.similarity_threshold,
                "max_query_length": self.max_query_length
            }
        }
    
    def clear_index(self) -> bool:
        """Clear all documents from the vector store"""
        if not self.is_ready:
            return False
        
        try:
            success = self.vector_store.clear_collection()
            if success:
                print("🗑️ Vector store index cleared")
            return success
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            return False

def create_retriever(collection_name: Optional[str] = None,
                    embedding_model_name: Optional[str] = None) -> RAGRetriever:
    """Factory function to create RAG retriever"""
    return RAGRetriever(collection_name, embedding_model_name)
