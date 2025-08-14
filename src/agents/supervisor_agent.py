"""
Supervisor Agent with coordination tools - AutoGen 0.6+
Main orchestrator for task decomposition and workflow coordination.
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .base_agent import BaseAgent
from src.tools import get_tool
from typing import Optional, Dict,Any,List
import logging
import time

logger = logging.getLogger(__name__)

class SupervisorAgent(BaseAgent):
    """
    Supervisor agent with task coordination and planning tools
    """
    
    def __init__(self):
        system_message = """You are the Supervisor Agent, the main coordinator of our autonomous knowledge-worker system.

YOUR KEY RESPONSIBILITIES:
1. **Task Analysis**: Understand user's high-level goals and requirements
2. **Task Decomposition**: Break down complex tasks into specific, actionable subtasks  
3. **Agent Assignment**: Decide which specialized agents should handle each subtask
4. **Workflow Planning**: Create logical sequence of agent interactions
5. **Quality Control**: Ensure all subtasks are completed properly
6. **Final Integration**: Coordinate creation of final deliverables

COORDINATION PROCESS:
1. Analyze the user's request carefully using create_task_plan
2. Break down into specific, measurable subtasks
3. Assign each subtask to appropriate agents using assign_agent
4. Monitor progress with track_progress
5. Ensure quality and integration of results

AGENT SPECIALIZATIONS:
- **Research Agent**: Document-based research and knowledge retrieval
- **Web Researcher**: Current information from internet sources  
- **Analyst**: Data analysis, calculations, and technical evaluation
- **Writer**: Report creation, formatting, and final documentation

Always create clear, numbered plans with specific agent assignments and expected deliverables."""

        super().__init__(
            name="supervisor",
            description="Task Supervisor and Workflow Coordinator", 
            system_message=system_message
      
        )
    
    def register_tools(self):
        """Register coordination tools for the supervisor"""
        
        async def create_task_plan_async(user_goal: str) -> str:
            """
            Break down a user goal into specific, actionable tasks for different agents.
            
            Args:
                user_goal: The high-level goal or request from the user
                
            Returns:
                Detailed task breakdown with agent assignments
            """
            
            self.save_to_memory("current_goal", user_goal)
            
           
            plan = f"""
🎯 TASK BREAKDOWN FOR: {user_goal}
Generated: {self._get_timestamp()}

PHASE 1: RESEARCH & INFORMATION GATHERING
├─ Task 1.1: Document Research
│  ├─ Agent: research_agent
│  ├─ Action: Search knowledge base and documents for background information
│  └─ Expected: Key facts, definitions, historical context with citations

├─ Task 1.2: Current Information Gathering  
│  ├─ Agent: web_researcher
│  ├─ Action: Find latest news, trends, and current developments
│  └─ Expected: Up-to-date information with web source citations

PHASE 2: ANALYSIS & PROCESSING
├─ Task 2.1: Data Analysis
│  ├─ Agent: analyst
│  ├─ Action: Process data, perform calculations, identify patterns
│  └─ Expected: Statistical insights, trends, numerical analysis

PHASE 3: SYNTHESIS & DOCUMENTATION
├─ Task 3.1: Report Creation
│  ├─ Agent: writer
│  ├─ Action: Synthesize all findings into comprehensive report
│  └─ Expected: Professional document with executive summary and references

COORDINATION NOTES:
• Each phase builds on the previous one
• All agents must provide proper citations for their sources
• Final deliverable should be actionable and comprehensive
• Supervisor will monitor progress and ensure quality at each step

NEXT STEPS:
1. Begin with research_agent for document analysis
2. Proceed to web_researcher for current information
3. Move to analyst for data processing
4. Conclude with writer for final documentation
"""
            
            self.save_to_memory("task_plan", plan)
            return plan
        
        async def assign_agent_async(task_description: str, agent_type: str, priority: str = "normal") -> str:
            """
            Assign a specific task to the most appropriate agent.
            
            Args:
                task_description: Detailed description of the task to be performed
                agent_type: Type of agent to assign (research_agent, web_researcher, analyst, writer)
                priority: Task priority level (low, normal, high, urgent)
                
            Returns:
                Task assignment confirmation with details
            """
            valid_agents = ["research_agent", "web_researcher", "analyst", "writer"]
            if agent_type not in valid_agents:
                return f"❌ Invalid agent type: {agent_type}. Must be one of: {', '.join(valid_agents)}"
            
            assignment = f"""
📋 TASK ASSIGNMENT CREATED
Timestamp: {self._get_timestamp()}

ASSIGNMENT DETAILS:
├─ Agent: {agent_type}
├─ Priority: {priority.upper()}
├─ Status: ASSIGNED
└─ Task: {task_description}

AGENT CAPABILITIES:
"""
            
            
            if agent_type == "research_agent":
                assignment += """├─ Document processing (PDF, Word, text, HTML, Markdown)
├─ Knowledge base search and analysis  
├─ Citation management and source verification
└─ Information synthesis from multiple documents"""
            elif agent_type == "web_researcher":
                assignment += """├─ Internet search and information gathering
├─ Web content extraction and analysis
├─ Source credibility evaluation
└─ Current trends and news monitoring"""
            elif agent_type == "analyst":
                assignment += """├─ Mathematical calculations and statistical analysis
├─ Code execution for data processing
├─ Trend identification and pattern analysis
└─ Data-driven insights and recommendations"""
            elif agent_type == "writer":
                assignment += """├─ Professional report and document creation
├─ Content structuring and formatting
├─ Citation integration and reference management
└─ Executive summaries and recommendations"""
            
            assignment += f"""

NEXT STEPS:
1. {agent_type} should begin working on this task immediately
2. Provide regular progress updates
3. Ensure all outputs include proper citations
4. Coordinate with supervisor for quality review

Assignment ID: {len(self.memory.get('assignments', [])) + 1}
"""
            
            # Store assignment in memory
            assignments = self.memory.get('assignments', [])
            assignments.append({
                'id': len(assignments) + 1,
                'agent': agent_type,
                'task': task_description,
                'priority': priority,
                'assigned_at': self._get_timestamp(),
                'status': 'assigned'
            })
            self.save_to_memory('assignments', assignments)
            
            return assignment
        
        async def track_progress_async(agent_name: str, status: str, details: str = "") -> str:
            """
            Track and monitor progress of tasks assigned to agents.
            
            Args:
                agent_name: Name of the agent providing the update
                status: Current status (in_progress, completed, blocked, needs_review)
                details: Additional details about the progress
                
            Returns:
                Progress tracking summary with next steps
            """
            valid_statuses = ["in_progress", "completed", "blocked", "needs_review", "waiting"]
            if status not in valid_statuses:
                return f"❌ Invalid status: {status}. Must be one of: {', '.join(valid_statuses)}"
            
            progress_update = f"""
📊 PROGRESS UPDATE
Timestamp: {self._get_timestamp()}

AGENT STATUS:
├─ Agent: {agent_name}
├─ Status: {status.upper().replace('_', ' ')}
├─ Update: {details if details else 'No additional details provided'}
└─ Logged: {self._get_timestamp()}

WORKFLOW STATUS:
"""
            
            # Add status-specific guidance
            if status == "completed":
                progress_update += """├─ ✅ Task completed successfully
├─ Next: Ready for next phase or quality review
└─ Action: Supervisor to review deliverables and assign next task"""
            elif status == "in_progress":
                progress_update += """├─ 🔄 Task in progress
├─ Next: Continue current work
└─ Action: Provide updates as work progresses"""
            elif status == "blocked":
                progress_update += """├─ ⚠️ Task blocked - needs attention
├─ Next: Resolve blocking issues
└─ Action: Supervisor to provide guidance or reassign resources"""
            elif status == "needs_review":
                progress_update += """├─ 👀 Task needs supervisor review
├─ Next: Await supervisor feedback
└─ Action: Supervisor to review and provide feedback"""
            else:  # waiting
                progress_update += """├─ ⏳ Task waiting for dependencies
├─ Next: Monitor dependency completion
└─ Action: Resume when dependencies are ready"""
            
            # Update progress in memory
            progress_history = self.memory.get('progress_history', [])
            progress_history.append({
                'agent': agent_name,
                'status': status,
                'details': details,
                'timestamp': self._get_timestamp()
            })
            self.save_to_memory('progress_history', progress_history)
            
            return progress_update
        
        # Create FunctionTool instances
        self.function_tools = [
            FunctionTool(
                create_task_plan_async,
                description="Break down complex user goals into specific, actionable tasks with agent assignments"
            ),
            FunctionTool(
                assign_agent_async,
                description="Assign specific tasks to the most appropriate specialist agent with priority levels"
            ),
            FunctionTool(
                track_progress_async,
                description="Monitor and track progress of tasks assigned to agents with status updates"
            )
        ]
    
    def create_autogen_agent(self):
        """Create AutoGen supervisor agent with coordination tools"""
        try:
            model_client = OpenAIChatCompletionClient(
                model=self.model_confrig["model"],
                api_key=self.model_confrig["api_key"],
            )
            
            agent = AssistantAgent(
                name=self.name,
                model_client=model_client,
                system_message=self.get_full_system_message(),
                tools=self.function_tools
            )
            
            logger.info(f"✅ Created supervisor with {len(self.function_tools)} coordination tools")
            return agent
            
        except Exception as e:
            logger.error(f"❌ Error creating {self.name}: {e}")
            raise
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_workflow_status(self) -> Dict:
        """Get current workflow status"""
        return {
            "current_goal": self.get_from_memory("current_goal"),
            "task_plan": self.get_from_memory("task_plan"),
            "assignments": self.get_from_memory("assignments"),
            "progress_history": self.get_from_memory("progress_history")
        }

def create_supervisor() -> SupervisorAgent:
    """Factory function to create supervisor agent"""
    return SupervisorAgent()
