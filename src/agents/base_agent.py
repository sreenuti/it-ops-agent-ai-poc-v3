"""
Base agent interface for framework-agnostic agent implementations
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseAgent(ABC):
    """Abstract base class for all agent implementations"""
    
    @abstractmethod
    def decompose_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Break down a complex task into subtasks
        
        Args:
            task: The task description
            context: Optional context information
            
        Returns:
            List of subtask dicts, each with:
                - subtask: str - Subtask description
                - task_type: str - Type of subtask
                - dependencies: List[str] - IDs of subtasks this depends on
                - priority: int - Priority level (1-10, 10 is highest)
        """
        pass
    
    @abstractmethod
    def retrieve_instructions(
        self,
        query: str,
        task_type: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant instructions from vector database
        
        Args:
            query: Search query
            task_type: Optional filter by task type
            n_results: Number of results to return
            
        Returns:
            List of instruction dicts with keys:
                - id: Instruction ID
                - text: Instruction text
                - metadata: Instruction metadata
                - distance: Similarity distance
        """
        pass
    
    @abstractmethod
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
            dry_run: If True, don't execute commands, only show what would be done
            
        Returns:
            Execution result dict with keys:
                - response: str - Agent's response
                - success: bool - Whether the task was successful
                - steps: List[Dict] - List of steps taken
                - error: Optional[str] - Error message if failed
        """
        pass
    
    @abstractmethod
    def process_query(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user query (natural language)
        
        Args:
            query: User's query/task request
            chat_history: Optional conversation history with format:
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            dry_run: If True, don't execute commands
            
        Returns:
            Dict with keys:
                - response: str - Agent's response
                - success: bool - Whether the task was successful
                - steps: List[Dict] - List of steps taken
                - error: Optional[str] - Error message if failed
        """
        pass
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """
        Get the name of the framework this agent uses
        
        Returns:
            Framework name (e.g., "langchain", "langgraph", "crewai", "autogen")
        """
        pass

