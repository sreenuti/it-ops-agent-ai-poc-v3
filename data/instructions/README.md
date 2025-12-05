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

## Available Instructions

### Access Management

- **password_reset.json** - Password reset procedures for AWS IAM, Active Directory, and local Windows accounts
- **account_locked.json** - Account unlock procedures for AD, AWS IAM, and local Windows accounts
- **jira_access_request.json** - Grant Jira access and assign appropriate roles
- **access_jira.json** - Troubleshoot Jira access issues and authentication problems
- **shared_drive_access.json** - Grant shared drive access for Windows shares and OneDrive/SharePoint

### Application Issues

- **outlook_sync.json** - Troubleshoot Outlook synchronization issues
- **outlook_not_syncing.json** - Fix Outlook sync problems and connection issues
- **teams_not_signing_in.json** - Resolve Microsoft Teams authentication issues
- **zoom_audio_not_working.json** - Fix Zoom audio problems and device configuration
- **application_crashing.json** - Troubleshoot application crashes and errors
- **software_install_request.json** - Handle software installation requests and deployment

### Hardware Issues

- **laptop_overheating.json** - Diagnose and resolve laptop overheating issues
- **monitor_not_detected.json** - Fix monitor detection and display issues
- **printer_not_working.json** - Troubleshoot printer problems and connectivity
- **no_sound_windows.json** - Fix Windows audio issues and device configuration

### Network Issues

- **vpn_troubleshooting.json** - General VPN troubleshooting steps and diagnostics
- **vpn_not_connecting.json** - Fix VPN connection problems and authentication
- **wifi_not_working.json** - Resolve WiFi connectivity issues and configuration

### System Issues

- **laptop_running_slow.json** - Diagnose and optimize slow laptop performance
- **blue_screen_error.json** - Troubleshoot BSOD errors and system crashes
- **excel_freezing.json** - Fix Excel freezing and performance issues
- **onedrive_sync_issue.json** - Resolve OneDrive sync problems and conflicts

### Email Issues

- **email_delivery_failed.json** - Troubleshoot email delivery failures and bounce-backs

## Adding New Instructions

To add a new instruction:

1. Create a new JSON file following the format above
2. Use a descriptive filename matching the task_type
3. Include comprehensive, step-by-step instructions
4. Add appropriate metadata (platform, complexity, category)
5. Load it using the load script or programmatically

## Categories

Tasks are categorized as:
- `access_management` - User access, permissions, accounts
- `application_issues` - Software and application problems
- `hardware_issues` - Physical hardware problems
- `network_issues` - Network connectivity and VPN
- `system_issues` - Operating system and performance
- `email_issues` - Email delivery and configuration

## Complexity Levels

- `low` - Simple tasks, few steps, minimal risk
- `medium` - Moderate complexity, multiple steps, some risk
- `high` - Complex tasks, many steps, higher risk or requires advanced knowledge
