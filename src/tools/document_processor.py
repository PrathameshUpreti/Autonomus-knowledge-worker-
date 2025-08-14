"""

Handles text file , PDF , Word Docs,and more.

"""

import os
from pathlib import Path
from typing import List,Dict, Optional , Union
import mimetypes 
from .Base_tool import BaseTool
from src.confrig.settings import settings
import logging

logger= logging.getLogger(__name__)

class DocumentProcessorTool(BaseTool):
    """
    Tool to read and process diffrent type of document
    Supports: .txt, .md, .pdf, .docx, .html files
    """

    def __init__(self):

        super().__init__(
            name="DocumentProcessorTool",
            description="Read and process text from various document types"

        )

        self.supported_types=[".txt", ".md", ".pdf", ".docx", ".html"]
        self.max_file_size_mb=10
        self.chunk_size=1000 # Split text into 1000 character chunks

    def execute(self, file_path:Union[str,Path],operation:str="extract")->Optional[Dict]:
         """
        Process a document file.
        
        Args:
            file_path: Path to the document (e.g., "./data/documents/report.pdf")
            operation: What to do - "extract", "analyze", or "chunk"
            
        Returns:
            Dictionary with file info and extracted text
        """
         file_path=Path(file_path)


         if not file_path.exists():
             print(f"❌ File not found: {file_path}")
             return None
         
         file_size_mb=file_path.start().st_size/(1024*1024)
         if file_size_mb > self.max_file_size_mb:
             print(f"❌ File too large: {file_size_mb:.1f}MB (max: {self.max_file_size_mb}MB)")
             return None
         
         try:
             print(f"📄 Processing: {file_path.name}")
             file_type = file_path.suffix.lower()

             if operation == "extract":
                text_content = self.extract_text(file_path, file_type)
             elif operation == "analyze":
                text_content = self.anlyse_document(file_path, file_type)
             elif operation == "chunk":
                text_content = self.chunk_document(file_path, file_type)
             else:
                text_content = self.extract_text(file_path, file_type)

            
             if text_content:
                 result={
                 "file_name": file_path.name,
                    "file_path": str(file_path),
                    "file_size_mb": round(file_size_mb, 2),
                    "file_type": file_type,
                    "operation": operation,
                    "content": text_content,
                    "processed_at": self._get_timestamp()
                 
             }
             print(f"✅ Processed {file_path.name} successfully")
             return result
            
         except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            
         return None

    def extract_text(self, file_path:Path,file_type:str)->Optional[str]:
        """Extract Text from diffrent file types""" 
        try:
            if file_type==".txt":
                return self.read_text_file(file_path)
            if file_type ==".md":
                return self.read_text_file(file_path)
            elif file_type == ".html":
                return self.read_html_file(file_path)
            elif file_type == ".pdf":
                return self.read_pdf_file(file_path)
            elif file_type == ".docx":
                return self.read_word_file(file_path)
            else:
                return self.read_word_file(file_path)
            
        except Exception as e:
            print(f"❌ Text extraction failed: {e}")
            return None
        
    
    def read_text_file(self,file_path:Path) ->str:
        """Read a simple file"""
        with open(file_path,'r',encoding='utf-8',errors='ignore')as f:
            return f.read()
        
    def read_html_file(self,file_path:Path)-> str:
        """Read HTML file"""
        try:
            from bs4 import BeautifulSoup

            with open(file_path,'r',encoding='utf-8',errors='ignore') as f:
                html_content=f.read()

            soup=BeautifulSoup(html_content,'html.parser')

            for tag in soup(["script","style"]):
                tag.decompose()
            
            return soup.get_text(seperator='\n',strip=True)
        except ImportError:
            print(f"❌ Text extraction failed")
            return None

    def read_pdf_file(self, file_path:Path)->str:
        """Read PDF File and extract text"""
        try:
            import pypdf

            text_content=""
            with open(file_path,'rb') as f:
                pdf_reader=pypdf.PdfReader(f)

            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text=page.extract_text()
                    if page_text:
                        text_content+=f"\n--- Page {page_num + 1} ---\n"
                        text_content+=page_text
                except Exception as e:
                    print(f"⚠️ Error reading page {page_num + 1}: {e}")
                    continue
            return text_content
        except ImportError:
            print("❌ pypdf not available. Install with: pip install pypdf")
            return ""
        
    
        
    def read_word_file(self,file_path:Path) -> str:
        """Read word document and extrct text"""

        try:
            from docx import Document
            doc=Document(file_path)
            text_content=""

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content+=paragraph.text +"\n"
            
            return text_content
        
        except ImportError:
            print("❌ python-docx not available. Install with: pip install python-docx")
            return ""
        
    def anlyse_document(self,file_path:Path, file_type:str)->Dict:
        """Analyze document and return statics"""

        text_content=self.extract_text(file_path,file_type)
        if not text_content:
            return {"error": "Could not extract text"}
        
        lines = text_content.split('\n')
        words = text_content.split()

        analysis = {
            "total_characters": len(text_content),
            "total_words": len(words),
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "average_words_per_line": len(words) / max(len(lines), 1),
            "preview": text_content[:300] + "..." if len(text_content) > 300 else text_content
        }
        
        return analysis
    
    def chunk_document(self,file_path:Path,file_type:str)->List[Dict]:
        """Break the document into smaller text for processing"""
        text_content= self.extract_text(file_path, file_type)
        if not text_content:
            return[]
        
        chunks=[]

        for i in range(0,len(text_content),self.chunk_size):
            chunk_text=text_content[i:i +self.chunk_size]
            chunk = {
                "chunk_number": len(chunks) + 1,
                "start_position": i,
                "end_position": min(i + self.chunk_size, len(text_content)),
                "text": chunk_text,
                "word_count": len(chunk_text.split()),
                "source_file": str(file_path)
            }
            chunks.append(chunk)
        
        return chunks
    def process_folder(self, folder_path: Union[str, Path]) -> List[Dict]:
        """Process all supported documents in a folder"""
        folder_path = Path(folder_path)
        results = []
        
        if not folder_path.exists():
            print(f"❌ Folder not found: {folder_path}")
            return results
        
        print(f"📁 Processing folder: {folder_path}")
        
        # Find all supported files
        for file_path in folder_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_types:
                result = self.execute(file_path, "extract")
                if result:
                    results.append(result)
        
        print(f"✅ Processed {len(results)} files from {folder_path}")
        return results
    
    def _get_timestamp(self) -> str:
        """Get current date and time"""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")

def create_document_processor() -> DocumentProcessorTool:
    """Create a document processor tool"""
    return DocumentProcessorTool()
            






        




            

             
             


       