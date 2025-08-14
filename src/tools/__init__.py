"""
Tools Package Initialization - Beginner Friendly
Manages all tools and provides easy access to them.
"""

import logging
from typing import Dict, Optional, List

# Import the base tool class
from .Base_tool import BaseTool

# Import all specific tools
from .web_serch import WebSearchTool, create_web_search_tool
from .document_processor import DocumentProcessorTool, create_document_processor
from .pdf_reader  import PDFReaderTool, create_pdf_reader
from .citation_formatter import CitationFormatterTool , create_citation_formatter
from .code_executor import CodeExecutorTool, create_code_executor

logger = logging.getLogger(__name__)

class ToolManager:
    """
    Simple manager to handle all tools in our system.
    Makes it easy to create, access, and manage tools.
    """
    
    def __init__(self):
        """Initialize the tool manager"""
        self.tools = {}
       
        self.tool_factories = {}
        self._setup_tool_factories()
        self._create_all_tools()
        
        print(f"🛠️ ToolManager initialized with {len(self.tools)} tools")
        logger.info(f"ToolManager created with tools: {list(self.tools.keys())}")
    
    def _setup_tool_factories(self):
        """Set up factory functions for creating tools"""
        self.tool_factories = {
            "web_search": create_web_search_tool,
            "document_processor": create_document_processor,
            "pdf_reader": create_pdf_reader,
            "citation_formatter": create_citation_formatter,
            "code_executor": create_code_executor
        }
    
    def _create_all_tools(self):
        """Create instances of all available tools"""
        for tool_name, factory_function in self.tool_factories.items():
            try:
                tool_instance = factory_function()
                self.tools[tool_name] = tool_instance
                print(f"  ✅ Created: {tool_name}")
            except Exception as e:
                print(f"  ❌ Failed to create {tool_name}: {e}")
                logger.error(f"Failed to create tool {tool_name}: {e}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a specific tool by name.
        
        Args:
            tool_name: Name of the tool to get
            
        Returns:
            Tool instance or None if not found
        """
        tool = self.tools.get(tool_name)
        if tool:
            logger.debug(f"Retrieved tool: {tool_name}")
        else:
            logger.warning(f"Tool not found: {tool_name}")
        return tool
    
    def list_tools(self) -> Dict[str, str]:
        """
        Get a list of all available tools with descriptions.
        
        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {name: tool.description for name, tool in self.tools.items()}
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """
        Get detailed information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with tool information or None if not found
        """
        tool = self.get_tool(tool_name)
        return tool.get_info() if tool else None
    
    def validate_all_tools(self) -> Dict[str, bool]:
        """
        Test that all tools are working correctly.
        
        Returns:
            Dictionary mapping tool names to validation results
        """
        print("🔍 Validating all tools...")
        validation_results = {}
        
        for name, tool in self.tools.items():
            try:
                # Basic validation - check if tool has required methods
                has_execute = hasattr(tool, 'execute') and callable(tool.execute)
                is_base_tool = isinstance(tool, BaseTool)
                
                is_valid = has_execute and is_base_tool
                validation_results[name] = is_valid
                
                status = "✅" if is_valid else "❌"
                print(f"  {status} {name}")
                
                if is_valid:
                    logger.info(f"Tool validation passed: {name}")
                else:
                    logger.error(f"Tool validation failed: {name}")
                    
            except Exception as e:
                validation_results[name] = False
                print(f"  ❌ {name} - Error: {e}")
                logger.error(f"Tool validation error for {name}: {e}")
        
        return validation_results
    
    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get usage statistics for all tools.
        
        Returns:
            Dictionary mapping tool names to usage counts
        """
        return {name: tool.usage_count for name, tool in self.tools.items()}
    
    def reset_all_usage_stats(self):
        """Reset usage statistics for all tools"""
        for tool in self.tools.values():
            tool.reset_usage_count()
        print("🔄 Reset usage stats for all tools")
    
    def reload_tool(self, tool_name: str) -> bool:
        """
        Reload a specific tool (useful for development).
        
        Args:
            tool_name: Name of the tool to reload
            
        Returns:
            True if reload was successful, False otherwise
        """
        if tool_name not in self.tool_factories:
            print(f"❌ Unknown tool: {tool_name}")
            return False
        
        try:
            # Create new instance
            factory_function = self.tool_factories[tool_name]
            new_tool = factory_function()
            
            # Replace old instance
            self.tools[tool_name] = new_tool
            print(f"🔄 Reloaded tool: {tool_name}")
            logger.info(f"Tool reloaded: {tool_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to reload {tool_name}: {e}")
            logger.error(f"Tool reload failed for {tool_name}: {e}")
            return False
    
    def available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())
    
    def tool_count(self) -> int:
        """Get total number of tools"""
        return len(self.tools)

# Create global tool manager instance
tool_manager = ToolManager()

# Convenience functions for easy access
def get_tool(tool_name: str) -> Optional[BaseTool]:
    """
    Easy way to get a tool by name.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool instance or None
    """
    return tool_manager.get_tool(tool_name)

def list_available_tools() -> Dict[str, str]:
    """
    Easy way to list all available tools.
    
    Returns:
        Dictionary mapping tool names to descriptions
    """
    return tool_manager.list_tools()

def validate_all_tools() -> Dict[str, bool]:
    """
    Easy way to validate all tools.
    
    Returns:
        Dictionary mapping tool names to validation results
    """
    return tool_manager.validate_all_tools()

def get_tool_usage_stats() -> Dict[str, int]:
    """
    Easy way to get usage statistics.
    
    Returns:
        Dictionary mapping tool names to usage counts
    """
    return tool_manager.get_usage_stats()

def reset_tool_usage_stats():
    """Easy way to reset all usage statistics"""
    tool_manager.reset_all_usage_stats()

# Export everything that other modules might need
__all__ = [
    # Base class
    'BaseTool',
    
    # Specific tool classes
    'WebSearchTool',
    'DocumentProcessorTool', 
    'PDFReaderTool',
    'CitationFormatterTool',
    'CodeExecutorTool',
    
    # Manager
    'ToolManager',
    'tool_manager',
    
    # Convenience functions
    'get_tool',
    'list_available_tools',
    'validate_all_tools',
    'get_tool_usage_stats',
    'reset_tool_usage_stats'
]

# Initialize message
print("📦 Tools package loaded successfully!")
logger.info("Tools package initialization complete")
