# Sample Instructions

This directory contains sample IT operations instructions in JSON format. Each instruction file represents a specific task type that the IT Ops Agent can handle.

## File Format

Each JSON file contains:
- `task_type`: The type of task (e.g., "password_reset", "vpn_troubleshooting")
- `instruction_text`: The detailed procedure/instructions for the task
- `metadata`: Additional metadata including:
  - `platform`: Platforms this applies to (e.g., "aws,ad,windows")
  - `complexity`: Task complexity level (low, medium, high)
  - `category`: Task category (access_management, network_issues, application_issues, etc.)

## Loading Instructions

To load these instructions into the instruction store, use the `load_instructions.py` script:

```bash
python scripts/load_instructions.py
```

Or load them programmatically:

```python
from src.vector_db.instruction_store import InstructionStore
import json

store = InstructionStore()

with open('data/instructions/password_reset.json', 'r') as f:
    instruction = json.load(f)
    store.add_instruction(
        task_type=instruction['task_type'],
        instruction_text=instruction['instruction_text'],
        metadata=instruction.get('metadata', {})
    )
```

## Current Instructions

- `password_reset.json` - Password reset procedures for AWS IAM, Active Directory, and local Windows accounts
- `vpn_troubleshooting.json` - VPN connection troubleshooting steps
- `outlook_sync.json` - Outlook synchronization issue resolution
- `account_locked.json` - Account unlock procedures

## Adding New Instructions

To add a new instruction:

1. Create a new JSON file following the format above
2. Use a descriptive filename matching the task_type
3. Include comprehensive, step-by-step instructions
4. Add appropriate metadata
5. Load it using the load script or programmatically

