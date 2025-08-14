"""
Main entry point for the Autonomous Knowledge-Worker Agent System
Integrates all components: agents, RAG, workflows, and provides CLI interface.
"""

import logging
import sys
import time
import asyncio
from pathlib import Path
from typing import  Dict , Any, Optional

from src.confrig.settings import settings
from src.agents import create_all_agents,agent_manager
from src.rag import setup_rag_system
from src.workflow import create_execution_manager
from src.tools import validate_all_tools

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('autonomous_agent.log')
    ]
)
logger=logging.getLogger(__name__)

class AutonomousKnowledgeWorker:
    """
    Main class that integrates all components of the autonomous knowledge-worker system.
    Provides high-level interface for running the complete agent system.
    """

    def __init__(self):
        self.agent={}
        self.rag_system=None
        self.execution_manager=None
        self.is_initialized=False

        print("🤖 Initializing Autonomous Knowledge-Worker Agent System")
        print("=" * 60)

    def initialize_system(self)->bool:
        """
        Initialize all system components: agents, RAG, workflows, tools.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            print("1️⃣ Validating system configuration...")

            if not self.validate_confriguration():
                return False
            print("   ✅ Configuration validated")

            tool_validation = validate_all_tools()
            failed_tools= [name for name, valid in tool_validation.items() if not valid]

            if failed_tools:
                print(f"   ❌ Failed tools: {', '.join(failed_tools)}")
                return False
            print(f"   ✅ All {len(tool_validation)} tools validated")

            print("\n 3️⃣ Setting up RAG system...")
            self.rag_system = setup_rag_system()
            print("   ✅ RAG system initialized")

            print("\n4️⃣ Creating agent system...")
            self.agents = create_all_agents()
            if not self.agents:
                print("   ❌ No agents were created! Check agent creation process.")
                return False
            print(f"   ✅ {len(self.agents)} agents created and ready")
            print(f"   🤖 Agents: {list(self.agents.keys())}")


            print("\n5️⃣ Setting up workflow execution manager...")
            self.execution_manager = create_execution_manager()
            print("   ✅ Execution manager ready")

            print("\n6️⃣ Indexing knowledge base...")
            self.index_knowledge_base()
            
            self.is_initialized = True
            print("\n" + "=" * 60)
            print("✅ Autonomous Knowledge-Worker Agent System Ready!")
            print("🎯 You can now ask complex questions and get comprehensive reports")
            print("=" * 60)
            
            return True
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            print(f"❌ System initialization failed: {e}")
            return False





            


    

    def validate_confriguration(self)->bool:
         """Validate system configuration
         1. Checking for LLM Model connected or not 
         2. Check for directories exixt or not

         
         """

         try:
             if not settings.openai_api_key or settings.openai_api_key=="your-openai-api-key":
                 print("   ❌ OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
                 return  False
             
             settings.docs_dir.mkdir(parents=True, exist_ok=True)
             settings.output_dir.mkdir(parents=True, exist_ok=True)
             settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
            
             return True
         
         except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
         
        
    def index_knowledge_base(self):
         """Index any documents in the knowledge base"""
         try:
             docs_dir=settings.docs_dir
             if docs_dir.exists() and any(docs_dir.iterdir()):
                 success = self.rag_system.index_documents(str(docs_dir))
                 if success:
                    print("   ✅ Knowledge base indexed successfully")
                 else:
                    print("   ⚠️ Knowledge base indexing had issues (check logs)")
             else:
                print("   📝 No documents found in knowledge base - you can add them later")

         except Exception as e:
             logger.warning(f"Knowledge base indexing error: {e}")
             print("   ⚠️ Knowledge base indexing failed (system will still work)")

        
    def rn_query(self,user_query:str,workflow_type:str="auto")->Dict[str,Any]:
        """
        Main method to process user queries through the autonomous agent system.
        
        Args:
            user_query: Natural language query from user
            workflow_type: Type of workflow to use (auto, research_report, etc.)
            
        Returns:
            Complete results from autonomous processing
        """

        if not self.is_initialized:
            raise  RuntimeError("System not initialized. Call initialize_system() first.")
        
        print(f"\n🔍 Processing Query: {user_query}")
        print("-" * 60)

        try:
            result=self.execution_manager.run_autonomous_workflow(
                user_request=user_query,
                workflow_type=workflow_type,
                save_results=True
            )
            return result
        
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "user_query": user_query
            }
        
    
    def interactive_mode(self):
        """
        Run interactive CLI mode for continuous user interaction.
        """

        if not self.is_initialized:
            print("❌ System not initialized. Please run initialize_system() first.")
            return
        
        print("\n🎯 Interactive Mode Started")
        print("=" * 40)
        print("💡 Ask me anything! I'll research and provide comprehensive answers.")
        print("💡 Type 'quit', 'exit', or 'q' to stop")
        print("💡 Type 'help' for available commands")
        print("=" * 40)

        while True:
            try:
                user_input=input("\n🤖 Ask me anything: ").strip()

                if user_input.lower() in ['quit','exit','q']:
                    print("Goodbye")
                    break
                elif user_input.lower() =='help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'status':
                    self.show_status()
                    continue
                elif not user_input:
                    continue

                result= self.rn_query(user_input)

                if result['status'] =='completed':
                     print("\n📄 **AUTONOMOUS AGENT RESPONSE:**")
                     print("-" * 40)
                     print(result['final_report'])

                     if 'saved_files' in result:
                        print(f"\n💾 Full report saved to: {result['saved_files']['report']}")
                else:
                    print(f"\n❌ Processing failed: {result.get('error', 'Unknown error')}")

            except KeyboardInterrupt:
                 print("\n👋 Goodbye!")
                 break
            except Exception as e:
                logger.error(f"Interactive mode error: {e}")
                print(f"\n❌ Error: {e}")

    def show_help(self):
        """Show help information"""

        print("""
📚 Available Commands:
• Just type your question naturally
• 'status' - Show system status
• 'help' - Show this help
• 'quit' or 'exit' - Stop the program

🎯 Example Questions:
• "Research the latest trends in renewable energy"
• "Analyze the competitive landscape for electric vehicles"
• "What are the key developments in AI safety?"
• "Create a market analysis for smart home devices"

💡 The system will automatically:
• Search your knowledge base for relevant documents
• Find current information from the web
• Perform analysis and calculations
• Generate a comprehensive report with citations
        """)

    def show_status(self):
         """Show system status"""
         if not self.execution_manager:
             print("❌ System not initialized")
             return
         
         status=self.execution_manager.get_execution_status()
         print(f"""📊 System Status:
• Agents Available: {len(self.agents)}
• Active Workflows: {status.get('active_workflows', 0)}
• Completed Workflows: {status.get('completed_workflows', 0)}
• Success Rate: {status.get('success_rate', 0):.1f}%
• Average Execution Time: {status.get('average_execution_time', 0):.1f}s

🤖 Available Agents: {', '.join(self.agents.keys())}
        """)
         
def main():
    """Maain CLI entry POint"""
    print("🚀 Starting Autonomous Knowledge-Worker Agent System")

    agent_system=AutonomousKnowledgeWorker()

    if not agent_system.initialize_system():
         print("❌ System initialization failed. Please check the logs and try again.")
         sys.exit(1)

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result=agent_system.rn_query(query)

        if result['status'] == 'completed':
            print("\n📄 **RESULT:**")
            print(result['final_report'])
        else:
            print(f"❌ Failed: {result.get('error')}")
    else:
        
        agent_system.interactive_mode()

if __name__ == "__main__":
    main()


             
             





        



             


                 
                 
                 


    

                 


    

