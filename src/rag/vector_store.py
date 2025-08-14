"""
Vector Store for RAG System
Stores and retrieves document embeddings using ChromaDB.
"""
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
from pathlib import Path
from . import rag_config

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Simple vector store using ChromaDB for storing and retrieving document embeddings.
    """
    def __init__(self, collection_name: Optional[str] = None):
        self.collection_name = collection_name or rag_config.collection_name
        self.db_path = rag_config.vector_store_path
        self.client = None
        self.collection = None
        self.setup_database()

    def setup_database(self):
        """Initialize ChromaDB client and collection"""
        try:
            import chromadb
            from chromadb.config import Settings

            print(f"🗃️ Setting up vector store: {self.collection_name}")

            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "RAG document embeddings for autonomous agent"}
            )
            
            print(f"✅ Vector store ready: {self.collection.count()} documents indexed")
            
        except ImportError:
            print("❌ chromadb not installed. Run: pip install chromadb")
            raise
        except Exception as e:
            print(f"❌ Error setting up vector store: {e}")
            raise

    def _flatten_metadata(self, metadata: Dict) -> Dict:
        """
        Flatten nested metadata dictionary for ChromaDB compatibility.
        ChromaDB only accepts str, int, float, bool, or None values.
        """
        flattened = {}
        
        def _flatten_recursive(obj, prefix=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}_{key}" if prefix else key
                    if isinstance(value, dict):
                        _flatten_recursive(value, new_key)
                    elif isinstance(value, (str, int, float, bool)) or value is None:
                        flattened[new_key] = value
                    elif isinstance(value, list):
                        # Convert lists to comma-separated strings
                        flattened[new_key] = ", ".join(str(item) for item in value)
                    else:
                        # Convert other types to string
                        flattened[new_key] = str(value)
            else:
                flattened[prefix] = obj if isinstance(obj, (str, int, float, bool)) or obj is None else str(obj)
        
        _flatten_recursive(metadata)
        
        # Ensure all values are ChromaDB-compatible types
        for key, value in flattened.items():
            if not isinstance(value, (str, int, float, bool)) and value is not None:
                flattened[key] = str(value)
        
        return flattened

    def add_documents(self, 
                     documents: List[str], 
                     embeddings: np.ndarray, 
                     metadata: List[Dict],
                     ids: Optional[List[str]] = None) -> bool:
        """
        Add documents and their embeddings to the vector store.
        
        Args:
            documents: List of document text chunks
            embeddings: Document embeddings as numpy array
            metadata: List of metadata dictionaries for each document
            ids: Optional list of document IDs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.collection:
                raise RuntimeError("Vector store not initialized")
            
            if ids is None:
                existing_count = self.collection.count()
                ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

            embeddings_list = embeddings.tolist()

            # ✅ FIXED: Flatten metadata for ChromaDB compatibility
            flattened_metadata = []
            for meta in metadata:
                if isinstance(meta, dict):
                    flattened_meta = self._flatten_metadata(meta)
                    flattened_metadata.append(flattened_meta)
                else:
                    # If it's not a dict, convert to string
                    flattened_metadata.append({"content": str(meta)})

            print(f"📋 Flattened metadata for {len(flattened_metadata)} documents")

            self.collection.add(
                documents=documents,
                embeddings=embeddings_list,
                metadatas=flattened_metadata,  # ✅ Now using flattened metadata
                ids=ids
            )
            print(f"✅ Added {len(documents)} documents to vector store")
            logger.info(f"Added {len(documents)} documents to collection {self.collection_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding documents to vector store: {e}")
            logger.error(f"Error adding documents: {e}")
            return False  # ✅ Fixed: was missing False
    
    def search_similar(self, 
                      query_embedding: np.ndarray, 
                      top_k: int = 5,
                      similarity_threshold: float = 0.7) -> List[Dict]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar documents with metadata and scores
        """
        try:
            if not self.collection:
                raise RuntimeError("Vector store not initialized")
            query_embedding_list = query_embedding.tolist()
            
            # Perform similarity search
            results = self.collection.query(
                query_embeddings=[query_embedding_list],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process results
            similar_docs = []
            
            if results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
                distances = results['distances'][0] if results['distances'] else [0] * len(documents)
                
                for doc, metadata, distance in zip(documents, metadatas, distances):
                    # Convert distance to similarity score (ChromaDB uses L2 distance)
                    similarity = 1 / (1 + distance)
                    
                    if similarity >= similarity_threshold:
                        similar_docs.append({
                            'document': doc,
                            'metadata': metadata,
                            'similarity_score': similarity,
                            'distance': distance
                        })
            
            logger.debug(f"🔍 Found {len(similar_docs)} similar documents")
            return similar_docs
            
        except Exception as e:
            logger.error(f"❌ Error searching vector store: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store collection"""
        try:
            if not self.collection:
                return {"error": "Vector store not initialized"}
            
            count = self.collection.count()

            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "database_path": str(self.db_path),
                "status": "ready" if count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
           
    def delete_document(self, ids: List[str]) -> bool:
        """Delete specific documents from the vector store"""
        try:
            if not self.collection:
                raise RuntimeError("Vector store not initialized")
            self.collection.delete(ids=ids)
            print(f"🗑️ Deleted {len(ids)} documents from vector store")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False
          
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            if not self.collection:
                raise RuntimeError("Vector store not initialized")

            # Delete and create the new collection
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "RAG document embeddings for autonomous agent"}     
            )
            print(f"🗑️ Cleared vector store collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False

def create_vector_store(collection_name: Optional[str] = None) -> VectorStore:
    """Factory function to create vector store"""
    return VectorStore(collection_name)
