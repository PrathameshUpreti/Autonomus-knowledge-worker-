"""
Chunk Processor for RAG System
Breaks documents into manageable, overlapping chunks for better retrieval.
"""

import logging
from typing import List, Dict, Optional, Union
import re
from . import rag_config

logger = logging.getLogger(__name__)

class ChunkProcessor:
    """
    Simple document chunk processor that breaks text into overlapping segments.
    Designed for optimal RAG performance with semantic preservation.
    """
    
    def __init__(self, 
                 chunk_size: Optional[int] = None,
                 chunk_overlap: Optional[int] = None,
                 preserve_sentences: bool = True):
        self.chunk_size = chunk_size or rag_config.chunk_size
        self.chunk_overlap = chunk_overlap or rag_config.chunk_overlap
        self.preserve_sentences = preserve_sentences
        self.max_chunks_per_doc = rag_config.max_chunks_per_doc
        
        print(f"📄 Chunk processor initialized")
        print(f"📏 Chunk size: {self.chunk_size} characters")
        print(f"🔗 Overlap: {self.chunk_overlap} characters")
        print(f"📝 Preserve sentences: {self.preserve_sentences}")
    
    def process_document(self, document: Dict) -> List[Dict]:
        """
        Process a document into chunks with metadata.
        
        Args:
            document: Document dict with 'content', 'metadata', and 'source'
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not document or 'content' not in document:
            logger.error("Invalid document format")
            return []
        
        content = document['content']
        if not content or not content.strip():
            logger.warning("Document has no content to chunk")
            return []
        
        try:
            print(f"📄 Processing document: {document.get('source', 'Unknown')}")
            
            # Clean the text
            cleaned_text = self._clean_text(content)
            
            # Create chunks
            if self.preserve_sentences:
                chunks = self._chunk_by_sentences(cleaned_text)
            else:
                chunks = self._chunk_by_characters(cleaned_text)
            
            # Add metadata to chunks
            processed_chunks = []
            source_metadata = document.get('metadata', {})
            source_path = document.get('source', 'unknown')
            
            for i, chunk_text in enumerate(chunks):
                if len(chunk_text.strip()) < 50:  # Skip very small chunks
                    continue
                
                chunk_metadata = {
                    'chunk_id': f"{source_path}_chunk_{i}",
                    'chunk_index': i,
                    'source_document': source_path,
                    'source_metadata': source_metadata,
                    'chunk_size': len(chunk_text),
                    'word_count': len(chunk_text.split()),
                    'created_at': self._get_timestamp()
                }
                
                chunk = {
                    'content': chunk_text.strip(),
                    'metadata': chunk_metadata
                }
                
                processed_chunks.append(chunk)
                
                # Limit chunks per document
                if len(processed_chunks) >= self.max_chunks_per_doc:
                    logger.warning(f"Reached max chunks limit ({self.max_chunks_per_doc}) for document")
                    break
            
            print(f"✅ Created {len(processed_chunks)} chunks from document")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return []
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """
        Chunk text while preserving sentence boundaries.
        More intelligent chunking that maintains semantic coherence.
        """
        try:
            # Try to use nltk for better sentence tokenization
            import nltk
            nltk.download('punkt', quiet=True)
            sentences = nltk.sent_tokenize(text)
        except ImportError:
            # Fallback: simple sentence splitting
            sentences = self._simple_sentence_split(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Start new chunk with current sentence
                current_chunk = sentence
                
                # If single sentence is too long, split it
                if len(current_chunk) > self.chunk_size:
                    char_chunks = self._chunk_by_characters(current_chunk)
                    chunks.extend(char_chunks[:-1])  # Add all but last
                    current_chunk = char_chunks[-1] if char_chunks else ""
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        # Add overlap between chunks
        return self._add_overlap(chunks)
    
    def _chunk_by_characters(self, text: str) -> List[str]:
        """
        Simple character-based chunking with overlap.
        Used as fallback or when sentence preservation is disabled.
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at word boundaries if possible
            if end < text_length and not text[end].isspace():
                # Find last space before chunk_size
                last_space = chunk_text.rfind(' ')
                if last_space > self.chunk_size * 0.8:  # If space is reasonably close
                    chunk_text = chunk_text[:last_space]
                    end = start + last_space
            
            chunks.append(chunk_text)
            
            # Calculate next start position with overlap
            if end >= text_length:
                break
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between sentence-based chunks"""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = [chunks[0]]  # First chunk as-is
        
        for i in range(1, len(chunks)):
            current_chunk = chunks[i]
            previous_chunk = chunks[i-1]
            
            # Get overlap text from previous chunk
            overlap_text = previous_chunk[-self.chunk_overlap:] if len(previous_chunk) > self.chunk_overlap else previous_chunk
            
            # Find good break point in overlap
            overlap_sentences = overlap_text.split('. ')
            if len(overlap_sentences) > 1:
                # Use last complete sentence for overlap
                overlap_text = overlap_sentences[-1]
            
            # Combine overlap with current chunk
            overlapped_chunk = overlap_text + " " + current_chunk
            overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks
    
    def _simple_sentence_split(self, text: str) -> List[str]:
        """Simple sentence splitting fallback when nltk is not available"""
        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Filter very short sentences
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better chunking"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s.,!?;:()\-"]', ' ', text)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def process_multiple_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Process multiple documents into chunks.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Flat list of all chunks from all documents
        """
        all_chunks = []
        
        print(f"📚 Processing {len(documents)} documents into chunks")
        
        for i, document in enumerate(documents):
            print(f"📄 Processing document {i+1}/{len(documents)}")
            chunks = self.process_document(document)
            all_chunks.extend(chunks)
        
        print(f"✅ Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def get_chunk_stats(self, chunks: List[Dict]) -> Dict:
        """Get statistics about processed chunks"""
        if not chunks:
            return {"total_chunks": 0}
        
        chunk_sizes = [len(chunk['content']) for chunk in chunks]
        word_counts = [len(chunk['content'].split()) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "avg_word_count": sum(word_counts) / len(word_counts),
            "total_content_length": sum(chunk_sizes)
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")

def create_chunk_processor(chunk_size: Optional[int] = None,
                          chunk_overlap: Optional[int] = None,
                          preserve_sentences: bool = True) -> ChunkProcessor:
    """Factory function to create chunk processor"""
    return ChunkProcessor(chunk_size, chunk_overlap, preserve_sentences)
