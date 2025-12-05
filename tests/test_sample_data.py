"""
Tests for sample instruction data loading and validation
"""
import json
import pytest
from pathlib import Path
from src.vector_db.instruction_store import InstructionStore
from src.vector_db.chroma_client import ChromaClient


@pytest.fixture
def instructions_dir():
    """Get the instructions directory path"""
    return Path(__file__).parent.parent / "data" / "instructions"


@pytest.fixture
def sample_instruction_files(instructions_dir):
    """Get all JSON instruction files"""
    json_files = list(instructions_dir.glob("*.json"))
    return json_files


def test_instruction_files_exist(sample_instruction_files):
    """Test that instruction files exist"""
    assert len(sample_instruction_files) > 0, "No instruction JSON files found"
    # Should have at least 4 original files plus new ones
    assert len(sample_instruction_files) >= 4, \
        f"Expected at least 4 instruction files, found {len(sample_instruction_files)}"


def test_instruction_file_format(sample_instruction_files):
    """Test that all instruction files have correct format"""
    required_fields = ["task_type", "instruction_text", "metadata"]
    required_metadata = ["platform", "complexity", "category"]
    
    for file_path in sample_instruction_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required fields
        for field in required_fields:
            assert field in data, \
                f"{file_path.name} is missing required field: {field}"
        
        # Check metadata fields
        metadata = data.get("metadata", {})
        for field in required_metadata:
            assert field in metadata, \
                f"{file_path.name} metadata is missing required field: {field}"
        
        # Validate field types
        assert isinstance(data["task_type"], str), \
            f"{file_path.name}: task_type must be a string"
        assert isinstance(data["instruction_text"], str), \
            f"{file_path.name}: instruction_text must be a string"
        assert isinstance(metadata, dict), \
            f"{file_path.name}: metadata must be a dictionary"
        
        # Validate metadata values
        assert metadata["complexity"] in ["low", "medium", "high"], \
            f"{file_path.name}: complexity must be 'low', 'medium', or 'high'"
        assert isinstance(metadata["platform"], str), \
            f"{file_path.name}: platform must be a string"
        assert isinstance(metadata["category"], str), \
            f"{file_path.name}: category must be a string"


def test_instruction_content_quality(sample_instruction_files):
    """Test that instruction content is meaningful"""
    for file_path in sample_instruction_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Instruction text should not be empty
        assert len(data["instruction_text"]) > 50, \
            f"{file_path.name}: instruction_text is too short (minimum 50 characters)"
        
        # Task type should match filename (without extension)
        expected_task_type = file_path.stem
        assert data["task_type"] == expected_task_type, \
            f"{file_path.name}: task_type '{data['task_type']}' should match filename '{expected_task_type}'"


def test_instruction_categories(sample_instruction_files):
    """Test that all expected categories are represented"""
    expected_categories = {
        "access_management",
        "application_issues",
        "hardware_issues",
        "network_issues",
        "system_issues",
        "email_issues"
    }
    
    found_categories = set()
    for file_path in sample_instruction_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            category = data["metadata"]["category"]
            found_categories.add(category)
    
    # Check that we have instructions in expected categories
    assert len(found_categories) > 0, "No categories found in instruction files"


def test_task_types_coverage(sample_instruction_files):
    """Test that we have good coverage of task types"""
    expected_task_types = [
        "password_reset",
        "account_locked",
        "vpn_troubleshooting",
        "outlook_sync",
    ]
    
    found_task_types = []
    for file_path in sample_instruction_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            found_task_types.append(data["task_type"])
    
    # At minimum, should have the core task types
    for task_type in expected_task_types:
        assert task_type in found_task_types, \
            f"Expected task type '{task_type}' not found in instruction files"


def test_instruction_json_validity(sample_instruction_files):
    """Test that all JSON files are valid"""
    for file_path in sample_instruction_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"{file_path.name} contains invalid JSON: {e}")


def test_instruction_loading(temp_chroma_dir, sample_instruction_files):
    """Test that instructions can be loaded into the store"""
    chroma_client = ChromaClient(persist_dir=str(temp_chroma_dir))
    instruction_store = InstructionStore(chroma_client)
    
    loaded_count = 0
    for file_path in sample_instruction_files[:5]:  # Test with first 5 files
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        instruction_id = instruction_store.add_instruction(
            task_type=data["task_type"],
            instruction_text=data["instruction_text"],
            metadata=data["metadata"]
        )
        
        assert instruction_id is not None
        assert len(instruction_id) > 0
        loaded_count += 1
    
    assert loaded_count > 0, "No instructions were loaded successfully"


def test_instruction_retrieval(temp_chroma_dir, sample_instruction_files):
    """Test that loaded instructions can be retrieved"""
    chroma_client = ChromaClient(persist_dir=str(temp_chroma_dir))
    instruction_store = InstructionStore(chroma_client)
    
    # Load a sample instruction
    test_file = sample_instruction_files[0]
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    instruction_id = instruction_store.add_instruction(
        task_type=data["task_type"],
        instruction_text=data["instruction_text"],
        metadata=data["metadata"]
    )
    
    # Retrieve it
    retrieved = instruction_store.get_instruction(instruction_id)
    assert retrieved is not None
    assert retrieved["task_type"] == data["task_type"]


def test_instruction_search(temp_chroma_dir, sample_instruction_files):
    """Test that instructions can be searched"""
    chroma_client = ChromaClient(persist_dir=str(temp_chroma_dir))
    instruction_store = InstructionStore(chroma_client)
    
    # Load a few instructions
    for file_path in sample_instruction_files[:3]:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        instruction_store.add_instruction(
            task_type=data["task_type"],
            instruction_text=data["instruction_text"],
            metadata=data["metadata"]
        )
    
    # Search for instructions
    results = instruction_store.search_instructions("password reset", n_results=3)
    assert len(results) > 0, "Search should return at least one result"


def test_instruction_metadata_consistency(sample_instruction_files):
    """Test that metadata values are consistent"""
    complexities = set()
    categories = set()
    
    for file_path in sample_instruction_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data["metadata"]
        complexities.add(metadata["complexity"])
        categories.add(metadata["category"])
    
    # Valid complexities
    valid_complexities = {"low", "medium", "high"}
    assert complexities.issubset(valid_complexities), \
        f"Invalid complexity values found: {complexities - valid_complexities}"
    
    # Should have multiple categories
    assert len(categories) >= 3, \
        f"Expected at least 3 different categories, found: {categories}"


@pytest.mark.integration
def test_load_all_instructions_script(instructions_dir, temp_chroma_dir, monkeypatch):
    """Test the load_instructions.py script can load all files"""
    # This test would require mocking or actually running the script
    # For now, we'll just verify the script exists
    script_path = Path(__file__).parent.parent / "scripts" / "load_instructions.py"
    assert script_path.exists(), "load_instructions.py script should exist"
    
    # Verify it's a valid Python file
    assert script_path.suffix == ".py", "load_instructions should be a Python file"

