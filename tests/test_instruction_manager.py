"""
Tests for instruction management
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.api.instruction_manager import InstructionManager
from src.vector_db.instruction_store import InstructionStore
from src.utils.error_handler import ValidationError, RetrievalError


class TestInstructionManager:
    """Test InstructionManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create instruction manager instance"""
        # Use a test collection name to avoid conflicts
        return InstructionManager()
    
    def test_add_instruction(self, manager):
        """Test adding an instruction"""
        result = manager.add_instruction(
            task_type="password_reset",
            instruction_text="This is a test instruction for password reset procedures.",
            metadata={"platform": "aws", "complexity": "low"}
        )
        
        assert result["success"] is True
        assert "instruction_id" in result
        assert "password_reset" in result["message"]
    
    def test_add_instruction_validation_empty_task_type(self, manager):
        """Test validation for empty task type"""
        with pytest.raises(ValidationError):
            manager.add_instruction(task_type="", instruction_text="Test instruction")
    
    def test_add_instruction_validation_short_text(self, manager):
        """Test validation for short instruction text"""
        with pytest.raises(ValidationError):
            manager.add_instruction(task_type="test", instruction_text="Short")
    
    def test_get_instruction(self, manager):
        """Test getting an instruction"""
        # First add an instruction
        add_result = manager.add_instruction(
            task_type="test_task",
            instruction_text="This is a test instruction for testing purposes."
        )
        instruction_id = add_result["instruction_id"]
        
        # Then get it
        result = manager.get_instruction(instruction_id)
        
        assert result["success"] is True
        assert result["instruction"]["id"] == instruction_id
        assert "test instruction" in result["instruction"]["text"].lower()
    
    def test_get_instruction_not_found(self, manager):
        """Test getting non-existent instruction"""
        with pytest.raises(RetrievalError):
            manager.get_instruction("nonexistent-id")
    
    def test_update_instruction(self, manager):
        """Test updating an instruction"""
        # Add instruction
        add_result = manager.add_instruction(
            task_type="test_task",
            instruction_text="Original instruction text for testing."
        )
        instruction_id = add_result["instruction_id"]
        
        # Update it
        result = manager.update_instruction(
            instruction_id=instruction_id,
            instruction_text="Updated instruction text for testing purposes."
        )
        
        assert result["success"] is True
        
        # Verify update
        get_result = manager.get_instruction(instruction_id)
        assert "Updated" in get_result["instruction"]["text"]
    
    def test_update_instruction_not_found(self, manager):
        """Test updating non-existent instruction"""
        with pytest.raises(RetrievalError):
            manager.update_instruction("nonexistent-id", instruction_text="New text")
    
    def test_update_instruction_validation(self, manager):
        """Test update validation"""
        # Add instruction first
        add_result = manager.add_instruction(
            task_type="test_task",
            instruction_text="Original instruction text for testing."
        )
        instruction_id = add_result["instruction_id"]
        
        # Try to update with short text
        with pytest.raises(ValidationError):
            manager.update_instruction(instruction_id, instruction_text="Short")
        
        # Try to update with nothing
        with pytest.raises(ValidationError):
            manager.update_instruction(instruction_id)
    
    def test_delete_instruction(self, manager):
        """Test deleting an instruction"""
        # Add instruction
        add_result = manager.add_instruction(
            task_type="test_task",
            instruction_text="Instruction to be deleted for testing."
        )
        instruction_id = add_result["instruction_id"]
        
        # Delete it
        result = manager.delete_instruction(instruction_id)
        
        assert result["success"] is True
        
        # Verify deletion
        with pytest.raises(RetrievalError):
            manager.get_instruction(instruction_id)
    
    def test_delete_instruction_not_found(self, manager):
        """Test deleting non-existent instruction"""
        with pytest.raises(RetrievalError):
            manager.delete_instruction("nonexistent-id")
    
    def test_list_instructions(self, manager):
        """Test listing instructions"""
        # Add some instructions
        manager.add_instruction(
            task_type="task1",
            instruction_text="First instruction for testing list functionality."
        )
        manager.add_instruction(
            task_type="task2",
            instruction_text="Second instruction for testing list functionality."
        )
        
        # List all
        result = manager.list_instructions()
        assert result["success"] is True
        assert result["count"] >= 2
        
        # List filtered by task type
        result = manager.list_instructions(task_type="task1")
        assert result["success"] is True
        assert all(inst["metadata"]["task_type"] == "task1" for inst in result["instructions"])
    
    def test_search_instructions(self, manager):
        """Test searching instructions"""
        # Add instruction
        manager.add_instruction(
            task_type="password_reset",
            instruction_text="Instructions for resetting user passwords in AWS IAM."
        )
        
        # Search
        result = manager.search_instructions("password reset")
        assert result["success"] is True
        assert result["count"] > 0
        assert "password" in result["query"].lower()
    
    def test_search_instructions_validation(self, manager):
        """Test search validation"""
        with pytest.raises(ValidationError):
            manager.search_instructions("")
    
    def test_bulk_import_from_file_single(self, manager):
        """Test bulk import from file with single instruction"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            instruction = {
                "task_type": "bulk_test",
                "instruction_text": "This is a test instruction for bulk import testing.",
                "metadata": {"source": "test"}
            }
            json.dump(instruction, f)
            file_path = Path(f.name)
        
        try:
            result = manager.bulk_import_from_file(file_path)
            assert result["success"] is True
            assert result["imported_count"] == 1
        finally:
            file_path.unlink()
    
    def test_bulk_import_from_file_multiple(self, manager):
        """Test bulk import from file with multiple instructions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            instructions = [
                {
                    "task_type": "bulk_test_1",
                    "instruction_text": "First instruction for bulk import testing."
                },
                {
                    "task_type": "bulk_test_2",
                    "instruction_text": "Second instruction for bulk import testing."
                }
            ]
            json.dump(instructions, f)
            file_path = Path(f.name)
        
        try:
            result = manager.bulk_import_from_file(file_path)
            assert result["success"] is True
            assert result["imported_count"] == 2
        finally:
            file_path.unlink()
    
    def test_bulk_import_from_file_invalid(self, manager):
        """Test bulk import with invalid file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            file_path = Path(f.name)
        
        try:
            with pytest.raises(ValidationError):
                manager.bulk_import_from_file(file_path)
        finally:
            file_path.unlink()
    
    def test_bulk_import_from_file_missing_fields(self, manager):
        """Test bulk import with missing required fields"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            instruction = {
                "task_type": "test"
                # Missing instruction_text
            }
            json.dump(instruction, f)
            file_path = Path(f.name)
        
        try:
            result = manager.bulk_import_from_file(file_path)
            assert result["success"] is False
            assert result["error_count"] > 0
        finally:
            file_path.unlink()
    
    def test_bulk_import_from_directory(self, manager):
        """Test bulk import from directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)
            
            # Create test JSON files
            file1 = dir_path / "test1.json"
            with open(file1, 'w') as f:
                json.dump({
                    "task_type": "dir_test_1",
                    "instruction_text": "First instruction from directory import."
                }, f)
            
            file2 = dir_path / "test2.json"
            with open(file2, 'w') as f:
                json.dump({
                    "task_type": "dir_test_2",
                    "instruction_text": "Second instruction from directory import."
                }, f)
            
            result = manager.bulk_import_from_directory(dir_path)
            assert result["success"] is True
            assert result["imported_count"] == 2
            assert result["files_processed"] == 2
    
    def test_bulk_import_from_directory_not_found(self, manager):
        """Test bulk import from non-existent directory"""
        with pytest.raises(ValidationError):
            manager.bulk_import_from_directory(Path("/nonexistent/directory"))

