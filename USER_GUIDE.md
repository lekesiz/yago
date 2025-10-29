# 📘 YAGO v8.0 - Complete User Guide

**Version**: 8.0.0
**Last Updated**: 2025-10-29
**Status**: Production Ready

---

## 🎯 What is YAGO?

**YAGO (Yet Another Genius Orchestrator)** is an AI-powered code generation platform that transforms your ideas into production-ready applications. Simply describe what you want to build, answer a few clarifying questions, and YAGO generates complete, working code with tests and documentation.

### Key Features

- 🤖 **Multi-AI Integration**: Uses OpenAI GPT-4, Claude, Gemini, and Cursor
- 💬 **Smart Clarification**: Asks intelligent questions to understand your needs
- 🚀 **Real Code Generation**: Creates actual, production-ready code
- 📁 **Complete Projects**: Generates code, tests, docs, and dependencies
- 📊 **Project Management**: Track all your generated projects
- 💰 **Cost Tracking**: Monitor AI usage and costs
- 🌐 **Modern UI**: Beautiful, responsive dashboard

---

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- OpenAI API key (required)
- Claude/Gemini/Cursor keys (optional)

### 2. Installation

```bash
# Clone repository
git clone https://github.com/lekesiz/yago.git
cd yago

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd yago/web/frontend
npm install
```

### 3. Configuration

Create `.env` file in project root:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional (but recommended)
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=your-gemini-key
CURSOR_API_KEY=your-cursor-key

# Database (SQLite by default)
DATABASE_URL=sqlite:///./yago.db
```

### 4. Run Application

```bash
# Terminal 1: Start Backend
python3 -m uvicorn yago.web.backend.main:app --reload

# Terminal 2: Start Frontend
cd yago/web/frontend
npm run dev
```

### 5. Open Browser

Navigate to `http://localhost:3000`

---

## 📖 User Journey

### Step 1: Create Project

1. Click **"+ Create Project"** tab
2. Choose between:
   - **📦 Choose Template**: Pre-built project templates
   - **✏️ Custom Project**: Describe your own idea

### Step 2: Describe Your Idea

Enter your project description:
- **Good**: "REST API for task management with user authentication"
- **Better**: "FastAPI backend for a todo app with JWT auth, PostgreSQL database, and CRUD operations"
- **Best**: "E-commerce API with products, cart, orders, Stripe payments, and admin dashboard"

### Step 3: Set Clarification Depth

Choose how many questions YAGO should ask:

- **⚡ Minimal** (~10 questions, 3-5 min)
  - Quick projects
  - Simple applications
  - Prototypes

- **⚖️ Standard** (~20 questions, 8-12 min) ⭐ Recommended
  - Most projects
  - Balanced detail
  - Good quality

- **🎯 Full** (~40+ questions, 15-25 min)
  - Complex systems
  - Enterprise apps
  - Maximum detail

### Step 4: AI Provider (Optional)

Select which AI to use:
- **🎯 Auto**: YAGO chooses best for each task (recommended)
- **🟢 OpenAI**: GPT-4 Turbo
- **🔵 Claude**: Anthropic Claude Opus
- **🔴 Gemini**: Google Gemini Pro
- **⚡ Cursor**: Cursor Large

### Step 5: Answer Questions

YAGO asks intelligent questions about:
- Project requirements
- Technical preferences
- Features and functionality
- User interface needs
- Data structure
- API endpoints
- Testing requirements

**Tips**:
- Be specific and detailed
- Use technical terms when possible
- Mention frameworks/libraries you want
- Describe user workflows
- Skip optional questions if unsure

### Step 6: Review & Generate

1. Review your answers (navigate with Previous/Next)
2. Click **"Complete & Generate Brief"**
3. Select AI agent role and strategy
4. Click **"Create Project"**

### Step 7: Execute Code Generation

1. Go to **📁 Projects** tab
2. Find your project
3. Click **"Execute"** button
4. Wait 30-60 seconds
5. ✅ Code generated!

### Step 8: View Generated Code

**Option A: In Dashboard**
- Click "View Files" on project card
- Browse generated files
- View code with syntax highlighting

**Option B: On Filesystem**
```bash
cd generated_projects/[project-id]/
ls -la
cat src/main.py
```

**Option C: Via API**
```bash
# List files
curl http://localhost:8000/api/v1/projects/[id]/files

# Read a file
curl http://localhost:8000/api/v1/projects/[id]/files/src/main.py
```

---

## 💡 Use Cases

### 1. Rapid Prototyping
**Scenario**: Need a quick MVP for investor demo

```
Input: "Landing page with email signup and Stripe checkout"
Output: React app with components, API integration, and styling
Time: ~5 minutes
```

### 2. Learning New Frameworks
**Scenario**: Want to learn FastAPI

```
Input: "Simple FastAPI blog with posts and comments"
Output: Complete FastAPI project with examples and best practices
Benefit: Learn by exploring working code
```

### 3. Boilerplate Generation
**Scenario**: Starting a new project

```
Input: "Next.js 14 app with TypeScript, Tailwind, and authentication"
Output: Full project structure with all configurations
Saved: Hours of setup time
```

### 4. API Development
**Scenario**: Need a backend API

```
Input: "REST API for inventory management with PostgreSQL"
Output: FastAPI with CRUD, database models, and tests
Quality: Production-ready code
```

### 5. Microservices
**Scenario**: Building microservices architecture

```
Input: "Payment processing microservice with Stripe"
Output: Isolated service with API, webhooks, and error handling
```

---

## 🎨 Dashboard Features

### Overview Tab
- System status
- Recent projects
- Quick actions
- Statistics

### Create Project Tab
- Template selector
- Custom project form
- Clarification wizard
- AI provider selection

### Projects Tab 📁
- All your projects
- Status tracking (creating, executing, completed)
- Search and filtering
- Quick actions:
  - View details
  - Execute code generation
  - View files
  - Delete project

### AI Models Tab 🤖
- View all 9 AI models
- Compare capabilities
- See pricing
- Check availability
- Model comparison tool (select up to 4)

### Analytics Tab 📊
- Usage statistics
- Cost tracking
- Provider analytics
- Performance metrics
- Trend graphs

### Marketplace Tab 🛒
- Project templates
- Extensions
- Integrations
- Community resources

---

## 🔧 Advanced Features

### Multi-Provider Strategy

YAGO automatically uses the best AI for each task:

| Task | Provider | Reason |
|------|----------|--------|
| Architecture Design | OpenAI GPT-4 | Best for structured planning |
| Code Generation | OpenAI GPT-4 | High-quality code |
| API Endpoints | Claude Opus | Expert at API design |
| Test Generation | OpenAI GPT-3.5 | Fast and cost-effective |
| Documentation | OpenAI GPT-4 | Clear explanations |

### Cost Optimization

YAGO tracks costs in real-time:

```
Average project costs:
- Minimal depth: $0.01 - $0.05
- Standard depth: $0.10 - $0.30
- Full depth: $0.50 - $1.00
```

**Cost Alerts**:
- Budget exceeded warnings (>120%)
- Weekly spending limits
- Provider usage breakdown

### File System Organization

Generated projects follow best practices:

```
generated_projects/[project-id]/
├── src/                    # Source code
│   ├── main.py            # Main application
│   ├── models.py          # Data models
│   ├── api.py             # API endpoints
│   └── ...
├── tests/                  # Unit tests
│   ├── test_main.py
│   └── test_models.py
├── docs/                   # Documentation
├── README.md              # Project documentation
└── requirements.txt       # Dependencies
```

---

## 📚 Examples

### Example 1: Blog API

**Input**:
```
Project: "Blog API with posts and comments"
Depth: Standard
Questions answered: 18
```

**Generated Output**:
- `src/main.py` - FastAPI application
- `src/models.py` - Post and Comment models
- `src/api.py` - CRUD endpoints
- `tests/` - Unit tests
- `README.md` - API documentation

**Code Quality**:
- ✅ Proper error handling
- ✅ Input validation
- ✅ Database integration
- ✅ RESTful design
- ✅ Comprehensive tests

### Example 2: E-commerce Platform

**Input**:
```
Project: "E-commerce API with products, cart, and checkout"
Depth: Full
Questions answered: 42
```

**Generated Output**:
- Complete FastAPI backend
- Product catalog system
- Shopping cart logic
- Order processing
- Payment integration structure
- Admin endpoints
- User authentication
- Comprehensive tests
- API documentation

**Time Saved**: 8-10 hours of development

### Example 3: Data Pipeline

**Input**:
```
Project: "ETL pipeline for CSV to PostgreSQL"
Depth: Standard
```

**Generated Output**:
- Data extraction logic
- Transformation functions
- Database loading
- Error handling
- Logging system
- Configuration management

---

## 🛠️ Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements.txt
# Or specific package:
pip install fastapi uvicorn sqlalchemy
```

### Frontend Build Fails

**Problem**: `npm install` errors

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

### API Keys Not Working

**Problem**: "Invalid API key"

**Solution**:
1. Check `.env` file exists in project root
2. Verify no extra spaces in keys
3. Restart backend after changing `.env`

### No Code Generated

**Problem**: Execute button clicked but no files

**Solution**:
1. Check backend logs for errors
2. Verify OpenAI API key is valid
3. Check `generated_projects/` directory permissions
4. Try with minimal depth first

### Database Errors

**Problem**: SQLAlchemy errors

**Solution**:
```bash
# Reset database
rm yago.db
alembic upgrade head
```

---

## 📖 FAQ

**Q: How much does it cost to generate a project?**
A: Typically $0.10-$0.30 for standard projects. Costs are tracked in real-time.

**Q: Can I edit the generated code?**
A: Yes! All code is saved to `generated_projects/` and is fully editable.

**Q: What languages/frameworks are supported?**
A: Currently Python (FastAPI, Django), Node.js (Express), React, Next.js. More coming soon!

**Q: Can I use my own AI models?**
A: Yes, if you have API access. Add keys to `.env` file.

**Q: Is my data secure?**
A: Yes. All code is generated locally. Only prompts are sent to AI providers.

**Q: Can I deploy generated projects?**
A: Absolutely! Generated code is production-ready and deployable.

**Q: How do I update YAGO?**
A: `git pull origin main && pip install -r requirements.txt`

---

## 🎓 Best Practices

### Writing Good Project Descriptions

**Bad**: "Make an app"
**Good**: "Todo app with user auth"
**Best**: "Task management API with JWT authentication, PostgreSQL, and real-time updates"

### Answering Questions

- **Be specific**: Instead of "yes", say "PostgreSQL database"
- **Mention tools**: "Use JWT for auth, Stripe for payments"
- **Describe workflows**: "User signs up → verifies email → creates profile"

### Choosing Depth

- **Minimal**: Simple CRUD, prototypes, learning
- **Standard**: Most production apps ⭐
- **Full**: Enterprise, complex systems, mission-critical

### Managing Projects

- Use descriptive names
- Delete old test projects
- Export important projects
- Review generated code before deploying

---

## 📞 Support

### Documentation
- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Database structure

### Community
- GitHub Issues: https://github.com/lekesiz/yago/issues
- Discussions: https://github.com/lekesiz/yago/discussions

### Updates
- **Version**: 8.0.0
- **Status**: Production Ready
- **Next Release**: v8.1 (Authentication, WebSocket progress)

---

**Made with ❤️ by YAGO Team**
*Transforming ideas into production-ready code with AI*
