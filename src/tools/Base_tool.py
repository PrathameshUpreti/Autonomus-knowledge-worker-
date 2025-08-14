"""
Tools package for the autonomous knowledge-worker system.
Simple, beginner-friendly tool implementations.

"""

import logging
import os
from abc import ABC , abstractmethod
from typing import Any,Dict,Optional
from src.confrig.settings import settings


logger=logging.getLogger(__name__)

class BaseTool(ABC):
    """
    Base class for all tools.Every tool inherit from the class.
    """

    def __init__(self,name:str,description:str):
        self.name=name
        self.description=description
        self.confrig={}
        print(f"🔧 Created tool: {self.name}")

    @abstractmethod
    def execute(self,*args, **kwargs) -> Any:
        """Every tool must have an execute method"""
        pass

    def validate_input(self,data:Any) -> bool:
        """Check if input data is valid"""
        return data is not None and data !=""
    
    def log_usage(self,opeartion:str,sucess:bool=True):
        """Log what the Toll is Doing"""
        self.usage_count+=1
        status="✅" if sucess else "❌"
        print(f"{status}{self.name}:{opeartion}")

    
    def get_info(self) ->Dict[str,Any]:
        """
        Get information about this tool
        Returns:
            Dictionary with tool information

        """
        return{
            "name":self.name,
            "description":self.description,
            "usage_count":self.usage_count,
            "confrig":self.confrig.copy()
        }
    
    def reset_usage_count(self,new_confrig:Dict):
        """
        Update the tool confriguration
        Args:
            new_config: Dictionary with new configuration settings
        """
     
        self.confrig.update(new_confrig)
        print(f"⚙️ Updated config for {self.name}")
        logger.info(f"Config updated for {self.name}: {new_confrig}")

    def __str__(self) -> str:
        """String representaion of tool"""
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        """Developer representation of the tool"""
        return f"<{self.__class__.__name__}(name='{self.name}', usage={self.usage_count})>"




    



