"""
Execution Manager - Manages workflow execution, monitoring, and state.
Provides simple interface for running autonomous knowledge-worker workflows.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from .workflow_builder import WorkflowBuilder, create_workflow_builder
from .task_decomposer import TaskPlan
from . import workflow_config

logger = logging.getLogger(__name__)

class ExecutionManager:
    """
    Simple execution manager that provides high-level interface for workflow execution.
    Handles workflow creation, execution, monitoring, and results management.
    """
    
    def __init__(self):
        self.workflow_builder = create_workflow_builder()
        self.active_workflows = {}
        self.completed_workflows = {}  
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time": 0
        }
        
        print("⚡ Execution manager initialized")
        print("🎯 Ready to run autonomous knowledge-worker workflows")
    
    def run_autonomous_workflow(self, 
                               user_request: str,
                               workflow_type: str = "auto",
                               save_results: bool = True) -> Dict[str, Any]:
        """
        Main entry point: Run complete autonomous knowledge-worker workflow.
        
        Args:
            user_request: Natural language request from user
            workflow_type: Type of workflow to use (auto, research_report, etc.)
            save_results: Whether to save results to files
            
        Returns:
            Complete workflow results with all outputs
        """
        try:
            print("🚀 Starting Autonomous Knowledge-Worker Workflow")
            print("=" * 60)
            print(f"📝 User Request: {user_request}")
            print(f"🔧 Workflow Type: {workflow_type}")
            print("-" * 60)
            
            start_time = time.time()
            
            # Step 1: Create workflow
            print("1️⃣ Creating workflow...")
            workflow = self.workflow_builder.create_workflow(
                user_goal=user_request,
                workflow_type=workflow_type
            )
            
            workflow_id = workflow["workflow_id"]
            self.active_workflows[workflow_id] = workflow
            
            print(f"   ✅ Workflow created: {workflow_id}")
            print(f"   🤖 Agents: {', '.join(workflow['template'].agent_sequence)}")
            print(f"   📋 Tasks: {workflow['task_plan'].total_tasks}")
            
            # Step 2: Execute workflow
            print("\n2️⃣ Executing multi-agent workflow...")
            execution_result = self.workflow_builder.execute_workflow_sync(workflow)
            
            # Step 3: Process results
            print("\n3️⃣ Processing results...")
            final_result = self._process_execution_result(
                workflow, 
                execution_result, 
                save_results
            )
            
            # Step 4: Update statistics
            execution_time = time.time() - start_time
            self._update_stats(execution_result["status"], execution_time)
            
            # Move to completed workflows
            self.completed_workflows[workflow_id] = workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            print("\n" + "=" * 60)
            print(f"✅ Autonomous workflow completed in {execution_time:.1f}s")
            print(f"📊 Status: {execution_result['status']}")
            if execution_result["status"] == "completed":
                print(f"📄 Report generated and saved")
            print("=" * 60)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Autonomous workflow execution error: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "user_request": user_request,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _process_execution_result(self, 
                                 workflow: Dict[str, Any],
                                 execution_result: Dict[str, Any],
                                 save_results: bool) -> Dict[str, Any]:
        """Process and format final execution results"""
        
        # Extract key information
        final_output = execution_result.get("final_output", "")
        execution_log = execution_result.get("execution_log", [])
        
        # Create comprehensive result
        result = {
            "status": execution_result["status"],
            "workflow_id": workflow["workflow_id"],
            "user_request": workflow["user_goal"],
            "workflow_type": workflow["template"].name,
            
            # Execution details
            "execution_time": execution_result.get("execution_time", 0),
            "agents_used": len(workflow["template"].agent_sequence),
            "tasks_completed": workflow["task_plan"].total_tasks,
            "messages_exchanged": execution_result.get("messages_exchanged", 0),
            
            # Outputs
            "final_report": final_output,
            "execution_log": execution_log,
            
            # Metadata
            "created_at": workflow["created_at"],
            "completed_at": execution_result.get("completed_at"),
            "agents_sequence": workflow["template"].agent_sequence
        }
        
        # Save results if requested
        if save_results and execution_result["status"] == "completed":
            self._save_workflow_results(result)
        
        return result
    
    def _save_workflow_results(self, result: Dict[str, Any]):
        """Save workflow results to files"""
        try:
            output_dir = workflow_config.workflow_output_dir
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Save final report
            report_filename = f"report_{timestamp}_{result['workflow_id']}.md"
            report_path = output_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"# Autonomous Knowledge-Worker Report\n\n")
                f.write(f"**User Request:** {result['user_request']}\n\n")
                f.write(f"**Workflow Type:** {result['workflow_type']}\n\n")
                f.write(f"**Generated:** {result['completed_at']}\n\n")
                f.write(f"**Execution Time:** {result['execution_time']}s\n\n")
                f.write("---\n\n")
                f.write(result['final_report'])
            
            # Save execution log
            log_filename = f"execution_log_{timestamp}_{result['workflow_id']}.txt"
            log_path = output_dir / log_filename
            
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"Execution Log - {result['workflow_id']}\n")
                f.write("=" * 50 + "\n\n")
                for i, message in enumerate(result['execution_log'], 1):
                    f.write(f"Message {i}:\n{message}\n\n")
            
            result['saved_files'] = {
                'report': str(report_path),
                'execution_log': str(log_path)
            }
            
            print(f"💾 Results saved:")
            print(f"   📄 Report: {report_path}")
            print(f"   📋 Log: {log_path}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def _update_stats(self, status: str, execution_time: float):
        """Update execution statistics"""
        self.execution_stats["total_executions"] += 1
        self.execution_stats["total_execution_time"] += execution_time
        
        if status == "completed":
            self.execution_stats["successful_executions"] += 1
        else:
            self.execution_stats["failed_executions"] += 1
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status and statistics"""
        return {
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.completed_workflows),
            "statistics": self.execution_stats.copy(),
            "success_rate": (
                self.execution_stats["successful_executions"] / 
                max(self.execution_stats["total_executions"], 1) * 100
            ),
            "average_execution_time": (
                self.execution_stats["total_execution_time"] / 
                max(self.execution_stats["total_executions"], 1)
            )
        }
    
    def list_available_workflows(self) -> Dict[str, str]:
        """List all available workflow types"""
        return self.workflow_builder.list_available_templates()
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get history of completed workflows"""
        return [
            {
                "workflow_id": wf["workflow_id"],
                "user_goal": wf["user_goal"], 
                "template": wf["template"].name,
                "status": wf.get("status", "unknown"),
                "created_at": wf["created_at"],
                "completed_at": wf.get("completed_at")
            }
            for wf in self.completed_workflows.values()
        ]

def create_execution_manager() -> ExecutionManager:
    """Factory function to create execution manager"""
    return ExecutionManager()
