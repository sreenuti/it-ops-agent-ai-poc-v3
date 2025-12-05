"""
Utility script to load sample instructions from data/instructions/ into the instruction store
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_db.instruction_store import InstructionStore
from src.vector_db.chroma_client import ChromaClient
from src.config.settings import get_settings


def load_instructions_from_file(file_path: Path, instruction_store: InstructionStore) -> bool:
    """
    Load a single instruction from a JSON file
    
    Args:
        file_path: Path to the instruction JSON file
        instruction_store: Instruction store instance
        
    Returns:
        True if loaded successfully, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            instruction_data = json.load(f)
        
        instruction_id = instruction_store.add_instruction(
            task_type=instruction_data['task_type'],
            instruction_text=instruction_data['instruction_text'],
            metadata=instruction_data.get('metadata', {})
        )
        
        print(f"✓ Loaded instruction: {instruction_data['task_type']} (ID: {instruction_id})")
        return True
        
    except Exception as e:
        print(f"✗ Failed to load {file_path.name}: {str(e)}")
        return False


def load_all_instructions(instructions_dir: Path = None) -> dict:
    """
    Load all instruction files from the instructions directory
    
    Args:
        instructions_dir: Path to instructions directory (defaults to data/instructions/)
        
    Returns:
        Dict with success count and total count
    """
    if instructions_dir is None:
        # Get the project root (parent of scripts directory)
        project_root = Path(__file__).parent.parent
        instructions_dir = project_root / "data" / "instructions"
    
    if not instructions_dir.exists():
        print(f"✗ Instructions directory not found: {instructions_dir}")
        return {"success": 0, "total": 0}
    
    # Initialize instruction store
    settings = get_settings()
    chroma_client = ChromaClient(persist_dir=settings.chroma_persist_dir)
    instruction_store = InstructionStore(chroma_client)
    
    # Find all JSON files (excluding README.md)
    json_files = list(instructions_dir.glob("*.json"))
    
    if not json_files:
        print(f"✗ No JSON instruction files found in {instructions_dir}")
        return {"success": 0, "total": 0}
    
    print(f"Found {len(json_files)} instruction file(s) to load...\n")
    
    success_count = 0
    for json_file in json_files:
        if load_instructions_from_file(json_file, instruction_store):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"Loaded {success_count}/{len(json_files)} instruction(s) successfully")
    print(f"{'='*50}")
    
    return {"success": success_count, "total": len(json_files)}


def main():
    """Main entry point"""
    print("IT Ops Agent - Instruction Loader")
    print("=" * 50)
    
    # Check if instructions directory exists
    project_root = Path(__file__).parent.parent
    instructions_dir = project_root / "data" / "instructions"
    
    if not instructions_dir.exists():
        print(f"Creating instructions directory: {instructions_dir}")
        instructions_dir.mkdir(parents=True, exist_ok=True)
        print("Please add instruction JSON files to this directory and run again.")
        return
    
    # Load instructions
    result = load_all_instructions(instructions_dir)
    
    if result["success"] > 0:
        print("\n✓ Instructions loaded successfully!")
        print("You can now use the IT Ops Agent with these instructions.")
    else:
        print("\n✗ No instructions were loaded. Please check the error messages above.")


if __name__ == "__main__":
    main()

