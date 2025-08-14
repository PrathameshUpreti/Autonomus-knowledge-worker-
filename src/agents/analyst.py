"""
Analyst Agent - Data analysis and calculations
"""
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .base_agent import BaseAgent
from src.tools import get_tool
import logging

logger = logging.getLogger(__name__)

class AnalystAgent(BaseAgent):
    """
    Analyst agent specialized in data analysis and calculations
    """
    def __init__(self):
        system_message="""
You are the Analyst Agent, specialized in data analysis and technical evaluation.

YOUR ANALYTICAL MISSION:
1. **Data Analysis**: Process and analyze numerical data
2. **Statistical Analysis**: Perform statistical calculations and interpretations
3. **Code Execution**: Run Python code for calculations and analysis
4. **Trend Analysis**: Identify patterns and trends in data
5. **Technical Evaluation**: Assess technical specifications and metrics

ANALYTICAL APPROACH:
- Use execute_code for complex calculations
- Use calculate for simple mathematical expressions
- Provide clear explanations of analytical methods
- Show calculations and reasoning
- Present findings with data-driven insights
"""
        super().__init__(
            name="analyst",
            description="Data Analysis and Technical Evaluation Specialist",
            system_message=system_message
         )
    
    def register_tools(self):
        """register analyst tools"""
        self.tool_objects = {
        "code_executor": get_tool("code_executor")  # ✅ Correct registration
    }
        async def execute_code(code: str) -> str:
            """Execute the python code for analysis"""
            try:
                tool=self.tool_objects["code_executor"]

                if not tool:
                    return "❌ Code executor tool not available"
                
                result=tool.execute(code)

                if isinstance(result, dict) and result.get("success", False):
                    output_parts=[]
                    if result.get("result") is not None:
                        output_parts.append(f"**Result:** {result['result']}")
                    if result.get("output"):
                        output_parts.append(f"**Output:**\n{result['output']}")
                    return "\n\n".join(output_parts) if output_parts else "✅ Code executed successfully"
                else:
                    return f"❌ Execution error: {result.get('error', 'Unknown error')}"
                
            except Exception as e:
                return f"❌ Code execution failed: {e}"
            
        async def  calculate(expression:str,variables:str="")->str:
            """Calculate mathematical expression"""
            tool= self.tool_objects["code_executor"]
            #parse varible if proved as "x=5,y=10"
            var_dict={ }

            if variables:
                for var_assign in variables.split(","):
                    if "=" in var_assign:
                        key,value= var_assign.strip().split("=",1)
                        try:
                            var_dict[key.strip()] = float(value.strip())
                        except ValueError:
                            var_dict[key.strip()] = value.strip()

                    result=tool.calculate(expression,var_dict if var_dict else None)

                    if result["sucess"]:
                        return f"Calculation:{expression} = {result['result']}"
                    else:
                        return f"Calculation error: {result.get('error', 'Unknown error')}"
                    
        self.add_tool_function("execute_code",execute_code,"Execute the python code for analysis")
        self.add_tool_function("calculate",calculate,"Perform mathematical calculations")

    def create_autogen_agent(self):
        """Create AutoGen agent with analysis tools"""
        try:
            model_client = OpenAIChatCompletionClient(
                model=self.model_confrig["model"],
                api_key=self.model_confrig["api_key"]
            )
            
            function_tools = []
            for tool_info in self.tools:
                function_tool = FunctionTool(
                    tool_info["function"],
                    description=tool_info["description"]
                )
                function_tools.append(function_tool)
            
            agent = AssistantAgent(
                name=self.name,
                model_client=model_client,
                system_message=self.get_full_system_message(),
                tools=function_tools
            )
            
            logger.info(f"✅ Created analyst with {len(function_tools)} tools")
            return agent
        
        except Exception as e:
            logger.error(f"❌ Error creating {self.name}: {e}")
            raise

def create_analyst() -> AnalystAgent:
    """Factory function to create analyst agent"""
    return AnalystAgent()
           
            
            



                            


            

