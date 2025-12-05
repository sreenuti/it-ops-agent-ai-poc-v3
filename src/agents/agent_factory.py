"""
Agent factory for creating framework-specific agents
"""
from typing import Optional, Literal

from src.agents.base_agent import BaseAgent
from src.agents.adapters.langchain_adapter import LangChainAdapter
from src.agents.adapters.langgraph_adapter import LangGraphAdapter
from src.agents.adapters.crewai_adapter import CrewAIAdapter
from src.agents.adapters.autogen_adapter import AutoGenAdapter
from src.config.settings import get_settings
from src.vector_db.instruction_store import InstructionStore
from src.script_executor.aws_executor import AWSExecutor
from src.script_executor.system_executor import SystemExecutor


class AgentFactory:
    """Factory for creating agent instances based on framework configuration"""
    
    @staticmethod
    def create_agent(
        framework: Optional[Literal["langchain", "langgraph", "crewai", "autogen"]] = None,
        instruction_store: Optional[InstructionStore] = None,
        aws_executor: Optional[AWSExecutor] = None,
        system_executor: Optional[SystemExecutor] = None
    ) -> BaseAgent:
        """
        Create an agent instance based on framework
        
        Args:
            framework: Framework name (defaults to config)
            instruction_store: Optional instruction store instance
            aws_executor: Optional AWS executor instance
            system_executor: Optional system executor instance
            
        Returns:
            BaseAgent instance
            
        Raises:
            ValueError: If framework is not supported
        """
        settings = get_settings()
        framework = framework or settings.agent_framework
        
        if framework == "langchain":
            return LangChainAdapter(
                instruction_store=instruction_store,
                aws_executor=aws_executor,
                system_executor=system_executor
            )
        elif framework == "langgraph":
            return LangGraphAdapter(
                instruction_store=instruction_store,
                aws_executor=aws_executor,
                system_executor=system_executor
            )
        elif framework == "crewai":
            return CrewAIAdapter(
                instruction_store=instruction_store,
                aws_executor=aws_executor,
                system_executor=system_executor
            )
        elif framework == "autogen":
            return AutoGenAdapter(
                instruction_store=instruction_store,
                aws_executor=aws_executor,
                system_executor=system_executor
            )
        else:
            raise ValueError(
                f"Unsupported framework: {framework}. "
                f"Supported frameworks: langchain, langgraph, crewai, autogen"
            )
    
    @staticmethod
    def get_available_frameworks() -> list[str]:
        """
        Get list of available frameworks
        
        Returns:
            List of framework names
        """
        return ["langchain", "langgraph", "crewai", "autogen"]
    
    @staticmethod
    def is_framework_available(framework: str) -> bool:
        """
        Check if a framework is available (installed)
        
        Args:
            framework: Framework name
            
        Returns:
            True if framework is available, False otherwise
        """
        if framework == "langchain":
            try:
                import langchain
                return True
            except ImportError:
                return False
        elif framework == "langgraph":
            try:
                import langgraph
                return True
            except ImportError:
                return False
        elif framework == "crewai":
            try:
                import crewai
                return True
            except ImportError:
                return False
        elif framework == "autogen":
            try:
                import autogen
                return True
            except ImportError:
                return False
        return False

