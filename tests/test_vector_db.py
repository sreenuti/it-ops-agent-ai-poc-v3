"""
Tests for vector database components
"""
import pytest
from src.vector_db.chroma_client import ChromaClient
from src.vector_db.instruction_store import InstructionStore


def test_chroma_client_initialization(temp_chroma_dir, sample_env_vars):
    """Test Chroma client initialization"""
    client = ChromaClient(persist_dir=temp_chroma_dir)
    
    assert client.client is not None
    assert client.collection is not None
    assert client.collection_name == "test_collection"


def test_chroma_client_health_check(temp_chroma_dir, sample_env_vars):
    """Test Chroma health check"""
    client = ChromaClient(persist_dir=temp_chroma_dir)
    
    # Health check should pass for local client
    assert client.health_check() is True


def test_instruction_store_add_instruction(temp_chroma_dir, sample_env_vars):
    """Test adding an instruction"""
    store = InstructionStore(ChromaClient(persist_dir=temp_chroma_dir))
    
    instruction_id = store.add_instruction(
        task_type="password_reset",
        instruction_text="To reset a password, use: aws iam update-login-profile --user-name USERNAME --password NEW_PASSWORD",
        metadata={"platform": "aws", "complexity": "low"}
    )
    
    assert instruction_id is not None
    assert len(instruction_id) > 0


def test_instruction_store_retrieve_instructions(temp_chroma_dir, sample_env_vars):
    """Test retrieving instructions"""
    store = InstructionStore(ChromaClient(persist_dir=temp_chroma_dir))
    
    # Add test instructions
    store.add_instruction(
        task_type="password_reset",
        instruction_text="Reset password using AWS CLI: aws iam update-login-profile"
    )
    store.add_instruction(
        task_type="vpn_troubleshooting",
        instruction_text="Check VPN connection status and restart service if needed"
    )
    
    # Retrieve instructions
    results = store.retrieve_instructions(
        query="How do I reset a password?",
        n_results=2
    )
    
    assert len(results) > 0
    assert "text" in results[0]
    assert "metadata" in results[0]


def test_instruction_store_filter_by_task_type(temp_chroma_dir, sample_env_vars):
    """Test filtering instructions by task type"""
    store = InstructionStore(ChromaClient(persist_dir=temp_chroma_dir))
    
    # Add instructions with different task types
    store.add_instruction(
        task_type="password_reset",
        instruction_text="Password reset instruction"
    )
    store.add_instruction(
        task_type="vpn_troubleshooting",
        instruction_text="VPN troubleshooting instruction"
    )
    
    # Retrieve with task type filter
    results = store.retrieve_instructions(
        query="password",
        task_type="password_reset",
        n_results=5
    )
    
    # All results should be password_reset type
    for result in results:
        assert result["metadata"]["task_type"] == "password_reset"


def test_instruction_store_get_by_id(temp_chroma_dir, sample_env_vars):
    """Test getting instruction by ID"""
    store = InstructionStore(ChromaClient(persist_dir=temp_chroma_dir))
    
    # Add instruction
    instruction_id = store.add_instruction(
        task_type="password_reset",
        instruction_text="Test instruction"
    )
    
    # Retrieve by ID
    instruction = store.get_instruction_by_id(instruction_id)
    
    assert instruction is not None
    assert instruction["id"] == instruction_id
    assert instruction["text"] == "Test instruction"


def test_instruction_store_update(temp_chroma_dir, sample_env_vars):
    """Test updating an instruction"""
    store = InstructionStore(ChromaClient(persist_dir=temp_chroma_dir))
    
    # Add instruction
    instruction_id = store.add_instruction(
        task_type="password_reset",
        instruction_text="Original text"
    )
    
    # Update instruction
    updated = store.update_instruction(
        instruction_id=instruction_id,
        instruction_text="Updated text",
        metadata={"updated": True}
    )
    
    assert updated is True
    
    # Verify update
    instruction = store.get_instruction_by_id(instruction_id)
    assert instruction["text"] == "Updated text"


def test_instruction_store_delete(temp_chroma_dir, sample_env_vars):
    """Test deleting an instruction"""
    store = InstructionStore(ChromaClient(persist_dir=temp_chroma_dir))
    
    # Add instruction
    instruction_id = store.add_instruction(
        task_type="password_reset",
        instruction_text="To be deleted"
    )
    
    # Delete instruction
    deleted = store.delete_instruction(instruction_id)
    assert deleted is True
    
    # Verify deletion
    instruction = store.get_instruction_by_id(instruction_id)
    assert instruction is None


def test_instruction_store_batch_add(temp_chroma_dir, sample_env_vars):
    """Test batch adding instructions"""
    store = InstructionStore(ChromaClient(persist_dir=temp_chroma_dir))
    
    instructions = [
        {
            "task_type": "password_reset",
            "instruction_text": "Instruction 1"
        },
        {
            "task_type": "vpn_troubleshooting",
            "instruction_text": "Instruction 2"
        }
    ]
    
    ids = store.add_instructions_batch(instructions)
    
    assert len(ids) == 2
    assert all(id is not None for id in ids)

