# User Guide

This guide helps users get started with the IT Ops Agent System and use it effectively for common IT operations tasks.

## Table of Contents

- [Getting Started](#getting-started)
- [Using the Web Interface](#using-the-web-interface)
- [Common Tasks](#common-tasks)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Tips and Tricks](#tips-and-tricks)

## Getting Started

### Prerequisites

Before using the IT Ops Agent, ensure you have:

1. **Access to the system** - The Gradio web interface should be accessible
2. **Proper credentials** - Required credentials for systems you'll be managing (AWS, Active Directory, etc.)
3. **Permissions** - Appropriate permissions to execute IT operations tasks

### First Time Setup

1. **Load Instructions** (if not already loaded):
   ```bash
   python scripts/load_instructions.py
   ```

2. **Access the Web Interface**:
   - Open your browser
   - Navigate to `http://localhost:7860` (or your configured URL)
   - You should see the IT Ops Agent chat interface

3. **Test Connection**:
   - Send a simple query like "Hello" or "What can you help me with?"
   - Verify the agent responds

## Using the Web Interface

### Interface Overview

The Gradio interface consists of:

- **Chat Window**: Main conversation area displaying messages
- **Input Box**: Where you type your queries
- **Send Button**: Submit your query
- **Clear Chat Button**: Clear conversation history
- **Dry Run Mode**: Toggle to preview commands without executing

### Basic Usage

1. **Type Your Query**:
   - Be specific about what you want to do
   - Include relevant details (usernames, system names, etc.)
   - Example: "Reset password for user john.doe in AWS IAM"

2. **Review the Response**:
   - The agent will retrieve relevant procedures
   - Show what commands will be executed
   - Provide status updates

3. **Execute or Preview**:
   - Use **Dry Run Mode** to see what would happen without executing
   - Disable Dry Run Mode to actually execute commands
   - Review results in the chat window

### Conversation Flow

The agent maintains conversation context:

- Previous messages are remembered
- You can ask follow-up questions
- The agent can reference earlier parts of the conversation

**Example Conversation:**
```
You: Reset password for user john.doe
Agent: ✅ I'll reset the password for john.doe in AWS IAM...

You: What commands did you use?
Agent: I executed the following AWS CLI command: aws iam update-login-profile...
```

## Common Tasks

### Password Resets

**AWS IAM:**
```
Query: "Reset password for user john.doe in AWS IAM to NewPassword123!"
```

**Active Directory:**
```
Query: "Reset Active Directory password for jane.smith"
```

**Local Windows Account:**
```
Query: "Reset local Windows account password for username admin"
```

### Account Management

**Unlock Account:**
```
Query: "Unlock account for user john.doe"
```

**Grant Access:**
```
Query: "Grant Jira access to user jane.smith"
Query: "Give shared drive access to user john.doe for folder \\server\share"
```

### Troubleshooting

**VPN Issues:**
```
Query: "Troubleshoot VPN connection for user john.doe"
Query: "User cannot connect to VPN, help troubleshoot"
```

**Application Issues:**
```
Query: "Outlook is not syncing for user jane.smith"
Query: "Teams sign-in not working for user john.doe"
Query: "Fix Zoom audio problems"
```

**System Issues:**
```
Query: "Laptop is running slow, help optimize"
Query: "Blue screen error occurred, help troubleshoot"
Query: "Excel keeps freezing"
```

**Network Issues:**
```
Query: "WiFi not working on user's laptop"
Query: "Help troubleshoot network connectivity"
```

### Hardware Issues

```
Query: "Laptop is overheating, help diagnose"
Query: "Monitor not being detected"
Query: "Printer not working"
Query: "No sound on Windows laptop"
```

## Best Practices

### 1. Be Specific

**Good:**
```
"Reset password for user john.doe in AWS IAM to NewPassword123! and require password change on next login"
```

**Not Ideal:**
```
"Reset password"
```

### 2. Use Dry Run First

Always use **Dry Run Mode** when:
- Testing a new type of task
- Unsure about what commands will be executed
- Learning what the agent does

**Example:**
1. Enable Dry Run Mode
2. Submit your query
3. Review the commands
4. If satisfied, disable Dry Run Mode and execute

### 3. Provide Context

Include relevant details:
- User identifiers (usernames, email addresses)
- System/platform information (AWS, Active Directory, Windows)
- Specific requirements or constraints

### 4. Review Before Execution

- Read the agent's response carefully
- Check that the commands match your intent
- Verify usernames and system names are correct
- Ensure you have necessary permissions

### 5. Check Results

After execution:
- Verify the operation completed successfully
- Check that the expected changes were made
- Test access or functionality if applicable

### 6. Use Follow-up Questions

If something is unclear:
- Ask for clarification
- Request more details about what will be done
- Ask about alternatives

## Troubleshooting

### Agent Not Responding

1. **Check Connection**:
   - Verify the web interface is accessible
   - Check if the service is running
   - Look for error messages

2. **Check Logs**:
   - Review application logs for errors
   - Check for configuration issues

3. **Restart Service**:
   - Restart the application
   - Check if Chroma database is running

### Commands Not Executing

1. **Check Permissions**:
   - Verify you have necessary permissions
   - Check AWS credentials if using AWS operations
   - Verify domain credentials for AD operations

2. **Check Dry Run Mode**:
   - Ensure Dry Run Mode is disabled
   - Commands won't execute if Dry Run is enabled

3. **Check Error Messages**:
   - Read error messages in the response
   - Common issues: authentication failures, permission errors, network issues

### Wrong Instructions Retrieved

1. **Be More Specific**:
   - Include more details in your query
   - Specify the platform (AWS, Windows, etc.)
   - Mention the task type explicitly

2. **Check Available Instructions**:
   - Review available instruction files
   - Ensure the task type you need is supported
   - Add custom instructions if needed

### Slow Response Times

1. **Check System Resources**:
   - Verify Chroma database is responsive
   - Check network connectivity to OpenAI API
   - Monitor system resources

2. **Simplify Query**:
   - Break complex tasks into smaller queries
   - Avoid overly complex requests

## Tips and Tricks

### 1. Use Natural Language

The agent understands natural language queries:
```
✅ "Reset password for john.doe"
✅ "Can you help unlock jane.smith's account?"
✅ "My laptop is running really slow, what can I do?"
```

### 2. Reference Previous Messages

The agent remembers context:
```
You: Reset password for john.doe
Agent: ✅ Password reset completed

You: Now unlock his account
Agent: ✅ Account unlocked for john.doe
```

### 3. Ask for Explanations

You can ask the agent to explain:
```
You: Reset password for john.doe
Agent: ✅ Password reset completed

You: What did you do exactly?
Agent: I executed the following commands...
```

### 4. Combine Tasks

For related tasks:
```
You: Reset password and unlock account for john.doe
```

The agent will handle both tasks in sequence.

### 5. Use Examples

If unsure about format:
```
You: Show me an example of resetting an AWS IAM password
```

### 6. Verify Before Executing

Always review in Dry Run Mode first:
1. Enable Dry Run Mode
2. Submit query
3. Review commands
4. Disable Dry Run Mode
5. Execute

## Security Considerations

### Credentials

- Never share credentials in the chat interface
- Use environment variables or secure configuration
- Rotate credentials regularly

### Permissions

- Use principle of least privilege
- Only grant necessary permissions
- Regularly audit access

### Audit Trail

- All operations are logged
- Review logs regularly
- Keep audit records for compliance

## Getting Help

### Documentation

- See [README.md](README.md) for setup and configuration
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture
- See [API_REFERENCE.md](API_REFERENCE.md) for API details

### Support

- Check application logs for errors
- Review troubleshooting section above
- Contact your IT administrator for system-level issues

## Advanced Usage

### Programmatic Access

For advanced users, you can use the agent programmatically:

```python
from src.agents.agent_factory import AgentFactory

agent = AgentFactory.create_agent()
result = agent.process_query(
    "Reset password for user john.doe",
    dry_run=True
)
```

See [API_REFERENCE.md](API_REFERENCE.md) for more details.

### Custom Instructions

Add custom instructions for your organization:

1. Create JSON file in `data/instructions/`
2. Follow the format in `data/instructions/README.md`
3. Load using `python scripts/load_instructions.py`

---

**Remember**: Always use Dry Run Mode first to preview commands, and ensure you have proper permissions before executing IT operations tasks.

