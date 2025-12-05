"""
Instruction store for managing IT ops instructions in Chroma
"""
from typing import List, Dict, Any, Optional
from uuid import uuid4
from src.vector_db.chroma_client import ChromaClient
from src.config.settings import get_settings


class InstructionStore:
    """Store and retrieve IT ops instructions from vector database"""
    
    def __init__(self, chroma_client: Optional[ChromaClient] = None):
        """
        Initialize instruction store
        
        Args:
            chroma_client: Optional Chroma client instance
        """
        self.chroma_client = chroma_client or ChromaClient()
        self.collection = self.chroma_client.get_collection()
    
    def add_instruction(
        self,
        task_type: str,
        instruction_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an instruction to the store
        
        Args:
            task_type: Type of task (e.g., "password_reset", "vpn_troubleshooting")
            instruction_text: The instruction/procedure text
            metadata: Additional metadata (e.g., platform, complexity)
            
        Returns:
            Instruction ID
        """
        instruction_id = str(uuid4())
        
        # Prepare metadata
        instruction_metadata = {
            "task_type": task_type,
            **(metadata or {})
        }
        
        # Add to collection
        self.collection.add(
            ids=[instruction_id],
            documents=[instruction_text],
            metadatas=[instruction_metadata]
        )
        
        return instruction_id
    
    def add_instructions_batch(
        self,
        instructions: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add multiple instructions at once
        
        Args:
            instructions: List of instruction dicts with keys:
                - task_type: Task type
                - instruction_text: Instruction text
                - metadata: Optional metadata dict
                
        Returns:
            List of instruction IDs
        """
        ids = []
        documents = []
        metadatas = []
        
        for instruction in instructions:
            instruction_id = str(uuid4())
            ids.append(instruction_id)
            documents.append(instruction["instruction_text"])
            
            metadata = {
                "task_type": instruction["task_type"],
                **(instruction.get("metadata", {}))
            }
            metadatas.append(metadata)
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        return ids
    
    def retrieve_instructions(
        self,
        query: str,
        task_type: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant instructions based on query
        
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
        # Build where clause if task_type specified
        where_clause = None
        if task_type:
            where_clause = {"task_type": task_type}
        
        # Query collection
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        # Format results
        instructions = []
        if results["documents"] and len(results["documents"][0]) > 0:
            for i in range(len(results["documents"][0])):
                instructions.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results["distances"] else None
                })
        
        return instructions
    
    def get_instruction_by_id(self, instruction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get instruction by ID
        
        Args:
            instruction_id: Instruction ID
            
        Returns:
            Instruction dict or None if not found
        """
        results = self.collection.get(ids=[instruction_id])
        
        if results["ids"] and len(results["ids"]) > 0:
            return {
                "id": results["ids"][0],
                "text": results["documents"][0],
                "metadata": results["metadatas"][0]
            }
        
        return None
    
    def update_instruction(
        self,
        instruction_id: str,
        instruction_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing instruction
        
        Args:
            instruction_id: Instruction ID
            instruction_text: New instruction text (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if updated, False if not found
        """
        existing = self.get_instruction_by_id(instruction_id)
        if not existing:
            return False
        
        # Prepare update data
        update_data = {}
        if instruction_text:
            update_data["documents"] = [instruction_text]
        if metadata:
            new_metadata = {**existing["metadata"], **metadata}
            update_data["metadatas"] = [new_metadata]
        
        if update_data:
            update_data["ids"] = [instruction_id]
            self.collection.update(**update_data)
        
        return True
    
    def delete_instruction(self, instruction_id: str) -> bool:
        """
        Delete an instruction
        
        Args:
            instruction_id: Instruction ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            self.collection.delete(ids=[instruction_id])
            return True
        except Exception:
            return False
    
    def list_instructions(
        self,
        task_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all instructions, optionally filtered by task type
        
        Args:
            task_type: Optional filter by task type
            limit: Optional limit on number of results
            
        Returns:
            List of instruction dicts
        """
        where_clause = None
        if task_type:
            where_clause = {"task_type": task_type}
        
        results = self.collection.get(
            where=where_clause,
            limit=limit
        )
        
        instructions = []
        if results["ids"]:
            for i in range(len(results["ids"])):
                instructions.append({
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
        
        return instructions

