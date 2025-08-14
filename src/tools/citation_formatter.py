"""
create proper acadmic critation and refrence list
"""
from typing import List, Dict, Optional
from datetime import datetime
from .Base_tool import BaseTool
import re


class CitationFormatterTool(BaseTool):
    """
    Tool to create proper citations.
    Supports APA, MLA, Chicago, and Simple styles.
    """

    def __init__(self):
        super().__init__(
            name="citation_formatter",
            description="Create proper academic citations and reference lists"
        )
        self.default_style="APA"
        self.supported_styles = ["APA", "MLA", "CHICAGO", "SIMPLE"]
        self.citations = []  

    def execute(self,source_info:Dict ,style:str ="APA")-> str:
        """
        Create a citation for a source.
        
        Args:
            source_info: Dictionary with source information like:
                        {"title": "Article Title", "url": "http://...", "author": "John Doe"}
            style: Citation style - "APA", "MLA", "CHICAGO", or "SIMPLE"
            
        Returns:
            Formatted citation string
        """
        if not source_info or not source_info.get("title"):
            print("❌ Need at least a title to create citation")
            return ""
        
        style=style.upper() 
        if style not in self.supported_styles:
            style = self.default_style

        try:
            print(f"📝 Creating {style} citation")
            
            # Add this source to our citation list
            citation_entry = source_info.copy()
            citation_entry["citation_id"] = len(self.citations) + 1
            citation_entry["style_used"] = style
            citation_entry["created_date"] = self._get_current_date()
            self.citations.append(citation_entry)

            if style == "APA":
                formatted = self.format_apa_style(source_info)
            elif style == "MLA":
                formatted = self.format_mla_style(source_info)
            elif style == "CHICAGO":
                formatted = self._format_chicago_style(source_info)
            else:  # SIMPLE
                formatted = self.format_simple_style(source_info)
            
            print(f"✅ Citation created (ID: {len(self.citations)})")
            return formatted
            
        except Exception as e:
            print(f"❌ Citation creation failed: {e}")
            return f"Error creating citation for: {source_info.get('title', 'Unknown')}"
        
    def format_apa_style(self,source:Dict) ->str:
        """Create APA style citation"""
        # Get information from source
        author = source.get("author", "").strip()
        title = self.clean_title(source.get("title", ""))
        url = source.get("url", "").strip()
        date = source.get("date", "").strip()
        source_name = source.get("source", "").strip()
        access_date = self._get_current_date()

        parts=[]

        if author:
            parts.append(f"{author}.")

        if date:
            parts.append(f"({date}).")
        
        if title:
            parts.append(f"{title}.")
        
        if source_name:
            parts.append(f"{source_name}.")
        
        if url:
            parts.append(f"Retrieved {access_date}, from {url}")
        
        return " ".join(parts)
    def format_mla_style(self,source:Dict) -> str:
        """Create MLA style creation"""
        author=source.get("author","").strip()
        title=self.clean_title(source.get("title",""))
        website=source.get("source",source.get("website","")).strip()
        url = source.get("url", "").strip()
        date = source.get("date", "").strip()
        access_date = self._get_current_date()

        parts=[]

        if author:
            parts.append(f"{author}.")
        
        if title:
            parts.append(f'"{title}."')
        
        if website:
            parts.append(f"{website},")
        
        if date:
            parts.append(f"{date},")
        
        if url:
            parts.append(f"{url}.")
            parts.append(f"Accessed {access_date}.")
        
        return " ".join(parts)
    
    def _format_chicago_style(self, source: Dict) -> str:
        """Create Chicago style citation"""
        author = source.get("author", "").strip()
        title = self.clean_title(source.get("title", ""))
        website = source.get("source", "").strip()
        url = source.get("url", "").strip()
        date = source.get("date", "").strip()
        access_date = self._get_current_date()
        
        parts = []
        
        if author:
            parts.append(f"{author}.")
        
        if title:
            parts.append(f'"{title}."')
        
        if website:
            parts.append(f"{website}.")
        
        if date:
            parts.append(f"Last modified {date}.")
        
        if url:
            parts.append(f"Accessed {access_date}.")
            parts.append(f"{url}.")

        return " ".join(parts)
    
    def format_simple_style(self,source:Dict)->str:
        """Create simple, easy-to-read citation"""
        title= self.clean_title(source.get("title",""))
        author= source.get("author","").strip()
        source_name=source.get("source","").strip()
        url=source.get("source","").strip()
        date=source.get("date","").strip()

        parts = []
        
        if title:
            parts.append(title)
        
        if author:
            parts.append(f"by {author}")
        
        if source_name:
            parts.append(f"({source_name})")
        
        if date:
            parts.append(f"[{date}]")
        
        if url:
            parts.append(f"<{url}>")
        
        return " ".join(parts)

    def clean_title(self, title:str)->str:
        """Clean up title text"""
        if not title:
            return ""
        
        title=re.sub(r'\s+',' ',title.strip()) # remove extra space

        if len(title)>100: #limit the length
            title=title[:97]+"..."
        return title
    
    def add_web_source(self, url: str, title: str, author: str = "", source: str = "", date: str = "") -> int:
        """
        Add a web source and create citation for it.
        
        Args:
            url: Web page URL
            title: Page title
            author: Author name (optional)
            source: Website name (optional)
            date: Publication date (optional)
            
        Returns:
            Citation ID number for referencing
        """
        source_info = {
            "type": "web",
            "title": title,
            "url": url,
            "author": author,
            "source": source,
            "date": date
        }
        self.execute(source_info)
        return len(self.citations) 

    def create_inline_citation(self, citation_id: int) -> str:
        """
        Create an inline citation reference like [1] or [2].
        
        Args:
            citation_id: The ID number of the citation
            
        Returns:
            Formatted inline citation
        """
        return f"[{citation_id}]"
    
    def generate_reference_list(self, style: str = "APA") -> str:
        """
        Create a complete reference list from all citations.
        
        Args:
            style: Citation style to use
            
        Returns:
            Formatted reference list
        """
        if not self.citations:
            return "No citations available."
        
        style = style.upper()
        lines = [f"## References ({style} Style)", ""]
        
        for i, citation in enumerate(self.citations, 1):
          
            if style == "APA":
                formatted = self.format_apa_style(citation)
            elif style == "MLA":
                formatted = self.format_mla_style(citation)
            elif style == "CHICAGO":
                formatted = self._format_chicago_style(citation)
            else:
                formatted = self.format_simple_style(citation)
            
            lines.append(f"{i}. {formatted}")
        
        return "\n".join(lines)
    def get_citation_count(self) -> int:
        """Get the total number of citations stored"""
        return len(self.citations)
    
    def clear_citations(self):
        """Remove all stored citations"""
        self.citations.clear()
        print("🗑️ All citations cleared")
    
    def list_citations(self) -> List[Dict]:
        """Get list of all citations"""
        return self.citations.copy()
    
    def _get_current_date(self) -> str:
        """Get today's date in readable format"""
        return datetime.now().strftime("%B %d, %Y")

def create_citation_formatter() -> CitationFormatterTool:
    """Create a citation formatter tool"""
    return CitationFormatterTool()
    

                   



 





        





    



