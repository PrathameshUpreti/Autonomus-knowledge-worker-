"""
Web Researcher Agent - Internet search and online information gathering.
"""

import logging
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .base_agent import BaseAgent
from src.tools import get_tool
from src.tools.web_serch import WebSearchTool
from src.tools.citation_formatter import CitationFormatterTool
        

logger = logging.getLogger(__name__)

class WebResearcherAgent(BaseAgent):

    def __init__(self):
        system_message = """
        You are the Web Researcher Agent, specialized in gathering current information from the internet.
        - Perform targeted searches
        - Extract and summarize content
        - Verify credibility
        - Always cite sources
        """
        super().__init__(
            name="web_researcher",
            description="Web Research and Online Information Specialist",
            system_message=system_message
        )

    def register_tools(self):
        """Register tools for searching and citing web content"""
        self.tool_objects = {
            "web_search": get_tool("web_search") or WebSearchTool(),
            "citation_formatter": get_tool("citation_formatter") or CitationFormatterTool()
        }

        async def search_web(query: str, max_results: int = 5) -> str:
            tool = self.tool_objects["web_search"]
            results = tool.execute(query, max_results)
            if results:
                return "\n".join(
                    f"{i+1}. {r['title']}\n   URL: {r['url']}\n   Content: {r['content'][:200]}..."
                    for i, r in enumerate(results)
                )
            return "No results found."

        async def get_content(url: str) -> str:
            tool = self.tool_objects["web_search"]
            result = tool.get_page_content(url)

            if result:
                return (
                    f"Page: {result['title']}\n"
                    f"URL: {url}\n"
                    f"Content: {result['content'][:500]}...\n"
                    f"Use cite_web_source to create citation."
                )
            return f"Failed to get content from: {url}"

        async def cite_web_source(title: str, url: str, author: str = "") -> str:
            tool = self.tool_objects["citation_formatter"]
            citation_id = tool.add_web_source(url, title, author)
            return f"Web source cited as [{citation_id}]."

        self.add_tool_function("search_web", search_web, "Search internet for information")
        self.add_tool_function("get_content", get_content, "Extract content from web pages")
        self.add_tool_function("cite_web_source", cite_web_source, "Create web source citations")

    def create_autogen_agent(self):
        """Create AutoGen agent with web research tools"""
        try:
            model_client = OpenAIChatCompletionClient(
                model=self.model_confrig["model"],
                api_key=self.model_confrig["api_key"]
            )
            function_tools = [
                FunctionTool(t["function"], description=t["description"])
                for t in self.tools
            ]
            agent = AssistantAgent(
                name=self.name,
                model_client=model_client,
                system_message=self.get_full_system_message(),
                tools=function_tools
            )
            logger.info(f"✅ Created web researcher with {len(function_tools)} tools")
            return agent
        except Exception as e:
            logger.error(f"❌ Error creating {self.name}: {e}")
            raise


def create_web_researcher() -> WebResearcherAgent:
    return WebResearcherAgent()
