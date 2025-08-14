"""
Workflows Package - Multi-Agent Orchestration System
Simple, beginner-friendly workflow implementation using AutoGen's DiGraphBuilder.
"""

import logging
from typing import Dict, Any, List, Optional
from src.confrig.settings import settings

logger = logging.getLogger(__name__)

class WorkflowConfig:
    """
    Simple configuration for workflow system.
    Defines how agents coordinate and execute tasks.
    """
    
    def __init__(self):
        # Workflow execution settings
        self.max_workflow_steps = 10
        self.timeout_per_step = 300  # 5 minutes per step
        self.enable_parallel_execution = False  # Keep simple for now
        
        # Agent coordination settings
        self.default_workflow_pattern = "sequential"  # supervisor -> research -> web -> analyst -> writer
        self.enable_conditional_routing = True
        self.save_intermediate_results = True
        
        # Output settings
        self.workflow_output_dir = settings.output_dir / "workflows"
        self.workflow_output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🔄 Workflow configuration initialized")
        logger.debug(f"📁 Workflow output: {self.workflow_output_dir}")
    
    def get_default_agent_sequence(self) -> List[str]:
        """Get the default sequence of agents for workflows"""
        return ["supervisor", "research_agent", "web_researcher", "analyst", "writer"]

# Global workflow configuration
workflow_config = WorkflowConfig()

# Import workflow components
from .task_decomposer import TaskDecomposer, create_task_decomposer
from .agent_orchestrator import AgentOrchestrator, create_orchestrator
from .workflow_builder import WorkflowBuilder, create_workflow_builder
from .execution_manager import ExecutionManager, create_execution_manager

__all__ = [
    'WorkflowConfig',
    'workflow_config',
    'TaskDecomposer',
    'AgentOrchestrator', 
    'WorkflowBuilder',
    'ExecutionManager',
    'create_task_decomposer',
    'create_orchestrator',
    'create_workflow_builder',
    'create_execution_manager'
]
