"""
Task decomposer for breaking complex tasks into subtasks
"""
from typing import Dict, Any, Optional, List
import json
import re

from src.config.settings import get_settings
from src.vector_db.instruction_store import InstructionStore


class TaskDecomposer:
    """Decompose complex IT ops tasks into manageable subtasks"""
    
    def __init__(
        self,
        instruction_store: Optional[InstructionStore] = None,
        llm=None
    ):
        """
        Initialize task decomposer
        
        Args:
            instruction_store: Instruction store instance
            llm: Optional LLM instance (for decomposition)
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
    
    def decompose(
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
        if self.llm is None:
            # Fallback: return single subtask
            return [{
                "subtask": task,
                "task_type": "general",
                "dependencies": [],
                "priority": 5
            }]
        
        # Use LLM to decompose task
        decomposition_prompt = f"""Break down the following IT ops task into logical subtasks.

Task: {task}
{f"Context: {context}" if context else ""}

For each subtask, provide:
- A clear description
- The task type (e.g., password_reset, vpn_troubleshooting, account_locked, etc.)
- Any dependencies on other subtasks (by subtask index)
- Priority (1-10, 10 is highest)

Return a JSON array of subtasks with this structure:
[
    {{
        "subtask": "description",
        "task_type": "task_type",
        "dependencies": [],
        "priority": 5
    }}
]

Only return the JSON array, no additional text."""
        
        try:
            response = self.llm.invoke(decomposition_prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                subtasks = json.loads(json_match.group())
                # Add IDs to subtasks
                for i, subtask in enumerate(subtasks):
                    subtask["id"] = str(i)
                return subtasks
            else:
                # Fallback: create single subtask
                return [{
                    "id": "0",
                    "subtask": task,
                    "task_type": "general",
                    "dependencies": [],
                    "priority": 5
                }]
        except Exception as e:
            # Fallback: return single subtask
            return [{
                "id": "0",
                "subtask": task,
                "task_type": "general",
                "dependencies": [],
                "priority": 5
            }]
    
    def get_instructions_for_subtasks(
        self,
        subtasks: List[Dict[str, Any]],
        n_results_per_subtask: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve instructions for each subtask
        
        Args:
            subtasks: List of subtask dicts
            n_results_per_subtask: Number of instructions to retrieve per subtask
            
        Returns:
            Dict mapping subtask ID to list of instructions
        """
        instructions_map = {}
        
        for subtask in subtasks:
            subtask_id = subtask.get("id", str(subtasks.index(subtask)))
            task_type = subtask.get("task_type", "general")
            subtask_desc = subtask.get("subtask", "")
            
            # Retrieve instructions for this subtask
            instructions = self.instruction_store.retrieve_instructions(
                query=subtask_desc,
                task_type=task_type if task_type != "general" else None,
                n_results=n_results_per_subtask
            )
            
            instructions_map[subtask_id] = instructions
        
        return instructions_map
    
    def create_execution_plan(
        self,
        subtasks: List[Dict[str, Any]],
        instructions_map: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Create an execution plan from subtasks and their instructions
        
        Args:
            subtasks: List of subtask dicts
            instructions_map: Dict mapping subtask ID to instructions
            
        Returns:
            List of execution plan steps with:
                - step_id: str
                - subtask: Dict
                - instructions: List[Dict]
                - order: int (based on dependencies and priority)
        """
        # Sort subtasks by priority (highest first) and resolve dependencies
        sorted_subtasks = sorted(
            subtasks,
            key=lambda x: (x.get("priority", 5), len(x.get("dependencies", []))),
            reverse=True
        )
        
        execution_plan = []
        for i, subtask in enumerate(sorted_subtasks):
            subtask_id = subtask.get("id", str(i))
            instructions = instructions_map.get(subtask_id, [])
            
            execution_plan.append({
                "step_id": subtask_id,
                "order": i + 1,
                "subtask": subtask,
                "instructions": instructions
            })
        
        return execution_plan

