"""
Task Decomposer - Breaks down complex tasks into manageable subtasks.
Works with the Supervisor Agent to create structured task plans.
"""

import  logging
from typing import  Dict , List, Optional, Any
from dataclasses import dataclass
from . import workflow_config
import time

logger=logging.getLogger(__name__)


"""
This file defines a Task Decomposer, whose job is to take a big goal from the user (e.g., “Do a market analysis for AI startups”) and break it down into smaller agent-specific tasks.

It works closely with a Supervisor Agent (and possibly other agents) to make structured, step-by-step execution plans.

"""
"""
A dataclass in Python is a decorator (@dataclass) that automatically generates special methods like __init__, __repr__, __eq__, etc., so you don’t have to write boilerplate code.
"""
@dataclass
class Task:
    """Simple task representation"""
    id:str
    description:str
    agent_type:str
    priority:str="normal"
    dependencies: List[str] = None
    status:str="pending"
    result:Optional[str]=None
    created_at:str=""

    def __post_init__(self):
        """__post_init__ is a special method in Python that is used with dataclasses.
        When you use a @dataclass in Python, it automatically creates the __init__ method for you (so you don’t have to write it yourself).
      But sometimes, after all the attributes have been set by __init__, you might want to do extra setup or validation.
        """
        if self.dependencies is None:
            self.dependencies=[]
        if  not self.created_at:
            self.created_at=time.strftime("%Y-%m-%d %H:%M:%S")

@dataclass

class TaskPlan:
     """Complete task plan with multiple tasks"""
     plan_id:str
     user_goal:str
     tasks: List[Task]
     total_tasks:int=0
     status:str="created"
     created_at:str=""

     def __post_init__(self):
         self.total_tasks=len(self.tasks)
         if not self.created_at:
             self.created_at= time.strftime("%Y-%m-%d %H:%M:%S")

class TaskDecomposer:
    """
    task decomposer that breaks complex goals into agent-specific tasks.
    Works with supervisor agent to create structured execution plans.
    """
    def __init__(self):
        self.task_template=self.load_task_template()
        self.agent_capabilties=self.define_agent_capabilities()
        self.task_counter=0 #used to create unique IDs.

    def load_task_template(self)->Dict[str,Dict]:
         """Define templates for common task patterns"""
         return{
             "research-analysis":{
                 "sequence":["supervisor", "research_agent", "web_researcher", "analyst", "writer"],
                 "description":"Research a topic, gather current info, analyze, and create report"
                 
             },
             "market_analysis": {
                "sequence": ["supervisor", "web_researcher", "research_agent", "analyst", "writer"],
                "description": "Analyze market conditions with web data and documents"
            },
            "competitive_analysis": {
                "sequence": ["supervisor", "research_agent", "web_researcher", "analyst", "writer"],
                "description": "Compare competitors using multiple information sources"
            },
            "simple_research": {
                "sequence": ["supervisor", "research_agent", "writer"],
                "description": "Simple document research with report creation"
            }
         }
    
    def define_agent_capabilities(self)->Dict[str,Dict]:
         """Define what each agent type can do"""
         return{
             "supervisor": {
                "capabilities": ["task_planning", "coordination", "quality_control"],
                "inputs": ["user_goals", "requirements"],
                "outputs": ["task_plans", "agent_assignments"]
            },
            "research_agent": {
                "capabilities": ["document_analysis", "rag_search", "citation_management"],
                "inputs": ["research_questions", "document_paths"],
                "outputs": ["research_findings", "citations", "source_analysis"]
            },
            "web_researcher": {
                "capabilities": ["web_search", "content_extraction", "source_verification"],
                "inputs": ["search_queries", "urls"],
                "outputs": ["web_findings", "current_information", "web_citations"]
            },
            "analyst": {
                "capabilities": ["data_analysis", "calculations", "trend_analysis"],
                "inputs": ["data", "research_findings", "calculations_needed"],
                "outputs": ["analysis_results", "insights", "recommendations"]
            },
            "writer": {
                "capabilities": ["report_creation", "content_synthesis", "formatting"],
                "inputs": ["research_findings", "analysis_results", "citations"],
                "outputs": ["reports", "documents", "summaries"]
            }
             
         }
    
    def decompose_task(self,user_goal:str,complexity:str="medium") -> TaskPlan:
         """
        Break down a user goal into specific tasks for different agents.
        
        Args:
            user_goal: The high-level goal from the user
            complexity: Task complexity level (simple, medium, complex)
            
        Returns:
        TaskPlan with structured tasks for agents

        """
         try:
             print(f"Decomposing the task :{user_goal}")
             plan_id=f"plan_{int(time.time())}_{self.task_counter}" 
         #Uses the current time (time.time()) so each plan ID is unique.
         #task_counter ensures uniqueness even if two plans are created in the same second.
             self.task_counter += 1
             template_name= self.select_template(user_goal,complexity)
             template=self.task_template[template_name]
             print(f"using template:{template_name}")

             tasks=[]
             agent_sequence=template["sequence"]
             for i , agent_type in enumerate(agent_sequence):
                 task_id=f"{plan_id}_task_{i+1}"
                 task_description=self.create_task_description(agent_type,user_goal,i)

                 dependencices=[]
             #First task (i=0) → no dependencies.
             # Later tasks → depend on the previous one.
                 if i>0:
                     dependencices=[f"{plan_id}_task{i}"]
             

                 priority="high" if agent_type=="supervisor" else "normal"

                 task=Task(
                 id=task_id,
                 description=task_description,
                 agent_type=agent_type,
                 priority=priority,
                 dependencies=dependencices
                 )
                 tasks.append(task)

             task_plan= TaskPlan(
                 plan_id=plan_id,
                 user_goal=user_goal,
                 tasks=tasks
                 )
             print(f"✅ Created task plan with {len(tasks)} tasks")
             return task_plan
         
         except Exception as e:
             logger.error(f"Error decomposing task: {e}")
             return self.create_fallback_plan(user_goal)
         
    def select_template(self,user_goal:str, complexity:str)->str:
         """Select appropriate task template based on goal and complexity"""
         goal_lower=user_goal.lower()

         if any(word in goal_lower for word in ["latest", "news", "current", "recent", "update"]):
             return "comprehensive"  
         
         elif any(word in goal_lower for word in ["detail", "ai", "code", ]):
             return "search_analysis" 
         
         elif any(word in goal_lower for word in ["reserch", "search", "ai","code"]):
             return "research_analysis" 
         elif any(word in goal_lower for word in ["market", "industry", "sector","stock"]):
             return "market_analysis" 
         elif any(word in goal_lower for word in ["competitor", "competitive", "compare"]):
             return "competitive_analysis" 
         else:
             return "comprehensive"
    
    def  load_task_templates(self) -> Dict[str,Dict]:
         """Define templates for common task patterns"""
         return {
        "research_analysis": {
            "sequence": ["supervisor", "research_agent", "web_researcher", "analyst", "writer"],  
            "description": "Research a topic, gather current info, analyze, and create report"
        },
        "market_analysis": {
            "sequence": ["supervisor", "web_researcher", "research_agent", "analyst", "writer"],  
            "description": "Analyze market conditions with web data and documents"
        },
        "competitive_analysis": {
            "sequence": ["supervisor", "research_agent", "web_researcher", "analyst", "writer"], 
            "description": "Compare competitors using multiple information sources"
        },
        "comprehensive": { 
            "sequence": ["supervisor", "research_agent", "web_researcher", "analyst", "writer"],
            "description": "Complete analysis using all available agents"
        }
    }
         


         
    
    def create_task_description(self,agent_type:str,user_goal:str,step_number:int)->str:
        """Create specific task description for each agent"""
        base_descriptions = {
            "supervisor": f"Analyze the goal '{user_goal}' and create a detailed execution plan. Coordinate the overall workflow and ensure quality standards.",
            
            "research_agent": f"Research '{user_goal}' using available documents and knowledge base. Extract relevant information and provide proper citations.",
            
            "web_researcher": f"Search for current information about '{user_goal}' from internet sources. Find latest news, trends, and developments.",
            
            "analyst": f"Analyze the research findings related to '{user_goal}'. Perform calculations, identify trends, and generate data-driven insights.",
            
            "writer": f"Create a comprehensive report about '{user_goal}' based on all research and analysis. Include executive summary, findings, and recommendations."
        }
        return base_descriptions.get(agent_type, f"Process information related to '{user_goal}'")
    

    def create_fallback_plan(self, user_goal : str)-> TaskPlan:
         """Create simple fallback plan if decomposition fails"""

         plan_id = f"fallback_{int(time.time())}"

         tasks = [
        Task(
            id=f"{plan_id}_task_1",
            description=f"Analyze and create execution plan for: {user_goal}",
            agent_type="supervisor"
        ),
        Task(
            id=f"{plan_id}_task_2", 
            description=f"Research existing documents and knowledge about: {user_goal}",
            agent_type="research_agent",
            dependencies=[f"{plan_id}_task_1"]
        ),
        Task(
            id=f"{plan_id}_task_3",
            description=f"Search web for current information about: {user_goal}",
            agent_type="web_researcher", 
            dependencies=[f"{plan_id}_task_2"]
        ),
        Task(
            id=f"{plan_id}_task_4",
            description=f"Analyze and process all gathered information about: {user_goal}",
            agent_type="analyst",
            dependencies=[f"{plan_id}_task_3"]
        ),
        Task(
            id=f"{plan_id}_task_5",
            description=f"Create comprehensive final report about: {user_goal}",
            agent_type="writer",
            dependencies=[f"{plan_id}_task_4"]
        )
    ]
         return TaskPlan(
            plan_id=plan_id,
            user_goal=user_goal,
            tasks=tasks
          )
    
    def update_task_status(self,task_id:str,status:str,result:Optional[str] = None):
        """Update the status of a specific task"""
        logger.info(f"Task {task_id} status updated to: {status}")
        if result:
            logger.debug(f"Task result preview: {result[:100]}...")

    def get_next_ready_task(self,task_plan:TaskPlan)->List[Task]:
        """Get tasks that are ready to execute (dependencies completed)"""

        ready_tasks=[]
        for task in task_plan.tasks:
            if task.status =="pending":
                dependencies_completed= True
                for dep_id in task.dependencies:
                    dep_task = next((t for t in task_plan.tasks if t.id == dep_id), None)
                    if not dep_task or dep_task.status != "completed":
                        dependencies_completed = False
                        break
                
                if dependencies_completed:
                    ready_tasks.append(task)
        
        return ready_tasks
    def get_task_summary(self, task_plan: TaskPlan) -> Dict[str, Any]:
        """Get summary of task plan status"""
        status_counts = {}
        for task in task_plan.tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
        
        return {
            "plan_id": task_plan.plan_id,
            "user_goal": task_plan.user_goal,
            "total_tasks": task_plan.total_tasks,
            "status_breakdown": status_counts,
            "overall_status": task_plan.status,
            "created_at": task_plan.created_at
        }
def create_task_decomposer() -> TaskDecomposer:
    """Factory function to create task decomposer"""
    return TaskDecomposer()














         
    









    
         



    

