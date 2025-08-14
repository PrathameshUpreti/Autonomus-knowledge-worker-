"""
Base Agent clas for all agents in the system

"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
from src.confrig.settings import Setting, settings
from src.confrig.llm_confrig import get_agent_confrig

logging.basicConfig(level=getattr(logging,settings.log_level))
logger= logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all agent in our system.
    Provide common functionality and enforce consistent structure.

    """
    def __init__(self,name:str, description:str, system_message:str):
        self.name=name
        self.role= description
        self.system_message= system_message
        self.agent_type= name.lower().replace("_agent", "")
        self.memory={}
        self.tools=[]
        self.tool_objects={}

        self.model_confrig = get_agent_confrig(self.agent_type)

        self.register_tools()
        logger.info(f"✅ Initialized {self.role}: {self.name} with {len(self.tools)} tools")


        logger.info(f"✅ Initializing {self.role}: {self.name}")
        logger.debug(f"📋 Model confrig: {self.model_confrig['model']}")

    @abstractmethod
    def create_autogen_agent(self):
        """
        Create and return the autogen agent instance

        """
        pass
    @abstractmethod
    def register_tools(self):
        """Create and return the autogen agent instance with tool"""
        pass

    def get_full_system_message(self):
        """
        Get the complete system message for this agent

        """
        return f"""
        You are {self.name} , a {self.role} in a autonoumus knowledge system.
        {self.system_message}
        IMPORTANT GUIDELINES:
        - Be precise and factual in all responses
        - Cite sources when available
        - Work collaboratively with other agents
        - Follow task instructions carefully
        - Ask for clarification if needed
        - Keep responses focused and relevant

        Your role: {self.role}
        System: {settings.project_name}

        """
    def save_to_memory(self,key:str,value:Any):
        """Save Information to agents Memory """  
        self.memory[key]=value
        logger.debug(f"💾 {self.name} saved to memory: {key}")

    def get_from_memory(self,key:str)-> Optional[Any]:
        """Retrive information from the agents memory """
        return self.memory.get(key)
    def clear_memory(self):
        """Clear agent's memory"""
        self.memory.clear()
        logger.debug(f"🗑️ {self.name} cleared memory")
    
    def add_tool_function(self, tool_name: str, tool_function: callable, description: str):
        """Add tool to autogen function"""
        self.tools.append({
            "name":tool_name,
            "function":tool_function,
            "description":description
        })    
        logger.debug(f"Added tool function {tool_name} to {self.name}")

