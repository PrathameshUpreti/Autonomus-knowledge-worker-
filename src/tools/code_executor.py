"""
Code Executor Tool- Safely runs Python code for calculations and basic analysis.

"""

import os
import sys,io
import ast
from typing import Dict, Optional
import traceback
from .Base_tool import BaseTool
import time
import contextlib

class CodeExecutorTool(BaseTool):
    """
    Safe Python code executor.
    Can run calculations and basic data analysis code safely.
    """
    def __init__(self):
        super().__init__(
            name="CodeExecutorTool",
            description="Safely execute Python code for calculations and analysis"

        )
        self.safe_mode = True
        self.max_execution_time = 5  # seconds
        self.max_output_length = 1000  # characters
        self.allowed_modules = ["math", "statistics", "datetime", "json", "re"]
        
        # Keep track of what we've run
        self.execution_history = []

    def execute(self, code:str,context:Optional[Dict]=None)->Dict:
        """
        Run Python code safely and return the results.
        
        Args:
            code: Python code to run (e.g., "2 + 2" or "import math; math.sqrt(16)")
            context: Optional variables to make available (e.g., {"x": 5, "y": 10})
            
        Returns:
            Dictionary with results, output, errors, and success status
        """
        if not code or not code.strip():
            return{
                "error":"No] code provided ",
                "sucess":False
            }       
        
        if self.safe_mode and not self.is_safe_code(code):
            return{"error": "Code contains unsafe operations",
                    "success": False
                }
        
        try:
            print(f"🐍 Executing code: {code[:50]}{'...' if len(code) > 50 else ''}")

            execution_global=self.create_self_environment(context)

            # Capture any output & error
            output_capture = io.StringIO()
            error_capture = io.StringIO()

            result = {
                "code": code,
                "success": False,
                "result": None,
                "output": "",
                "error": "",
                "execution_time": 0
            }

            start_time=time.time()
            try:
                # Redirect print statements to capture them
                with contextlib.redirect_stdout(output_capture), \
                     contextlib.redirect_stderr(error_capture):
                    
                    # Try to run as expression first (like "2 + 2")
                    try:
                        # Parse as expression
                        parsed = ast.parse(code, mode='eval')
                        result["result"] = eval(compile(parsed, '<string>', 'eval'), execution_global)
                        result["success"] = True
                    except SyntaxError:
                        # If that fails, try as statement(s) (like "x = 5; print(x)")
                        parsed = ast.parse(code, mode='exec')
                        exec(compile(parsed, '<string>', 'exec'), execution_global)
                        result["success"] = True
                        
                        # Check if there's a 'result' variable
                        if 'result' in execution_global:
                            result["result"] = execution_global['result']
                
                # Get execution time
                result["execution_time"] = round(time.time() - start_time, 3)

                result["output"] = output_capture.getvalue()
                
                # Get any errors
                if error_capture.getvalue():
                    result["error"] = error_capture.getvalue()
                
            except Exception as e:
                result["error"] = str(e)
                result["execution_time"] = round(time.time() - start_time, 3)
            
            # Limit output length to prevent huge outputs
            if len(result["output"]) > self.max_output_length:
                result["output"] = result["output"][:self.max_output_length] + "...[output truncated]"
            
            # Store in history
            self.execution_history.append(result.copy())
            
            # Show result
            if result["success"]:
                print(f"✅ Code executed successfully")
                if result["result"] is not None:
                    print(f"📊 Result: {result['result']}")
            else:
                print(f"❌ Code execution failed: {result['error']}")
            
            return result
        except Exception as e:
            print(f"❌ Execution error: {e}")
            return {
                "code": code,
                "success": False,
                "error": str(e),
                "result": None,
                "output": "",
                "execution_time": 0
            }
    
    def if_safe_code(self,code:str) ->bool:
        """Check if code is safe to run"""

        daangerous_pattern=[
            "import os", "import sys", "import subprocess", "import shutil",
            "open(", "file(", "exec(", "eval(", "__import__",
            "globals()", "locals()", "vars()", "dir()",
            "getattr", "setattr", "delattr",
            "input(", "raw_input(", "exit(", "quit()",
            "while True:", "for i in range(99999"

        ]
        code_lower=code.lower()
        for pattern in daangerous_pattern:
            if pattern in code_lower:
                print(f"⚠️ Unsafe code detected: {pattern}")
                return False
        
        try:
            tree=ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if hasattr(node, 'names'):
                        for alias in node.names:
                            module_name = alias.name
                            if module_name not in self.allowed_modules:
                                print(f"⚠️ Module not allowed: {module_name}")
                                return False
        except SyntaxError:
            return False
        
        return True
    
    def _create_safe_environment(self, context: Optional[Dict] = None) -> Dict:
        """Create a safe environment for code execution"""
        # Only allow safe built-in functions
        safe_builtins = {
            'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter',
            'float', 'int', 'len', 'list', 'max', 'min', 'range', 'round',
            'sorted', 'str', 'sum', 'tuple', 'zip', 'print', 'type'
        }
        
        # Create safe globals
        safe_globals = {
            '__builtins__': {name: getattr(__builtins__, name) for name in safe_builtins}
        }
        
        # Add allowed modules
        for module_name in self.allowed_modules:
            try:
                safe_globals[module_name] = __import__(module_name)
            except ImportError:
                print(f"⚠️ Module {module_name} not available")
        
        # Add any context variables
        if context:
            safe_globals.update(context)
        
        return safe_globals
    
    def calculate(self, expression: str, variables: Optional[Dict] = None) -> Dict:
        """
        Simple calculator for math expressions.
        
        Args:
            expression: Math expression like "2 + 2" or "math.sqrt(x)"
            variables: Optional variables like {"x": 16, "y": 4}
            
        Returns:
            Dictionary with calculation result
        """
        # Build the code to run
        if variables:
            # Add variable assignments
            assignments = []
            for key, value in variables.items():
                if isinstance(value, str):
                    assignments.append(f"{key} = '{value}'")
                else:
                    assignments.append(f"{key} = {value}")
            
            code = "\n".join(assignments) + f"\nresult = {expression}"
        else:
            code = f"result = {expression}"
        
        # Run the calculation
        result = self.execute(code)
        
        if result["success"]:
            return {
                "expression": expression,
                "result": result["result"],
                "variables": variables or {},
                "success": True
            }
        else:
            return {
                "expression": expression,
                "error": result["error"],
                "success": False
            }
    
    def get_execution_history(self) -> list:
        """Get history of all code that was run"""
        return self.execution_history.copy()
    
    def clear_history(self):
        """Clear the execution history"""
        self.execution_history.clear()
        print("🗑️ Execution history cleared")
    
    def run_simple_analysis(self, data: list, operation: str = "stats") -> Dict:
        """
        Run simple data analysis on a list of numbers.
        
        Args:
            data: List of numbers like [1, 2, 3, 4, 5]
            operation: Type of analysis - "stats", "sum", "average", etc.
            
        Returns:
            Dictionary with analysis results
        """
        if not data or not all(isinstance(x, (int, float)) for x in data):
            return {"error": "Need a list of numbers", "success": False}
        
        if operation == "stats":
            code = f"""
import statistics
data = {data}
result = {{
    'count': len(data),
    'sum': sum(data),
    'average': statistics.mean(data),
    'median': statistics.median(data),
    'min': min(data),
    'max': max(data)
}}
"""
        elif operation == "sum":
            code = f"result = sum({data})"
        elif operation == "average":
            code = f"import statistics; result = statistics.mean({data})"
        else:
            return {"error": f"Unknown operation: {operation}", "success": False}
        
        return self.execute(code)

def create_code_executor() -> CodeExecutorTool:
    """Create a code executor tool"""
    return CodeExecutorTool()



            