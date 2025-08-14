"""
Workflow Builder - Creates and manages different workflow patterns.
Provides templates and patterns for common multi-agent workflows.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .task_decomposer import TaskPlan, Task, create_task_decomposer
from .agent_orchestrator import AgentOrchestrator, create_orchestrator
from . import workflow_config
import time

logger = logging.getLogger(__name__)

@dataclass
class WorkflowTemplate:
    """Template for creating workflows"""
    name: str
    description: str
    agent_sequence: List[str]
    parallel_stages: List[List[str]] = None
    conditions: Dict[str, str] = None
    
    def __post_init__(self):
        if self.parallel_stages is None:
            self.parallel_stages = []
        if self.conditions is None:
            self.conditions = {}

class WorkflowBuilder:
    """
    Simple workflow builder that creates and manages workflow patterns.
    Provides templates for common multi-agent coordination scenarios.
    """
    
    def __init__(self):
        self.templates = self._create_workflow_templates()
        self.task_decomposer = create_task_decomposer()
        self.orchestrator = None
        
        print("🏗️ Workflow builder initialized")
        print(f"📋 Available templates: {list(self.templates.keys())}")
    
    def _create_workflow_templates(self) -> Dict[str, WorkflowTemplate]:
        """Create predefined workflow templates"""
        return {
            "research_report": WorkflowTemplate(
                name="research_report",
                description="Complete research report with document analysis and web research",
                agent_sequence=["supervisor", "research_agent", "web_researcher", "analyst", "writer"]
            ),
            
            "market_analysis": WorkflowTemplate(
                name="market_analysis", 
                description="Market analysis with web-first approach",
                agent_sequence=["supervisor", "web_researcher", "research_agent", "analyst", "writer"]
            ),
            
            "quick_research": WorkflowTemplate(
                name="quick_research",
                description="Quick research using only document analysis",
                agent_sequence=["supervisor", "research_agent", "writer"]
            ),
            
            "data_analysis": WorkflowTemplate(
                name="data_analysis",
                description="Focus on data analysis and calculations",
                agent_sequence=["supervisor", "research_agent", "analyst", "writer"]
            ),
            
            "web_research": WorkflowTemplate(
                name="web_research", 
                description="Web-focused research with minimal document analysis",
                agent_sequence=["supervisor", "web_researcher", "analyst", "writer"]
            ),
            
            "comprehensive": WorkflowTemplate(
                name="comprehensive",
                description="Full comprehensive analysis using all agents",
                agent_sequence=["supervisor", "research_agent", "web_researcher", "analyst", "writer"]
            )
        }
    
    def create_workflow(self, 
                       user_goal: str,
                       workflow_type: str = "comprehensive",
                       custom_sequence: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a complete workflow including task plan and orchestrator.
        
        Args:
            user_goal: The goal/task from user
            workflow_type: Type of workflow template to use
            custom_sequence: Optional custom agent sequence
            
        Returns:
            Dictionary with workflow components ready for execution
        """
        try:
            print(f"🏗️ Creating workflow for: {user_goal}")
            
            # Auto-select workflow type if needed
            if workflow_type == "auto":
                workflow_type = self._auto_select_workflow_type(user_goal)
            
            print(f"📋 Using workflow type: {workflow_type}")
            
            # Get or create template
            if custom_sequence:
                template = WorkflowTemplate(
                    name="custom",
                    description="Custom workflow sequence",
                    agent_sequence=custom_sequence
                )
            elif workflow_type in self.templates:
                template = self.templates[workflow_type]
            else:
                template = self.templates["comprehensive"]  # Default fallback
            
            # Create task plan using decomposer
            complexity = self._assess_task_complexity(user_goal)
            task_plan = self.task_decomposer.decompose_task(user_goal, complexity)
            
            # Create orchestrator if not exists
            if not self.orchestrator:
                self.orchestrator = create_orchestrator()
            
            # Prepare workflow configuration
            workflow = {
                "workflow_id": f"workflow_{int(time.time())}",
                "user_goal": user_goal,
                "template": template,
                "task_plan": task_plan,
                "orchestrator": self.orchestrator,
                "status": "ready",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"✅ Workflow created with {len(template.agent_sequence)} agents")
            return workflow
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise
    
    def _auto_select_workflow_type(self, user_goal: str) -> str:
        """Automatically select appropriate workflow type based on user goal"""
        goal_lower = user_goal.lower()
        if any(word in goal_lower for word in ["latest", "news", "current", "update"]):
            return "comprehensive"  # ✅ Full workflow for current info
        elif any(word in goal_lower for word in ["market", "industry", "competitor"]):
            return "market_analysis"  # ✅ Full workflow for market queries
        elif any(word in goal_lower for word in ["analyze", "calculate", "data", "statistics"]):
            return "comprehensive"  # ✅ Full workflow for analysis
        else:
            return "comprehensive"
    
    def _assess_task_complexity(self, user_goal: str) -> str:
        """Assess task complexity based on goal content"""
        word_count = len(user_goal.split())
        
        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "medium"
        else:
            return "complex"
    
    async def execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete workflow.
        
        Args:
            workflow: Workflow dictionary from create_workflow()
            
        Returns:
            Execution results
        """
        try:
            print(f"🚀 Executing workflow: {workflow['workflow_id']}")
            
            orchestrator = workflow["orchestrator"]
            task_plan = workflow["task_plan"]
            user_goal = workflow["user_goal"]
            
            # Execute using orchestrator
            result = await orchestrator.execute_workflow(user_goal, task_plan)
            
            # Update workflow status
            workflow["status"] = result["status"]
            workflow["execution_result"] = result
            workflow["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "workflow_id": workflow.get("workflow_id")
            }
    
    def execute_workflow_sync(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous workflow execution"""
        import asyncio
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.execute_workflow(workflow))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Sync workflow execution error: {e}")
            return {"status": "failed", "error": str(e)}
    
    def list_available_templates(self) -> Dict[str, str]:
        """List all available workflow templates"""
        return {name: template.description for name, template in self.templates.items()}
    
    def get_template_details(self, template_name: str) -> Optional[WorkflowTemplate]:
        """Get details of a specific template"""
        return self.templates.get(template_name)
    
    def create_custom_template(self, 
                              name: str,
                              description: str, 
                              agent_sequence: List[str]) -> WorkflowTemplate:
        """Create and register a custom workflow template"""
        template = WorkflowTemplate(
            name=name,
            description=description,
            agent_sequence=agent_sequence
        )
        
        self.templates[name] = template
        print(f"📋 Created custom template: {name}")
        return template

def create_workflow_builder() -> WorkflowBuilder:
    """Factory function to create workflow builder"""
    return WorkflowBuilder()


