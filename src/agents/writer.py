"""
Writer Agent - Document creation and report writing
"""
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .base_agent import BaseAgent
from src.tools import get_tool
from src.confrig.settings import settings
import logging
import time

logger = logging.getLogger(__name__)

class WriterAgent(BaseAgent):
    """
    Writer agent specialized in document creation and formatting
    """

    def __init__(self):
        system_message = f"""You are the Writer Agent, specialized in creating professional documents and reports.

YOUR WRITING MISSION:
1. **Report Structure**: Create well-organized, professional documents
2. **Content Integration**: Synthesize information from multiple sources
3. **Professional Writing**: Use clear, professional language
4. **Citation Management**: Integrate proper citations throughout
5. **Document Formatting**: Apply consistent formatting and styling

WRITING STANDARDS:
- Create structured documents with clear headings
- Include executive summaries for longer reports
- Integrate citations seamlessly into text
- Use bullet points and tables for clarity
- Provide actionable recommendations
- Save documents to: {settings.output_dir}/reports/"""
        super().__init__(
            name="writer",
            description="Professional Report Writer and Documentation Specialist",
            system_message=system_message

        )
    def register_tools(self):
        """Register the writer tool"""
        self.tool_objects={
            "citation_formatter": get_tool("citation_formatter")

        }
        async def create_report(title:str,content:str,report_type:str="analysis")->str:
            """Create a structed report"""
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            report = f"""# {title}
## Executive Summary
{self._create_executive_summary(content)}

## Main Content
{content}

## Key Findings
{self._extract_key_findings(content)}

## Recommendations
{self._generate_recommendations(content)}

---
*Report Type: {report_type}*
*Generated: {timestamp}*
*System: Autonomous Knowledge-Worker Agent*
"""
            self.save_to_memory("last_report",{
                "title": title,
                "content": report,
                "type": report_type,
                "timestamp": timestamp

            })
            return f"Report '{title}' created successfully. Length: {len(report)} characters."
        
        async def save_document(filename:str,content:str,format_type:str="markdown")->str:
             """Save document to output directory"""
             try:
                output_dir = settings.output_dir / "reports"
                output_dir.mkdir(parents=True, exist_ok=True)


                if not filename.endswith(('.md','.txt','.html')):
                    if format_type=="markdown":
                        filename +=".md"
                    elif format_type=="html":
                        filename +=".html"
                    else:
                        filename +=".txt"
                
                file_path = output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return f"Document saved: {file_path}"
             except Exception as e:
                return f"Failed to save document: {e}"
        
        async def generate_reference_list(style: str = "APA") -> str:
            """Generate reference list from all citations"""
            tool = self.tool_objects["citation_formatter"]
            
            if tool.get_citation_count() > 0:
                return tool.generate_reference_list(style)
            else:
                return "No citations available for reference list."
            
        
        self.add_tool_function("create_report", create_report, "Create structured reports")
        self.add_tool_function("save_document", save_document, "Save documents to files")
        self.add_tool_function("generate_reference_list", generate_reference_list, "Generate reference lists")

    def create_autogen_agent(self):
        """Create AutoGen agent with writing tools"""
        try:
            model_client = OpenAIChatCompletionClient(
                model=self.model_confrig["model"],
                api_key=self.model_confrig["api_key"]
            )
            
            function_tools = []
            for tool_info in self.tools:
                function_tool = FunctionTool(
                    tool_info["function"],
                    description=tool_info["description"]
                )
                function_tools.append(function_tool)
            
            agent = AssistantAgent(
                name=self.name,
                model_client=model_client,
                system_message=self.get_full_system_message(),
                tools=function_tools
            )
            
            logger.info(f"✅ Created writer with {len(function_tools)} tools")
            return agent
        except Exception as e:
            logger.error(f"❌ Error creating {self.name}: {e}")
            raise
    
    def _create_executive_summary(self, content: str) -> str:
        """Create simple executive summary"""
        sentences = content.split('.')[:3]
        return '. '.join(sentences) + '.' if sentences else "Executive summary to be completed."
    
    def _extract_key_findings(self, content: str) -> str:
        """Extract key findings"""
        return "• Key findings extracted from analysis\n• Important insights highlighted\n• Critical observations noted"
    
    def _generate_recommendations(self, content: str) -> str:
        """Generate recommendations"""
        return "• Recommendations based on findings\n• Actionable next steps\n• Strategic considerations"

def create_writer() -> WriterAgent:
    """Factory function to create writer agent"""
    return WriterAgent()


                
                 





