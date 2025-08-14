"""
Embeddings Model for RAG System
Converts text into vector representations for semantic search.
"""
import logging
from typing import List,Dict,Optional,Union
import numpy as np
from . import rag_config

logger=logging.getLogger(__name__)

class EmbeddingModel:
    """
    Embedding model using sentence-transformers.
    Converts text into numerical vectors for similarity search.
    """

    def __init__(self,model_name:Optional[str]=None):
        self.model_name=model_name or rag_config.embedding_model_name
        self.model=None
        self.dimension=rag_config.embedding_dimension

        self.load_model()

    def load_model(self):
        """Load the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer

            print(f"🤖 Loading embedding model: {self.model_name}")

            self.model=SentenceTransformer(self.model_name)

            self.dimension=self.model.get_sentence_embedding_dimension()

            print(f"✅ Embedding model loaded successfully")
            print(f"📐 Vector dimension: {self.dimension}")

        except Exception as e:
            print("❌ sentence-transformers not installed. Run: pip install sentence-transformers")
            raise
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            raise
    
    def encode_text(self,text:Union[str,List[str]])->np.ndarray:
        """
        Convert text into vector embeddings.
        
        Args:
            text: Single text string or list of text strings
            
        Returns:
            NumPy array of embeddings
        """

        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            if isinstance(text,str):
                text=[text]
            
            cleaned_text=[self.clean_text(t) for t in text]

            embedding = self.model.encode(
                cleaned_text,
                convert_to_numpy=True,
                show_progress_bar=len(cleaned_text)>10

            )
            logger.debug(f"🔢 Generated embeddings for {len(text)} texts")
            return embedding
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            raise

    def encode_query(self,query:str)->np.ndarray:
        """
        Encode a search query into embeddings.
        
        Args:
            query: Search query text
        
        Returns:
            Query embedding vector
        """
        if len(query)> rag_config.max_query_length:
            query=query[:rag_config.max_query_length]
        
        return self.encode_text(query)[0]
    
    def calculate_similarity(self,query_embedding:np.ndarray,doc_embedding:np.ndarray)-> np.ndarray:
        """
        Calculate cosine similarity between query and document embeddings.
        
        Args:
            query_embedding: Query vector
            doc_embeddings: Document vectors
            
        Returns:
            Similarity scores
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            if query_embedding.ndim == 1:
                query_embedding=query_embedding.reshape(1,-1)

            similarieties= cosine_similarity(query_embedding,doc_embedding)[0]
            return similarieties
        except ImportError:
            def cosine_sim(a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            
            return np.array([cosine_sim(query_embedding, doc_emb) for doc_emb in doc_embedding])
        

    def clean_text(self,text:str)->str:
        """Clean text for better embedding"""

        if not text or not text.strip():
            return ""
        
        text=text.strip()
        text="".join(text.split())
        return text
    
    def get_model_info(self) ->dict:
        """Get information about the embedding model"""
        return{
            "model_name": self.model_name,
            "dimension": self.dimension,
            "max_seq_length": getattr(self.model, 'max_seq_length', 'Unknown'),
            "is_loaded": self.model is not None

        }
def create_embedding_model(model_name:Optional[str]=None)-> EmbeddingModel:
        """Factory function to create embedding model"""
        return EmbeddingModel(model_name)
    














    

