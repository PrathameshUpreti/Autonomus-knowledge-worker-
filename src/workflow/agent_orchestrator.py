"""
Agent Orchestrator - Coordinates multi-agent workflows using AutoGen's DiGraphBuilder.
Manages agent communication and task execution flow.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from autogen_agentchat.teams import DiGraphBuilder , GraphFlow
from autogen_agentchat.conditions import MaxMessageTermination , TextMentionTermination
from autogen_agentchat.ui import Console
from src.agents import get_agent
from .task_decomposer  import TaskPlan,Task
from . import workflow_config 
import time

logger= logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrator that coordinates multi-agent workflows using AutoGen's DiGraphBuilder.
    Manages the execution flow between supervisor, research, web, analyst, and writer agents.
    """
    def __init__(self,agents:Optional[Dict[str,Any]] =None):
        self.agents=agents or {}
        self.autogen_agents ={} # hold agents converted to AutoGen-compatible objects.
        self.workflow_graph= None
        self.current_execution = None

        self.execution_history= []
        self.current_task_plan = None

        self.setup_agents()
        print("🎭 Agent orchestrator initialized")
        print(f"🤖 Available agents: {list(self.agents.keys())}")


    def setup_agents(self):
         """Initialize and prepare agents for orchestration"""
         try:
             if not self.agents:
                 from src.agents import agent_manager
                 self.agents=agent_manager.agents

             self.autogen_agents ={}
             for name, agent in self.agents.items():
                 try:
                     autogen_agent= agent.create_autogen_agent()
                     self.autogen_agents[name]=autogen_agent
                     print(f"{name} ready for orchestrotion")
                 except Exception as e:
                     print(f"  ❌ {name} setup failed: {e}")
                     logger.error(f"Agent setup failed for {name}: {e}")

             print(f"🎯 {len(self.autogen_agents)} agents ready for orchestration")

         except Exception as e:
             logger.error(f"Error setting up agents: {e}")
             raise
    
    def build_workflow_graph(self,task_plan:TaskPlan) -> DiGraphBuilder:
        """
        Goal: Create a graph showing how agents are connected based on the task plan.
        Build AutoGen workflow graph based on task plan.
        Creates nodes for agents and edges for task flow.

        """
        try:
            print("🔧 Building workflow graph...")

            builder=DiGraphBuilder()

            agents_needed= list(set(task.agent_type for task in task_plan.tasks))

            for agent_type in agents_needed:
                if agent_type in self.autogen_agents:
                    builder.add_node(self.autogen_agents[agent_type])
                    print(f"  📍 Added node: {agent_type}")
                else:
                    logger.warning(f"Agent {agent_type} not available")

            for task in task_plan.tasks:
                current_agent=task.agent_type

                for dep_task_id in task.dependencies:
                    dep_task=next((t for t in task_plan.tasks if t.id==dep_task_id), None)

                    if dep_task and dep_task.agent_type in self.autogen_agents:
                        prev_agent=dep_task.agent_type

                        builder.add_edge(
                            self.autogen_agents[prev_agent],
                            self.autogen_agents[current_agent]
                        )
                        print(f"  🔗 Added edge: {prev_agent} → {current_agent}")
            
            self.workflow_graph=builder
            print("✅ Workflow graph built successfully")

            return builder
        except Exception as e:
             logger.error(f"Error building workflow graph: {e}")
             raise
    
    def build_simple_sequential_workflow(self) -> DiGraphBuilder:
        """
        Build a simple sequential workflow: supervisor → research → web → analyst → writer
        Use this when task plan is not available or for simple workflows.
        """
        try:
            print("🔧 Building simple sequential workflow...")
            
            builder = DiGraphBuilder()

            sequence= ["supervisor", "research_agent", "web_researcher", "analyst", "writer"]
            available_agent=[]

            for agent_name in sequence:
                if agent_name in self.autogen_agents:
                    builder.add_node(self.autogen_agents[agent_name])
                    available_agent.append(agent_name)
                    print(f"  📍 Added node: {agent_name}")

            
            for i in range (len(available_agent)- 1):
                current= available_agent[i]
                next_agent=available_agent[i+1]

                builder.add_edge(
                    self.autogen_agents[current],
                    self.autogen_agents[next_agent]
                )
                print(f"  🔗 Added edge: {current} → {next_agent}")
            
            self.workflow_graph=builder
            print("✅ Simple sequential workflow built")
            return builder
        
        except Exception as e:
            logger.error(f"Error building simple workflow: {e}")
            raise
    
    async def execute_workflow(self,user_task: str, task_plan:Optional[TaskPlan]=None, max_iteration: int=10) -> Dict[str,Any]:
        """
        Execute multi-agent workflow using AutoGen's GraphFlow.
        
        Args:
            user_task: The initial task/query from user
            task_plan: Optional structured task plan
            max_iterations: Maximum number of message exchanges
            
        Returns:
            Dictionary with execution results and metadata
        """
        try:
            print(f"🚀 Starting workflow execution...")
            print(f"📝 Task: {user_task}")

            start_time=time.time()

            if task_plan:
                self.current_task_plan=task_plan
                builder=self.build_workflow_graph(task_plan)
            else:
                builder=self.build_simple_sequential_workflow()

            termination_condition= MaxMessageTermination(max_iteration)

            graph= builder.build()
            participants=builder.get_participants()

            flow= GraphFlow(
                participants=participants,
                graph=graph,
                termination_condition=termination_condition
            )
            print(f"🎯 Starting execution with {len(participants)} agents...")

            execution_result= []

            async for message in flow.run_stream(task=user_task):
                execution_result.append(str(message))
                print(f"📢 {message}")
            
            execution_time=time.time() - start_time

            result={
                "status": "completed",
                "user_task": user_task,
                "execution_time": round(execution_time, 2),
                "agents_used": len(participants),
                "messages_exchanged": len(execution_result),
                "final_output": execution_result[-1] if execution_result else "No output generated",
                "execution_log": execution_result,
                "task_plan_id": task_plan.plan_id if task_plan else None,
                "completed_at": time.strftime("%Y-%m-%d %H:%M:%S")

            }
            self.execution_history.append(result)
            print(f"✅ Workflow completed in {execution_time:.1f}s")
            print(f"📊 {len(execution_result)} messages exchanged")
            
            return result
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "user_task": user_task,
                "completed_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def execute_workflow_sync(self, user_task: str, task_plan: Optional[TaskPlan] = None) -> Dict[str, Any]:
        """
        Synchronous wrapper for workflow execution.
        Use this for easier integration in non-async environments.
        """
        try:
            # Run async workflow in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.execute_workflow(user_task, task_plan))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Sync workflow execution error: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "user_task": user_task
            }
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status and statistics"""
        return {
            "total_executions": len(self.execution_history),
            "agents_available": len(self.autogen_agents),
            "agents_ready": list(self.autogen_agents.keys()),
            "current_task_plan": self.current_task_plan.plan_id if self.current_task_plan else None,
            "last_execution": self.execution_history[-1] if self.execution_history else None
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of all workflow executions"""
        return self.execution_history.copy()
    
    def clear_execution_history(self):
        """Clear execution history"""
        self.execution_history.clear()
        print("🗑️ Execution history cleared")

def create_orchestrator(agents: Optional[Dict[str, Any]] = None) -> AgentOrchestrator:
    """Factory function to create agent orchestrator"""
    return AgentOrchestrator(agents)
    

            






             

                     
             



    
