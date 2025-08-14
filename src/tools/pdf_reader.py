"""
Simple PDF Reader Tool - Beginner Friendly
Specialized tool just for reading PDF files with extra features.
"""

from pathlib import Path
from typing import List, Dict, Optional, Union
from . import BaseTool
import logging

logger = logging.getLogger(__name__)

class PDFReaderTool(BaseTool):
    """
    Special tool just for PDF files.
    Can read specific pages, get metadata, and analyze PDF structure.
    """
    
    def __init__(self):
        super().__init__(
            name="PDFReaderTool", 
            description="Specialized PDF reader with page-by-page analysis"
        )
        
        # Simple settings
        self.extract_metadata = True
        self.max_pages_at_once = 50  # Don't try to read huge PDFs at once
    
    def execute(self, pdf_path: Union[str, Path], page_range: Optional[tuple] = None) -> Optional[Dict]:
        """
        Read a PDF file and extract information.
        
        Args:
            pdf_path: Path to the PDF file
            page_range: Tuple like (1, 5) to read pages 1-5, or None for all pages
            
        Returns:
            Dictionary with PDF content, metadata, and page information
        """
        pdf_path = Path(pdf_path)
        
        # Check if file exists and is a PDF
        if not pdf_path.exists():
            print(f"❌ PDF file not found: {pdf_path}")
            return None
        
        if pdf_path.suffix.lower() != '.pdf':
            print(f"❌ File is not a PDF: {pdf_path}")
            return None
        
        try:
            print(f"📄 Reading PDF: {pdf_path.name}")
            
            # Extract all the information
            text_content = self._extract_pdf_text(pdf_path, page_range)
            metadata = self._get_pdf_metadata(pdf_path)
            page_info = self._analyze_pdf_pages(pdf_path)
            
            result = {
                "file_name": pdf_path.name,
                "file_path": str(pdf_path),
                "file_size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
                "text_content": text_content,
                "metadata": metadata,
                "page_info": page_info,
                "pages_processed": page_range or "all",
                "processed_at": self._get_timestamp()
            }
            
            print(f"✅ Successfully read PDF: {pdf_path.name}")
            return result
            
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            return None
    
    def _extract_pdf_text(self, pdf_path: Path, page_range: Optional[tuple] = None) -> str:
        """Extract text from PDF pages"""
        try:
            import pypdf
            
            text_content = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Figure out which pages to read
                if page_range:
                    start_page, end_page = page_range
                    start_page = max(0, start_page - 1)  # Convert to 0-based indexing
                    end_page = min(total_pages, end_page)
                else:
                    start_page, end_page = 0, min(total_pages, self.max_pages_at_once)
                
                print(f"📖 Reading pages {start_page + 1} to {end_page}")
                
                # Extract text from each page
                for page_num in range(start_page, end_page):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        
                        if page_text.strip():
                            text_content += f"\n=== PAGE {page_num + 1} ===\n"
                            text_content += page_text + "\n"
                        
                    except Exception as e:
                        print(f"⚠️ Could not read page {page_num + 1}: {e}")
                        continue
            
            return text_content
            
        except ImportError:
            print("❌ pypdf not installed. Run: pip install pypdf")
            return ""
        except Exception as e:
            print(f"❌ PDF text extraction failed: {e}")
            return ""
    
    def _get_pdf_metadata(self, pdf_path: Path) -> Dict:
        """Get PDF file information and metadata"""
        try:
            import pypdf
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Basic information
                info = {
                    "title": "",
                    "author": "",
                    "subject": "",
                    "creator": "",
                    "producer": "",
                    "creation_date": "",
                    "modification_date": "",
                    "total_pages": len(pdf_reader.pages),
                    "is_encrypted": pdf_reader.is_encrypted
                }
                
                # Try to get detailed metadata
                if pdf_reader.metadata:
                    metadata = pdf_reader.metadata
                    
                    info.update({
                        "title": str(metadata.get("/Title", "")),
                        "author": str(metadata.get("/Author", "")),
                        "subject": str(metadata.get("/Subject", "")),
                        "creator": str(metadata.get("/Creator", "")),
                        "producer": str(metadata.get("/Producer", "")),
                        "creation_date": str(metadata.get("/CreationDate", "")),
                        "modification_date": str(metadata.get("/ModDate", ""))
                    })
                
                return info
                
        except Exception as e:
            print(f"⚠️ Could not read PDF metadata: {e}")
            return {"error": str(e), "total_pages": 0}
    
    def _analyze_pdf_pages(self, pdf_path: Path) -> List[Dict]:
        """Analyze each page in the PDF"""
        try:
            import pypdf
            
            page_analysis = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        # Get text from this page
                        page_text = page.extract_text()
                        
                        # Get page dimensions
                        try:
                            width = float(page.mediabox.width) if hasattr(page, 'mediabox') else 0
                            height = float(page.mediabox.height) if hasattr(page, 'mediabox') else 0
                        except:
                            width = height = 0
                        
                        page_data = {
                            "page_number": page_num + 1,
                            "has_text": bool(page_text.strip()),
                            "character_count": len(page_text),
                            "word_count": len(page_text.split()) if page_text else 0,
                            "width": width,
                            "height": height
                        }
                        
                        page_analysis.append(page_data)
                        
                    except Exception as e:
                        print(f"⚠️ Error analyzing page {page_num + 1}: {e}")
                        page_analysis.append({
                            "page_number": page_num + 1,
                            "error": str(e)
                        })
            
            return page_analysis
            
        except Exception as e:
            print(f"❌ Page analysis failed: {e}")
            return []
    
    def read_specific_pages(self, pdf_path: Union[str, Path], start_page: int, end_page: int) -> Optional[Dict]:
        """
        Read only specific pages from a PDF.
        
        Args:
            pdf_path: Path to PDF file
            start_page: First page to read (1-based, so 1 = first page)
            end_page: Last page to read (inclusive)
            
        Returns:
            Dictionary with content from those pages only
        """
        return self.execute(pdf_path, page_range=(start_page, end_page))
    
    def get_pdf_summary(self, pdf_path: Union[str, Path]) -> Optional[Dict]:
        """
        Get a quick summary of the PDF without reading all content.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF summary information
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists() or pdf_path.suffix.lower() != '.pdf':
            return None
        
        try:
            metadata = self._get_pdf_metadata(pdf_path)
            page_info = self._analyze_pdf_pages(pdf_path)
            
            # Calculate summary stats
            total_words = sum(page.get("word_count", 0) for page in page_info if isinstance(page, dict))
            pages_with_text = sum(1 for page in page_info if page.get("has_text", False))
            
            summary = {
                "file_name": pdf_path.name,
                "file_path": str(pdf_path),
                "file_size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
                "total_pages": metadata.get("total_pages", 0),
                "pages_with_text": pages_with_text,
                "estimated_total_words": total_words,
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "is_encrypted": metadata.get("is_encrypted", False),
                "summary_created_at": self._get_timestamp()
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Could not create PDF summary: {e}")
            return None
    
    def _get_timestamp(self) -> str:
        """Get current date and time"""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")

def create_pdf_reader() -> PDFReaderTool:
    """Create a PDF reader tool"""
    return PDFReaderTool()
