"""
Agent package initialization and factory functions
"""
import logging
from typing import Dict, Any

# Import all agents
from .supervisor_agent import SupervisorAgent, create_supervisor
from .research_agent import ResearchAgent, create_research_agent
from .web_resercher import WebResearcherAgent, create_web_researcher
from .analyst import AnalystAgent, create_analyst
from .writer import WriterAgent, create_writer
from .base_agent import BaseAgent 

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Simple manager for all agents in our system
    """
    
    def __init__(self):
        self.agents = {}
        self.autogen_agents = {}
        logger.info("🤖 AgentManager initialized")
    
    def create_all_agents(self) -> Dict[str, Any]:
        """Create all agents and their AutoGen instances"""
        try:
            self.agents = {
                "supervisor": create_supervisor(),
                "research_agent": create_research_agent(),
                "web_researcher": create_web_researcher(),
                "analyst": create_analyst(),
                "writer": create_writer()
            }
            
            self.autogen_agents = {
                name: agent.create_autogen_agent()
                for name, agent in self.agents.items()
            }
            
            logger.info(f"✅ Created {len(self.agents)} agents successfully")
            return self.autogen_agents
            
        except Exception as e:
            logger.error(f"❌ Error creating agents: {e}")
            raise
    
    def get_agent(self, agent_name: str):
        """Get specific agent instance"""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> list:
        """List all available agents"""
        return list(self.agents.keys())

# Global agent manager
agent_manager = AgentManager()

# Convenience functions
def create_all_agents():
    """Create all agents"""
    return agent_manager.create_all_agents()

def get_agent(agent_name: str):
    """Get specific agent"""
    return agent_manager.get_agent(agent_name)
