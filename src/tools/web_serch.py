"""
Web based serch tool
Searches the internet and gets content from web pages.

"""

import requests
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .Base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """
    Tool to serch in Internet--->
    Uses DuckDuckGo and web scrapping
    """

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the internet and get content from web pages"

        )

        self.max_result=5
        self.timeout=10
        self.delay = 1  
        self.user_agent = "Mozilla/5.0 (compatible; AutonomousAgent/1.0)"


    def execute(self, query:str,max_result:Optional[int]=None)->List[Dict]:

         """
        Search the internet for information.
        
        Args:
            query: What to search for (e.g., "electric cars 2024")
            max_results: How many results to return (default: 5)
            
        Returns:
            List of search results with title, URL, and content
        """
         if not self.validate_input(query):
             print("❌ Invalid search query")
             return[]
         
         max_result=max_result or self.max_result

         try:
             print(f"🔍 Searching for: {query}")
             results= self.search_duckduckgo(query, max_result)
             if not results:
                 results=self.search_web_basic(query , max_result)
             print(f"✅ Found {len(results)} results")
             return results
         except Exception as e:
             print(f"❌ Search failed: {e}")
             return []
         
    def search_duckduckgo(self, query:str,max_result:int) -> List[Dict]:
        """Search DucKDuckGo free API"""
        try:
            url= f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"

            response= requests.get(url,timeout=self.timeout)

            if response.status_code==200:
                data=response.json()
                results=[]

                if data.get("Abstract"):
                    results.append({

                        "title": data.get("Heading", "DuckDuckGo Result"),
                        "url": data.get("AbstractURL", ""),
                        "content": data.get("Abstract", ""),
                        "source": "DuckDuckGo",
                        "date": self._get_current_date()

                    })

                for topic in data.get("RelatedTopics",[])[:max_result-1]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "")[:100],
                            "url": topic.get("FirstURL", ""),
                            "content": topic.get("Text", ""),
                            "source": "DuckDuckGo",
                            "date": self._get_current_date()
                        })
                    return results[:max_result]
        except Exception as e:
            print(f"⚠️ DuckDuckGo search failed: {e}")
            
        return []
    
    def search_web_basic(self, query: str, max_results: int) -> List[Dict]:
        """Basic web search as backup"""
        try:
            # Simple search using DuckDuckGo's HTML interface
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

            response = requests.get(
                search_url,
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent}
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                # Find search result links
                links = soup.find_all('a', class_='result__a')[:max_results]
                
                for link in links:
                    title = link.get_text(strip=True)
                    url = link.get('href', '')

                    snippet = ""
                    parent = link.find_parent('div', class_='result')
                    if parent:
                        snippet_elem = parent.find('a', class_='result__snippet')
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "content": snippet,
                            "source": "Web Search",
                            "date": self._get_current_date()
                        })
                    time.sleep(self.delay)
                
                return results
                
        except Exception as e:
            print(f"⚠️ Basic web search failed: {e}")
            
        return []
    
    def get_page_content(self,url:str)->Optional[Dict]:
        """
        Get content from a specific web page.
        
        Args:
            url: The web page URL to read
            
        Returns:
            Dictionary with page title and content

        """
        try:
            print(f"📄 Getting content from: {url}")

            response=requests.get(
                url,timeout=self.timeout,
                headers={"user-Agent":self.user_agent}

            )
            if response.status_code ==200:
                soup=BeautifulSoup(response.content,'html.parser')

                title="No Title"
                title_tag=soup.find('title')
                if title_tag:
                    title=title_tag.get_text(strip=True)

                content=""

                content_areas=soup.find_all(['p', 'article', 'div', 'section'])
                content_piece=[]

                for area in content_areas:
                    text=area.get_text(strip=True)
                    if len(text)>50:
                        content_piece.append(text)
                
                content = "\n\n".join(content_piece[:10])

                results={
                    "title":title,
                    "url":url,
                    "content":content,
                    "source": "Web Page",
                    "date":self._get_current_date()
                }
                print("✅ Content extracted successfully")
                return results
            
        except Exception as e:
            print(f"❌ Failed to get content from {url}: {e}")
            
        return None
    def _get_current_date(self) -> str:
        """Get today's date"""
        return time.strftime("%Y-%m-%d")
    
def create_web_search_tool() -> WebSearchTool:
    """Create a web search tool"""
    return WebSearchTool()
 




             

       

