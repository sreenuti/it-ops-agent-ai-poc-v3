"""
Script generator for creating executable scripts from instructions
"""
from typing import Dict, Any, Optional, List
import re

from src.config.settings import get_settings
from src.vector_db.instruction_store import InstructionStore


class ScriptGenerator:
    """Generate executable scripts from instructions and context"""
    
    def __init__(
        self,
        instruction_store: Optional[InstructionStore] = None,
        llm=None
    ):
        """
        Initialize script generator
        
        Args:
            instruction_store: Instruction store instance
            llm: Optional LLM instance (for script generation)
        """
        settings = get_settings()
        self.instruction_store = instruction_store or InstructionStore()
        self.llm = llm
        
        # Initialize LLM if not provided
        if self.llm is None:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model=settings.openai_model,
                    temperature=0,
                    openai_api_key=settings.openai_api_key
                )
            except ImportError:
                # LangChain not available, will use fallback
                self.llm = None
    
    def generate_script(
        self,
        instructions: List[Dict[str, Any]],
        task_params: Dict[str, Any],
        executor_type: str = "system"
    ) -> Dict[str, Any]:
        """
        Generate a script from instructions and parameters
        
        Args:
            instructions: List of instruction dicts
            task_params: Task parameters (e.g., username, password, etc.)
            executor_type: Type of executor ("aws", "system", "powershell", "bash")
            
        Returns:
            Dict with keys:
                - script: str - Generated script
                - commands: List[str] - List of commands
                - validation_errors: List[str] - Any validation errors
                - executor_type: str - Executor type to use
        """
        if not instructions:
            return {
                "script": "",
                "commands": [],
                "validation_errors": ["No instructions provided"],
                "executor_type": executor_type
            }
        
        # Combine instruction texts
        instruction_text = "\n\n".join([
            f"Instruction {i+1}:\n{inst.get('text', '')}"
            for i, inst in enumerate(instructions)
        ])
        
        # Determine script format based on executor type
        if executor_type == "aws":
            script_format = "AWS CLI command"
            example = "aws iam update-login-profile --username USERNAME --password PASSWORD"
        elif executor_type in ["powershell", "system"]:
            script_format = "PowerShell command"
            example = "Get-ADUser -Identity USERNAME"
        elif executor_type == "bash":
            script_format = "Bash command"
            example = "sudo passwd USERNAME"
        else:
            script_format = "System command"
            example = "command with parameters"
        
        # Build generation prompt
        params_str = ", ".join([f"{k}={v}" for k, v in task_params.items()])
        
        generation_prompt = f"""Generate a {script_format} based on the following instructions and parameters.

Instructions:
{instruction_text}

Parameters:
{params_str}

Example format: {example}

Requirements:
1. Replace placeholders (USERNAME, PASSWORD, etc.) with actual parameter values
2. Generate a valid, executable command
3. Ensure proper escaping of special characters
4. Follow security best practices (e.g., don't echo passwords)

Return only the command/script, no additional explanation."""
        
        try:
            if self.llm:
                response = self.llm.invoke(generation_prompt)
                script = response.content if hasattr(response, 'content') else str(response)
                script = script.strip()
            else:
                # Fallback: simple template replacement
                script = self._simple_template_replace(instruction_text, task_params, executor_type)
            
            # Validate script
            validation_errors = self.validate_script(script, executor_type, task_params)
            
            # Extract individual commands if multi-step
            commands = self._extract_commands(script, executor_type)
            
            return {
                "script": script,
                "commands": commands,
                "validation_errors": validation_errors,
                "executor_type": executor_type
            }
        except Exception as e:
            return {
                "script": "",
                "commands": [],
                "validation_errors": [f"Error generating script: {str(e)}"],
                "executor_type": executor_type
            }
    
    def _simple_template_replace(
        self,
        instruction_text: str,
        task_params: Dict[str, Any],
        executor_type: str
    ) -> str:
        """Simple template replacement fallback"""
        # Extract common patterns from instructions
        script = instruction_text
        
        # Replace common placeholders
        for key, value in task_params.items():
            placeholder = key.upper()
            script = script.replace(f"{{{placeholder}}}", str(value))
            script = script.replace(f"${placeholder}", str(value))
            script = script.replace(f"%{placeholder}%", str(value))
        
        # Extract first command-like line
        lines = script.split("\n")
        for line in lines:
            if any(cmd in line.lower() for cmd in ["aws ", "get-", "set-", "sudo ", "command"]):
                return line.strip()
        
        return script.split("\n")[0].strip()
    
    def _extract_commands(
        self,
        script: str,
        executor_type: str
    ) -> List[str]:
        """Extract individual commands from a script"""
        if executor_type == "aws":
            # AWS commands are typically single-line
            return [script]
        elif executor_type in ["powershell", "system"]:
            # PowerShell commands separated by semicolons or newlines
            commands = re.split(r'[;\n]', script)
            return [cmd.strip() for cmd in commands if cmd.strip()]
        elif executor_type == "bash":
            # Bash commands separated by semicolons or && or newlines
            commands = re.split(r'[;\n&]', script)
            return [cmd.strip() for cmd in commands if cmd.strip()]
        else:
            return [script]
    
    def validate_script(
        self,
        script: str,
        executor_type: str,
        task_params: Dict[str, Any]
    ) -> List[str]:
        """
        Validate a generated script
        
        Args:
            script: Generated script
            executor_type: Type of executor
            task_params: Task parameters
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check script is not empty
        if not script or not script.strip():
            errors.append("Script is empty")
            return errors
        
        # Check for dangerous commands (basic security check)
        dangerous_patterns = [
            r'rm\s+-rf',
            r'del\s+/f\s+/s',
            r'format\s+',
            r'drop\s+database',
            r'shutdown',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, script, re.IGNORECASE):
                errors.append(f"Potentially dangerous command detected: {pattern}")
        
        # Check for required parameters
        if executor_type == "aws" and "aws " not in script.lower():
            errors.append("AWS script should start with 'aws' command")
        
        # Check for placeholder values that weren't replaced
        placeholders = re.findall(r'\{(\w+)\}|\$(\w+)|\%(\w+)\%', script)
        if placeholders:
            errors.append(f"Unreplaced placeholders found: {placeholders}")
        
        return errors
    
    def generate_multi_step_script(
        self,
        execution_plan: List[Dict[str, Any]],
        task_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a multi-step script from an execution plan
        
        Args:
            execution_plan: List of execution plan steps
            task_params: Task parameters
            
        Returns:
            Dict with multi-step script information
        """
        scripts = []
        all_commands = []
        all_errors = []
        
        for step in execution_plan:
            subtask = step.get("subtask", {})
            instructions = step.get("instructions", [])
            
            # Determine executor type from subtask
            task_type = subtask.get("task_type", "general")
            executor_type = self._determine_executor_type(task_type, instructions)
            
            # Generate script for this step
            step_result = self.generate_script(
                instructions=instructions,
                task_params=task_params,
                executor_type=executor_type
            )
            
            scripts.append({
                "step_id": step.get("step_id"),
                "order": step.get("order"),
                "subtask": subtask.get("subtask"),
                **step_result
            })
            
            all_commands.extend(step_result.get("commands", []))
            all_errors.extend(step_result.get("validation_errors", []))
        
        return {
            "steps": scripts,
            "all_commands": all_commands,
            "validation_errors": all_errors,
            "total_steps": len(scripts)
        }
    
    def _determine_executor_type(
        self,
        task_type: str,
        instructions: List[Dict[str, Any]]
    ) -> str:
        """Determine executor type from task type and instructions"""
        # Check task type
        if "aws" in task_type.lower() or "iam" in task_type.lower():
            return "aws"
        
        # Check instruction content
        instruction_text = " ".join([inst.get("text", "") for inst in instructions])
        if "aws " in instruction_text.lower():
            return "aws"
        elif "powershell" in instruction_text.lower() or "get-ad" in instruction_text.lower():
            return "powershell"
        elif "bash" in instruction_text.lower() or "sudo " in instruction_text.lower():
            return "bash"
        
        # Default based on settings
        settings = get_settings()
        if settings.execution_environment == "windows":
            return "powershell"
        elif settings.execution_environment == "linux":
            return "bash"
        else:
            return "system"

