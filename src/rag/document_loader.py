"""
Document Loader for RAG System
Loads and processes various document formats for the knowledge base.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
from . import rag_config
from src.tools import get_tool

logger = logging.getLogger(__name__)

class DocumentLoader:
    """
    Simple document loader that processes various file formats for RAG indexing.
    Uses existing tools for document processing.
    """
    
    def __init__(self):
        self.supported_formats = rag_config.supported_formats
        
        # Get document processing tools
        self.document_processor = get_tool("document_processor")
        self.pdf_reader = get_tool("pdf_reader")
        
        print(f"📄 Document loader initialized")
        print(f"📋 Supported formats: {', '.join(self.supported_formats)}")
    
    def load_document(self, file_path: Union[str, Path]) -> Optional[Dict]:
        """
        Load a single document and extract its content.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary with document content and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        if file_path.suffix.lower() not in self.supported_formats:
            logger.warning(f"Unsupported file format: {file_path.suffix}")
            return None
        
        try:
            print(f"📖 Loading document: {file_path.name}")
            
            # Use appropriate tool based on file type
            if file_path.suffix.lower() == '.pdf':
                result = self.pdf_reader.execute(file_path)
                content = result.get('text_content', '') if result else ''
            else:
                result = self.document_processor.execute(file_path, 'extract')
                content = result.get('content', '') if result else ''
            
            if not content:
                logger.warning(f"No content extracted from: {file_path}")
                return None
            
            # Create document metadata
            metadata = {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'file_type': file_path.suffix.lower(),
                'file_size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
                'content_length': len(content),
                'word_count': len(content.split()),
                'loaded_at': self._get_timestamp()
            }
            
            # Add PDF-specific metadata if available
            if result and file_path.suffix.lower() == '.pdf':
                pdf_metadata = result.get('metadata', {})
                metadata.update({
                    'author': pdf_metadata.get('author', ''),
                    'title': pdf_metadata.get('title', ''),
                    'total_pages': pdf_metadata.get('total_pages', 0)
                })
            
            document = {
                'content': content,
                'metadata': metadata,
                'source': str(file_path)
            }
            
            print(f"✅ Loaded document: {file_path.name} ({len(content)} characters)")
            return document
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            return None
    
    def load_directory(self, directory_path: Union[str, Path], 
                      recursive: bool = True) -> List[Dict]:
        """
        Load all supported documents from a directory.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to search subdirectories
            
        Returns:
            List of loaded documents
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return []
        
        print(f"📁 Loading documents from: {directory_path}")
        
        documents = []
        
        # Find all supported files
        if recursive:
            file_pattern = "**/*"
        else:
            file_pattern = "*"
        
        for file_path in directory_path.glob(file_pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                document = self.load_document(file_path)
                if document:
                    documents.append(document)
        
        print(f"✅ Loaded {len(documents)} documents from {directory_path}")
        return documents
    
    def load_knowledge_base(self) -> List[Dict]:
        """
        Load all documents from the configured knowledge base directories.
        
        Returns:
            List of all loaded documents
        """
        all_documents = []
        
        # Load from main documents directory
        docs_dir = Path(rag_config.vector_store_path).parent / "documents"
        if docs_dir.exists():
            documents = self.load_directory(docs_dir, recursive=True)
            all_documents.extend(documents)
        
        # Load from knowledge base subdirectory
        kb_dir = docs_dir / "knowledge_base"
        if kb_dir.exists():
            kb_documents = self.load_directory(kb_dir, recursive=True)
            all_documents.extend(kb_documents)
        
        print(f"📚 Total documents loaded from knowledge base: {len(all_documents)}")
        return all_documents
    
    def validate_document(self, document: Dict) -> bool:
        """
        Validate that a document has the required structure.
        
        Args:
            document: Document dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['content', 'metadata', 'source']
        
        for field in required_fields:
            if field not in document:
                logger.error(f"Missing required field in document: {field}")
                return False
        
        if not document['content'] or not document['content'].strip():
            logger.error("Document has empty content")
            return False
        
        return True
    
    def get_document_summary(self, documents: List[Dict]) -> Dict:
        """
        Get summary statistics about loaded documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Summary statistics
        """
        if not documents:
            return {"total_documents": 0}
        
        file_types = {}
        total_content_length = 0
        total_word_count = 0
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            file_type = metadata.get('file_type', 'unknown')
            
            file_types[file_type] = file_types.get(file_type, 0) + 1
            total_content_length += metadata.get('content_length', 0)
            total_word_count += metadata.get('word_count', 0)
        
        return {
            "total_documents": len(documents),
            "file_types": file_types,
            "total_content_length": total_content_length,
            "total_word_count": total_word_count,
            "average_content_length": total_content_length // len(documents) if documents else 0,
            "average_word_count": total_word_count // len(documents) if documents else 0
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")

def create_document_loader() -> DocumentLoader:
    """Factory function to create document loader"""
    return DocumentLoader()
