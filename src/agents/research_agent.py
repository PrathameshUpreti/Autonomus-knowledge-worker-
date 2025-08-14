"""
Resarch agent with RAG capability using Autogen

"""
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .base_agent import BaseAgent
from autogen_core.tools import  FunctionTool    
from src.tools import get_tool
from src.confrig.settings import settings
import logging
import os
from typing import Dict
from pathlib import Path
import inspect

logger=logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    """
    Research agent with basic RAG capabilities.
    Specializes in finding information from documents and knowledge bases.

    """
    def __init__(self):
        system_message="""You are the Research Agent, specialized in document-based research and knowledge retrieval.

YOUR KEY RESPONSIBILITIES:
1. **Document Analysis**: Search through uploaded documents and knowledge bases
2. **Information Extraction**: Find relevant information for specific questions
3. **Source Verification**: Cross-reference information across multiple documents
4. **Citation Management**: Provide proper citations for all information
5. **Knowledge Synthesis**: Combine information from multiple sources
6. **Gap Identification**: Identify missing information or research needs

RESEARCH PROCESS:
1. Understand the specific research question or topic
2. Search through available documents in our knowledge base
3. Extract relevant information with source attribution
4. Verify information accuracy across sources
5. Synthesize findings into clear, organized insights
6. Identify any gaps or areas needing additional research

RESPONSE FORMAT:
- Provide clear, factual information
- Always include source citations when available
- Indicate confidence level for each piece of information
- Suggest additional research directions if needed
- Use bullet points for clarity when listing multiple facts

AVAILABLE RESOURCES:
- Document directory: {settings.docs_dir}
- Knowledge base: {settings.docs_dir}/knowledge_base
- Vector store: {settings.vector_store_dir}"""
        super().__init__(
           name="research_agent",
           description="Document Research and Knowledge Retrieval Specialist",
           system_message= system_message
       )
        self.setup_rag()
    
    def register_tools(self):
        """register reserch tool using functioTool"""
        self.tool_objects={
          "document_processor": get_tool("document_processor"),
            
          "citation_formatter": get_tool("citation_formatter")
        }

        async def process_document(file_path: str, operation: str = "extract") -> str:
            """Process document and extract content"""
            try:
                from pathlib import Path
                from src.confrig.settings import settings
                
                tool = self.tool_objects.get("document_processor")
                if not tool:
                    return "❌ Document processor tool not available"
                
                kb_dir = Path(settings.docs_dir) / "knowledge_base"
                if not Path(file_path).is_absolute():
                    file_path = kb_dir / file_path
                
                file_path = Path(str(file_path).replace("settings.docs_dir", str(settings.docs_dir)))
                if not file_path.exists():
                    return f"❌ File not found: {file_path}"
                result = tool.execute(file_path, operation)
                
                if result and isinstance(result, dict):
                    content_preview = result.get("content", "")[:500]
                    file_name = result.get("file_name", "Unknown Document")
                    return (
                f"✅ Document processed: {file_name}\n"
                f"Content preview: {content_preview}... "
                f"Use format_citation to cite this document."
                )

                return f"❌ Document processing failed or returned empty content for: {file_path}"

            except Exception as e:
               return f"❌ Error processing document {file_path}: {e}"


            

        async def format_citation(title:str,url:str="",author: str = "", style: str = "APA")->str:
            """Create critation"""

            tool=self.tool_objects["critation_formatter"]
            source_info={"title": title,
                          "url": url, 
                          "author": author
                          }
            citation=tool.execute(source_info,style)
            citation_id = len(citation)
            return f"Citation [{citation_id}]: {citation}"
        

        self.add_tool_function("process_document", process_document, "Process various document formats")
        self.add_tool_function("format_citation", format_citation, "Create academic citations")
    def setup_rag(self):
        """
        Set up basic rag confrigration

        """
        self.rag_confrig={
            "docs_directory":str(settings.docs_dir),
            "vector_store_path":str(settings.vector_store_dir),
            "embedding_model":settings.embedding_model,
            "collection_name": settings.vector_db_name,
            "chunk_size":1000,
            "chunk_overlap":200
        }
        logger.info(f"🔍 RAG setup complete for {self.name}")
        logger.debug(f"📁 Document directory: {self.rag_confrig['docs_directory']}")

        
    def create_autogen_agent(self):
        """Create aautogen agent with reserch capabitity"""

        try:
            model_client=OpenAIChatCompletionClient(
                model=self.model_confrig["model"],
                api_key=self.model_confrig["api_key"]
            )
            function_tools=[]
            for tool_info in self.tools:
                function_tool=FunctionTool(
                    tool_info["function"],
                    description=tool_info["description"]
                    

                )
                function_tools.append(function_tool)

            agent=AssistantAgent(
                name=self.name,
                model_client=model_client,
                system_message=self.get_full_system_message(),
                tools=function_tools

            )
            logger.info(f"✅ Created research agent: {self.name}")
            return agent
            
        except Exception as e:
            logger.error(f"❌ Error creating {self.name}: {e}")
            raise
    def  check_document_availabilty(self)->Dict:
         """Check what documents are available for research"""
         docs_info={
             "documents_found": 0,
            "document_types": [],
            "total_size_mb": 0
             
         }
         try:
             docs_path= settings.docs_dir
             if  docs_path.exists():
                 docs_files=list(docs_path.glob("**/*"))
                 docs_files=[f for f in docs_files if f.is_file()]
                 docs_info["documents_found"]=len(docs_files)

                 # Get file types
                 extensions = {f.suffix.lower() for f in docs_files if f.suffix}
                 docs_info["document_types"] = list(extensions)
                
                # Calculate total size
                 total_size = sum(f.stat().st_size for f in docs_files)
                 docs_info["total_size_mb"] = round(total_size / (1024 * 1024), 2)

                 logger.info(f"📊 Document availability check: {docs_info['documents_found']} files, {docs_info['total_size_mb']}MB")
                
         except Exception as e:
            logger.warning(f"Could not check documents: {e}")
        
         self.save_to_memory("docs_info", docs_info)
         return docs_info
    
    def get_rag_status(self) -> Dict:
        """Get status of RAG configuration and document availability"""
        return {
            "rag_config": self.setup_rag,
            "document_availability": self.check_document_availabilty(),
            "tools_available": len(self.tools),
            "status": "Ready for research tasks"
        }

def create_research_agent() -> ResearchAgent:
    """Factory function to create research agent"""
    return ResearchAgent()


                 

    

    
