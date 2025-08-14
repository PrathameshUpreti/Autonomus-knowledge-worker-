"""
LLM Confriguration for Autogen Agents.

"""
from .settings import settings
import logging

logger=logging.getLogger(__name__)

class LLMConfrig:
    """LLM CONFRIGGURATION MANAGER"""
    def __init__(self):
        self.model_config= settings.get_model_confrig()
        logger.info(f"LLM Config initialized with model: {self.model_config['model']}")

    def get_confrig_for_agent(self,agent_type="default"):
        """
        Get LLM configuration for different agent types.
        Simple version with minimal differences.

        """
        base_confrig=self.model_config.copy()

        temprature_map={
             "supervisor": 0.1,    # More deterministic for planning
            "researcher": 0.2,    # Slightly more exploratory
            "writer": 0.3,        # More creative for writing
            "analyst": 0.0,       # Very deterministic for analysis
            "default": 0.1

        }

        base_confrig["temperature"] = temprature_map.get(agent_type,0.1)
        return base_confrig
    

    def validate_api_key(self):
        """SIMPLE API KEY VALIDATION"""
        try:
            import openai
            client=openai.OpenAI(api_key=settings.openai_api_key)
            models= client.models.list()

            logger.info("✅ OpenAI API key is valid")
            return True
        except Exception as e:
            logger.error(f"❌ OpenAI API key validation failed: {e}")
            return False
        
llm_confrig=LLMConfrig()

def get_agent_confrig(agent_type="default"):

     return llm_confrig.get_confrig_for_agent(agent_type)



