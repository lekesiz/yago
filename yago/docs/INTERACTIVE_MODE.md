# 💬 YAGO Interactive Mode

**Status**: ✅ Complete (v2.4)
**Added**: 2025-01-06
**Author**: YAGO Development Team

## 🎯 Overview

Interactive Mode allows real-time collaboration between you and YAGO during code generation. Instead of waiting until the end, YAGO can now ask you questions and get clarifications while it works!

## 🚀 Quick Start

### Enable Interactive Mode

```bash
# With idea
python main.py --idea "Build a REST API" --interactive

# Short form
python main.py --idea "Build a REST API" -i

# With template
python main.py --template fastapi_rest_api --interactive
```

### Example Interaction

```
🤖 YAGO - Yerel AI Geliştirme Orkestratörü
============================================================
💬 Interactive chat mode enabled
   You can provide input when YAGO asks questions
   Type 'skip' to use default answer
   Type 'auto' to disable interactive mode

============================================================
🤔 YAGO Question:
============================================================
Should I use SQLite or PostgreSQL for the database?

Context:
  • project_type: REST API
  • complexity: Medium

Default answer: SQLite

Your answer (or 'skip'/'auto'):
→ PostgreSQL

ℹ️  YAGO: Noted. Using PostgreSQL for database...
```

## 🎨 Features

### 1. **Open Questions** (`ask_user` tool)

YAGO asks you open-ended questions:

```python
# Example usage by YAGO
result = ask_user(
    question="What should the API endpoint be named?",
    default_answer="/api/v1/users",
    context="Creating user management endpoints"
)
```

### 2. **Multiple Choice** (`ask_user_choice` tool)

Choose from predefined options:

```python
# Example usage by YAGO
database = ask_user_choice(
    question="Which database?",
    choices=["SQLite", "PostgreSQL", "MySQL", "MongoDB"],
    default_index=0,  # SQLite
    context="Backend data storage"
)
```

### 3. **Yes/No Questions** (`ask_user_yes_no` tool)

Quick boolean decisions:

```python
# Example usage by YAGO
enable_logging = ask_user_yes_no(
    question="Enable debug logging?",
    default=True,
    context="Development environment"
)
```

### 4. **Notifications** (`notify_user` tool)

YAGO informs you about important events:

```python
# Example usage by YAGO
notify_user(
    message="Generated 10 test cases successfully",
    emoji="✅"
)
```

## ⚙️ Configuration

### Timeout Settings

Questions have a 30-second timeout by default. If you don't respond, YAGO uses the default answer.

### Disable Mid-Run

Type `auto` at any prompt to disable interactive mode for the rest of the run:

```
Your answer (or 'skip'/'auto'):
→ auto
   → Interactive mode disabled
```

### Skip Question

Type `skip` to use the default answer without disabling interactive mode:

```
Your answer (or 'skip'/'auto'):
→ skip
   → Using default: SQLite
```

## 📋 Use Cases

### 1. **Architecture Decisions**

YAGO asks about:
- Database choice (SQL vs NoSQL)
- Authentication method (JWT, OAuth, Session)
- API design (REST vs GraphQL)
- Framework selection

### 2. **Feature Preferences**

YAGO asks about:
- Logging level
- Error handling strategy
- Test coverage preferences
- Documentation style

### 3. **Technical Choices**

YAGO asks about:
- Library versions
- Deployment target
- CI/CD preferences
- Code style preferences

### 4. **Clarifications**

YAGO asks when requirements are ambiguous:
- "Should user emails be unique?"
- "Allow anonymous access?"
- "Enable rate limiting?"

## 🎭 Behavior

### **Planner Agent** (Claude)

Can ask questions about:
- Project structure
- Technology stack
- Architecture patterns
- Requirements clarification

### **Coder Agent** (GPT-4)

Can ask questions about:
- Implementation details
- Library choices
- Code organization
- Naming conventions

### **Other Agents**

Currently, only Planner and Coder have interactive tools. Tester, Reviewer, and Documenter work autonomously.

## 📊 Conversation History

All interactions are recorded and exported:

```python
# Exported to chat_history.json after run
{
  "summary": {
    "total_interactions": 5,
    "enabled": true
  },
  "interactions": [
    {
      "timestamp": "2025-01-06T10:30:45",
      "question": "Which database?",
      "answer": "PostgreSQL",
      "context": {"project_type": "REST API"}
    }
  ]
}
```

## 🔧 Advanced Usage

### Programmatic Access

```python
from utils.interactive_chat import get_interactive_chat

# Get the chat instance
chat = get_interactive_chat(enabled=True)

# Ask a question
answer = chat.ask_question(
    question="Your question here?",
    default_answer="default",
    timeout=30
)

# Get history
history = chat.get_history()

# Export to file
chat.export_history("my_session.json")
```

### Custom Tools

Create your own interactive tools:

```python
from crewai.tools import BaseTool
from utils.interactive_chat import get_interactive_chat

class MyCustomTool(BaseTool):
    name = "my_question_tool"
    description = "Asks user a custom question"

    def _run(self):
        chat = get_interactive_chat()
        return chat.ask_question("Your question?")
```

## 🐛 Troubleshooting

### Issue: Timeout Errors

**Problem**: Questions timeout too quickly

**Solution**: Questions auto-timeout after 30 seconds. Respond faster or modify timeout in code.

### Issue: Input Not Detected

**Problem**: Input prompt doesn't appear

**Solution**: Ensure you're running in a proper terminal (not background/daemon mode)

### Issue: Unexpected Auto Mode

**Problem**: Interactive mode disabled unexpectedly

**Solution**: Check if you typed "auto" by mistake. Restart YAGO to re-enable.

## 📈 Performance Impact

- **Latency**: +0.5-2s per question (waiting for user input)
- **Token Usage**: No impact (questions don't use API)
- **Cost**: No impact
- **Speed**: Depends on user response time

## 🔒 Security & Privacy

- All conversations stored locally
- No data sent to external servers
- Chat history can be deleted manually
- Sensitive inputs are logged (review before sharing logs)

## 🎯 Best Practices

### DO ✅

- Enable for complex projects with many decisions
- Use when requirements are ambiguous
- Provide clear, concise answers
- Review chat history after completion

### DON'T ❌

- Enable for simple, well-defined projects
- Leave prompts unanswered (defeats the purpose)
- Share chat history with sensitive data
- Use in automated/CI environments

## 🚀 Future Enhancements

Planned for future versions:

- [ ] Voice input support
- [ ] Multi-choice with checkboxes
- [ ] Confirmation dialogs for risky operations
- [ ] Conversation memory across runs
- [ ] Web UI for interactive mode
- [ ] Suggested answers based on project context

## 📚 Examples

### Example 1: API Development

```bash
python main.py --idea "User management API" --interactive
```

YAGO might ask:
- "Which database: SQLite, PostgreSQL, or MySQL?"
- "Enable JWT authentication? [Y/n]"
- "Should passwords be hashed with bcrypt or argon2?"
- "API versioning strategy: URL or Header?"

### Example 2: Data Pipeline

```bash
python main.py --idea "ETL pipeline for CSV data" --interactive
```

YAGO might ask:
- "Data source: Local files or S3?"
- "Error handling: Skip invalid rows or fail completely?"
- "Output format: JSON, Parquet, or Database?"
- "Schedule: Cron job or on-demand?"

### Example 3: Web App

```bash
python main.py --idea "Flask TODO app" --interactive
```

YAGO might ask:
- "Frontend: Templates or REST API only?"
- "Use Bootstrap or custom CSS?"
- "Enable user registration?"
- "Session management or JWT tokens?"

## 🙌 Feedback

Interactive Mode is brand new! Share your experience:
- GitHub Issues: https://github.com/lekesiz/yago/issues
- Feature requests welcome
- Bug reports appreciated

---

**Version**: 2.4
**Last Updated**: 2025-01-06
**Compatibility**: YAGO v1.3+
