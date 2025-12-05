"""
Test project setup and structure
"""
import pytest
from pathlib import Path


def test_project_structure_exists():
    """Test that required directories exist"""
    base_path = Path(__file__).parent.parent
    
    required_dirs = [
        "src",
        "src/agents",
        "src/agents/adapters",
        "src/vector_db",
        "src/script_executor",
        "src/task_decomposer",
        "src/api",
        "src/config",
        "src/utils",
        "tests",
        "data/instructions",
        "docker",
        "k8s",
    ]
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        assert full_path.exists(), f"Directory {dir_path} does not exist"
        assert full_path.is_dir(), f"{dir_path} is not a directory"


def test_requirements_file_exists():
    """Test that requirements.txt exists"""
    requirements_path = Path(__file__).parent.parent / "requirements.txt"
    assert requirements_path.exists(), "requirements.txt does not exist"
    assert requirements_path.is_file(), "requirements.txt is not a file"


def test_env_example_exists():
    """Test that .env.example exists"""
    env_example_path = Path(__file__).parent.parent / ".env.example"
    assert env_example_path.exists(), ".env.example does not exist"


def test_readme_exists():
    """Test that README.md exists"""
    readme_path = Path(__file__).parent.parent / "README.md"
    assert readme_path.exists(), "README.md does not exist"


def test_init_files_exist():
    """Test that __init__.py files exist in key directories"""
    base_path = Path(__file__).parent.parent
    
    init_files = [
        "src/__init__.py",
        "src/agents/__init__.py",
        "src/agents/adapters/__init__.py",
        "src/vector_db/__init__.py",
        "src/script_executor/__init__.py",
        "src/task_decomposer/__init__.py",
        "src/api/__init__.py",
        "src/config/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py",
    ]
    
    for init_file in init_files:
        full_path = base_path / init_file
        assert full_path.exists(), f"{init_file} does not exist"

