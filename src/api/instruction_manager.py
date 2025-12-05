"""
Instruction management API for CRUD operations on IT ops instructions
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from src.vector_db.instruction_store import InstructionStore
from src.utils.error_handler import (
    ValidationError,
    RetrievalError,
    handle_error
)


class InstructionManager:
    """Manages IT ops instructions with validation and bulk operations"""
    
    def __init__(self, instruction_store: Optional[InstructionStore] = None):
        """
        Initialize instruction manager
        
        Args:
            instruction_store: Optional instruction store instance
        """
        self.store = instruction_store or InstructionStore()
    
    def add_instruction(
        self,
        task_type: str,
        instruction_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a new instruction with validation
        
        Args:
            task_type: Task type (e.g., "password_reset")
            instruction_text: Instruction text
            metadata: Optional metadata
            
        Returns:
            Dict with instruction_id and status
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        if not task_type or not isinstance(task_type, str):
            raise ValidationError("task_type is required and must be a string")
        
        if not instruction_text or not isinstance(instruction_text, str):
            raise ValidationError("instruction_text is required and must be a string")
        
        if len(instruction_text.strip()) < 10:
            raise ValidationError("instruction_text must be at least 10 characters")
        
        try:
            instruction_id = self.store.add_instruction(
                task_type=task_type,
                instruction_text=instruction_text,
                metadata=metadata
            )
            
            return {
                "success": True,
                "instruction_id": instruction_id,
                "message": f"Instruction added successfully for task type: {task_type}"
            }
        except Exception as e:
            error = handle_error(e, "Failed to add instruction")
            raise ValidationError(str(error), details={"task_type": task_type})
    
    def get_instruction(self, instruction_id: str) -> Dict[str, Any]:
        """
        Get instruction by ID
        
        Args:
            instruction_id: Instruction ID
            
        Returns:
            Dict with instruction data
            
        Raises:
            RetrievalError: If instruction not found
        """
        if not instruction_id:
            raise ValidationError("instruction_id is required")
        
        try:
            instruction = self.store.get_instruction_by_id(instruction_id)
            
            if not instruction:
                raise RetrievalError(
                    f"Instruction not found: {instruction_id}",
                    query=instruction_id
                )
            
            return {
                "success": True,
                "instruction": instruction
            }
        except RetrievalError:
            raise
        except Exception as e:
            error = handle_error(e, "Failed to retrieve instruction")
            raise RetrievalError(str(error), query=instruction_id)
    
    def update_instruction(
        self,
        instruction_id: str,
        instruction_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing instruction
        
        Args:
            instruction_id: Instruction ID
            instruction_text: New instruction text (optional)
            metadata: New metadata (optional)
            
        Returns:
            Dict with status
            
        Raises:
            ValidationError: If validation fails
            RetrievalError: If instruction not found
        """
        if not instruction_id:
            raise ValidationError("instruction_id is required")
        
        if instruction_text and len(instruction_text.strip()) < 10:
            raise ValidationError("instruction_text must be at least 10 characters")
        
        if not instruction_text and not metadata:
            raise ValidationError("At least one of instruction_text or metadata must be provided")
        
        try:
            # Check if instruction exists
            existing = self.store.get_instruction_by_id(instruction_id)
            if not existing:
                raise RetrievalError(
                    f"Instruction not found: {instruction_id}",
                    query=instruction_id
                )
            
            success = self.store.update_instruction(
                instruction_id=instruction_id,
                instruction_text=instruction_text,
                metadata=metadata
            )
            
            if not success:
                raise RetrievalError(
                    f"Failed to update instruction: {instruction_id}",
                    query=instruction_id
                )
            
            return {
                "success": True,
                "message": f"Instruction {instruction_id} updated successfully"
            }
        except (ValidationError, RetrievalError):
            raise
        except Exception as e:
            error = handle_error(e, "Failed to update instruction")
            raise ValidationError(str(error), details={"instruction_id": instruction_id})
    
    def delete_instruction(self, instruction_id: str) -> Dict[str, Any]:
        """
        Delete an instruction
        
        Args:
            instruction_id: Instruction ID
            
        Returns:
            Dict with status
            
        Raises:
            ValidationError: If validation fails
            RetrievalError: If instruction not found
        """
        if not instruction_id:
            raise ValidationError("instruction_id is required")
        
        try:
            # Check if instruction exists
            existing = self.store.get_instruction_by_id(instruction_id)
            if not existing:
                raise RetrievalError(
                    f"Instruction not found: {instruction_id}",
                    query=instruction_id
                )
            
            success = self.store.delete_instruction(instruction_id)
            
            if not success:
                raise RetrievalError(
                    f"Failed to delete instruction: {instruction_id}",
                    query=instruction_id
                )
            
            return {
                "success": True,
                "message": f"Instruction {instruction_id} deleted successfully"
            }
        except (ValidationError, RetrievalError):
            raise
        except Exception as e:
            error = handle_error(e, "Failed to delete instruction")
            raise ValidationError(str(error), details={"instruction_id": instruction_id})
    
    def list_instructions(
        self,
        task_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List instructions, optionally filtered by task type
        
        Args:
            task_type: Optional task type filter
            limit: Optional result limit
            
        Returns:
            Dict with list of instructions
        """
        try:
            instructions = self.store.list_instructions(
                task_type=task_type,
                limit=limit
            )
            
            return {
                "success": True,
                "instructions": instructions,
                "count": len(instructions)
            }
        except Exception as e:
            error = handle_error(e, "Failed to list instructions")
            raise RetrievalError(str(error))
    
    def search_instructions(
        self,
        query: str,
        task_type: Optional[str] = None,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search instructions by query
        
        Args:
            query: Search query
            task_type: Optional task type filter
            n_results: Number of results
            
        Returns:
            Dict with search results
        """
        if not query or not isinstance(query, str):
            raise ValidationError("query is required and must be a string")
        
        try:
            instructions = self.store.retrieve_instructions(
                query=query,
                task_type=task_type,
                n_results=n_results
            )
            
            return {
                "success": True,
                "instructions": instructions,
                "count": len(instructions),
                "query": query
            }
        except Exception as e:
            error = handle_error(e, "Failed to search instructions")
            raise RetrievalError(str(error), query=query)
    
    def bulk_import_from_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Import instructions from a JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dict with import results
            
        Raises:
            ValidationError: If file is invalid
        """
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle single instruction or list
            if isinstance(data, dict):
                instructions = [data]
            elif isinstance(data, list):
                instructions = data
            else:
                raise ValidationError("File must contain a JSON object or array")
            
            # Validate and import
            imported = []
            errors = []
            
            for idx, instruction in enumerate(instructions):
                try:
                    if not isinstance(instruction, dict):
                        errors.append(f"Item {idx}: Must be a JSON object")
                        continue
                    
                    task_type = instruction.get("task_type")
                    instruction_text = instruction.get("instruction_text")
                    metadata = instruction.get("metadata")
                    
                    if not task_type or not instruction_text:
                        errors.append(f"Item {idx}: Missing required fields (task_type, instruction_text)")
                        continue
                    
                    instruction_id = self.store.add_instruction(
                        task_type=task_type,
                        instruction_text=instruction_text,
                        metadata=metadata
                    )
                    imported.append(instruction_id)
                except Exception as e:
                    errors.append(f"Item {idx}: {str(e)}")
            
            return {
                "success": len(errors) == 0,
                "imported_count": len(imported),
                "error_count": len(errors),
                "imported_ids": imported,
                "errors": errors
            }
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON file: {str(e)}")
        except Exception as e:
            error = handle_error(e, "Failed to import instructions from file")
            raise ValidationError(str(error), details={"file_path": str(file_path)})
    
    def bulk_import_from_directory(self, directory_path: Path) -> Dict[str, Any]:
        """
        Import instructions from a directory of JSON files
        
        Args:
            directory_path: Path to directory containing JSON files
            
        Returns:
            Dict with import results
        """
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValidationError(f"Directory not found: {directory_path}")
        
        json_files = list(directory_path.glob("*.json"))
        
        if not json_files:
            raise ValidationError(f"No JSON files found in directory: {directory_path}")
        
        all_imported = []
        all_errors = []
        
        for json_file in json_files:
            try:
                result = self.bulk_import_from_file(json_file)
                all_imported.extend(result.get("imported_ids", []))
                if result.get("errors"):
                    all_errors.extend([f"{json_file.name}: {err}" for err in result["errors"]])
            except Exception as e:
                all_errors.append(f"{json_file.name}: {str(e)}")
        
        return {
            "success": len(all_errors) == 0,
            "imported_count": len(all_imported),
            "error_count": len(all_errors),
            "files_processed": len(json_files),
            "imported_ids": all_imported,
            "errors": all_errors
        }

