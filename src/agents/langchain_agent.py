"""
LangChain-based agent for IT ops tasks
"""
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_tools_agent

from src.config.settings import get_settings
from src.vector_db.instruction_store import InstructionStore
from src.script_executor.aws_executor import AWSExecutor
from src.script_executor.system_executor import SystemExecutor


class LangChainAgent:
    """Basic LangChain agent for IT ops tasks"""
    
    def __init__(
        self,
        instruction_store: Optional[InstructionStore] = None,
        aws_executor: Optional[AWSExecutor] = None,
        system_executor: Optional[SystemExecutor] = None,
        llm: Optional[ChatOpenAI] = None
    ):
        """
        Initialize LangChain agent
        
        Args:
            instruction_store: Instruction store instance
            aws_executor: AWS executor instance
            system_executor: System executor instance
            llm: LangChain LLM instance
        """
        settings = get_settings()
        
        self.instruction_store = instruction_store or InstructionStore()
        self.aws_executor = aws_executor or AWSExecutor()
        self.system_executor = system_executor or SystemExecutor()
        
        # Initialize LLM
        if llm is None:
            self.llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=0,
                openai_api_key=settings.openai_api_key
            )
        else:
            self.llm = llm
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=settings.debug,
            handle_parsing_errors=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        
        def retrieve_instructions(query: str) -> str:
            """Retrieve relevant IT ops instructions from the knowledge base.
            
            Args:
                query: The task or question to search for instructions
                
            Returns:
                Relevant instructions as a formatted string
            """
            instructions = self.instruction_store.retrieve_instructions(
                query=query,
                n_results=5
            )
            
            if not instructions:
                return "No relevant instructions found."
            
            formatted = "Relevant Instructions:\n\n"
            for i, inst in enumerate(instructions, 1):
                formatted += f"{i}. Task Type: {inst['metadata'].get('task_type', 'unknown')}\n"
                formatted += f"   Instruction: {inst['text']}\n"
                if inst.get('distance'):
                    formatted += f"   Relevance: {1 - inst['distance']:.2f}\n"
                formatted += "\n"
            
            return formatted
        
        def execute_aws_command(command: str) -> str:
            """Execute an AWS CLI command.
            
            Args:
                command: The AWS CLI command to execute (e.g., "aws iam update-login-profile --username john --password NewPass123")
                
            Returns:
                Command execution result
            """
            result = self.aws_executor.execute(command)
            
            if result["success"]:
                output = result.get("output", "")
                if isinstance(output, dict):
                    output = str(output)
                return f"Success: {output}"
            else:
                error = result.get("error", "Unknown error")
                return f"Error: {error}"
        
        def execute_system_command(command: str) -> str:
            """Execute a system command (PowerShell on Windows, Bash on Linux).
            
            Args:
                command: The system command to execute
                
            Returns:
                Command execution result
            """
            result = self.system_executor.execute(command)
            
            if result["success"]:
                return f"Success: {result.get('output', '')}"
            else:
                error = result.get("error", "Unknown error")
                return f"Error: {error}"
        
        return [
            Tool(
                name="retrieve_instructions",
                func=retrieve_instructions,
                description="Retrieve relevant IT ops instructions from the knowledge base. Use this to find procedures for tasks like password resets, VPN troubleshooting, etc."
            ),
            Tool(
                name="execute_aws_command",
                func=execute_aws_command,
                description="Execute AWS CLI commands. Use this for AWS-related tasks like IAM password resets, EC2 management, etc. The command should be a complete AWS CLI command."
            ),
            Tool(
                name="execute_system_command",
                func=execute_system_command,
                description="Execute system commands (PowerShell on Windows, Bash on Linux). Use this for local system tasks like checking services, running diagnostics, etc."
            )
        ]
    
    def _create_agent(self):
        """Create the LangChain agent"""
        
        system_prompt = """You are an IT Operations assistant that helps with common IT tasks.

Your workflow:
1. When given a task, first use retrieve_instructions to find relevant procedures
2. Based on the instructions, determine what commands need to be executed
3. Use execute_aws_command for AWS-related tasks (IAM, EC2, etc.)
4. Use execute_system_command for local system tasks (Windows/Linux commands)
5. Provide clear feedback about what was done

Important:
- Always retrieve instructions first to understand the proper procedure
- Validate commands before executing them
- Provide clear, user-friendly responses
- If a task requires multiple steps, break it down and execute them sequentially
- Always explain what you're doing and why

Task types you handle:
- Password resets (AWS IAM, Active Directory, local accounts)
- VPN troubleshooting
- Outlook sync issues
- Account access requests
- System diagnostics
- And other common IT ops tasks"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return agent
    
    def process_query(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user query
        
        Args:
            query: User's query/task request
            chat_history: Optional conversation history
            dry_run: If True, don't execute commands, just show what would be done
            
        Returns:
            Dict with keys:
                - response: Agent's response
                - success: Whether the task was successful
                - steps: List of steps taken
                - error: Optional error message
        """
        try:
            # Convert chat history to LangChain messages
            messages = []
            if chat_history:
                for msg in chat_history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg.get("content", "")))
            
            # Add dry run context if needed
            if dry_run:
                query = f"[DRY RUN MODE] {query} - Do not execute commands, only show what would be done."
            
            # Execute agent
            result = self.agent_executor.invoke({
                "input": query,
                "chat_history": messages
            })
            
            response_text = result.get("output", "")
            
            # Determine success based on response content
            success = "error" not in response_text.lower() and "failed" not in response_text.lower()
            
            return {
                "response": response_text,
                "success": success,
                "steps": [],  # Could be enhanced to track steps
                "error": None
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "success": False,
                "steps": [],
                "error": str(e)
            }
    
    def execute_task(
        self,
        task_type: str,
        task_params: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a specific task type with parameters
        
        Args:
            task_type: Type of task (e.g., "password_reset", "vpn_troubleshooting")
            task_params: Task-specific parameters
            dry_run: If True, don't execute commands
            
        Returns:
            Execution result dict
        """
        # Build query from task type and params
        query = f"Task: {task_type}"
        if task_params:
            params_str = ", ".join([f"{k}={v}" for k, v in task_params.items()])
            query += f" with parameters: {params_str}"
        
        return self.process_query(query, dry_run=dry_run)

