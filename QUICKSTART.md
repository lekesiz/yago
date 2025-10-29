# 🚀 YAGO v8.0 - 5-Minute Quick Start

**Get YAGO running locally in 5 minutes!**

---

## ⚡ Quick Start

### Option A: Manual Setup (Recommended)

#### 1. Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- OpenAI API key (required)

#### 2. Clone & Setup

```bash
# Clone repository
git clone https://github.com/lekesiz/yago.git
cd yago

# Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key  # Optional
GOOGLE_API_KEY=your-gemini-key     # Optional
CURSOR_API_KEY=your-cursor-key     # Optional
DATABASE_URL=sqlite:///./yago.db
EOF

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd yago/web/frontend
npm install
cd ../..

# Initialize database
alembic upgrade head
```

#### 3. Start Backend

```bash
# Terminal 1
python3 -m uvicorn yago.web.backend.main:app --reload --port 8000
```

#### 4. Start Frontend

```bash
# Terminal 2
cd yago/web/frontend
npm run dev
```

#### 5. Open Browser

Navigate to `http://localhost:3000`

**Access Points**:
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

### Option B: Automated Script

```bash
cd /Users/mikail/Desktop/YAGO
./scripts/start-local.sh
```

**What this does**:
- ✅ Installs Python dependencies
- ✅ Installs Node.js dependencies
- ✅ Creates database
- ✅ Starts backend (http://localhost:8000)
- ✅ Starts frontend (http://localhost:3000)

---

## 🎯 First Test

### Create Your First Project

1. **Go to Dashboard**: http://localhost:3000
2. **Click**: "➕ Create Project" tab
3. **Choose**: "✏️ Custom Project"
4. **Enter Idea**: "REST API for task management with JWT auth"
5. **Set Depth**: "⚖️ Standard" (recommended)
6. **Answer Questions**: ~20 questions (8-12 minutes)
7. **Complete**: Click "Complete & Generate Brief"
8. **Execute**: Go to "📁 Projects" tab → Click "Execute"
9. **Wait**: ~45 seconds
10. **Success!**: 7 files, ~386 lines of code generated! 🎉

### View Generated Code

**Option 1: In Dashboard**
- Click "View Files" on project card
- Browse and view generated files

**Option 2: On Filesystem**
```bash
cd generated_projects/[project-id]/
ls -la
cat src/main.py
```

**Option 3: Via API**
```bash
# List files
curl http://localhost:8000/api/v1/projects/[id]/files | jq

# Read a file
curl http://localhost:8000/api/v1/projects/[id]/files/src/main.py | jq
```

---

## 🛑 Stop Services

```bash
# Kill backend and frontend
lsof -ti:8000,3000 | xargs kill

# Or use stop script (if available)
./scripts/stop-local.sh
```

---

## 📚 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user manual (A to Z)
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Full API reference
- **[README.md](README.md)** - Project overview
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database schema

---

## ❓ Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process if needed
kill -9 $(lsof -ti:8000)

# Check backend logs
tail -f logs/backend.log  # If log directory exists

# Try manual start
python3 -m uvicorn yago.web.backend.main:app --reload --port 8000
```

### Frontend won't start

```bash
# Check if port 3000 is already in use
lsof -i :3000

# Kill the process if needed
kill -9 $(lsof -ti:3000)

# Reinstall dependencies
cd yago/web/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database errors

```bash
# Reset database
rm yago.db

# Reinitialize migrations
alembic upgrade head
```

### API key not working

1. Check `.env` file exists in project root
2. Verify no extra spaces in API keys
3. Restart backend after changing `.env`
4. Test API key:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Import errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version (must be 3.11+)
python3 --version
```

---

## 📊 What's Working?

After following this guide, you should have:

- ✅ Backend API running on port 8000
- ✅ Frontend dashboard on port 3000
- ✅ Database initialized (SQLite)
- ✅ All AI providers configured
- ✅ Real code generation working
- ✅ Project management working
- ✅ Clarification sessions working

**Test it**: Create a project and execute code generation!

---

## 🎓 Next Steps

1. **Read the User Guide**: [USER_GUIDE.md](USER_GUIDE.md) for complete instructions
2. **Explore API Docs**: http://localhost:8000/docs for interactive API testing
3. **Try Different Depths**: Test minimal, standard, and full clarification modes
4. **Check Generated Code**: View the production-ready code in `generated_projects/`
5. **Explore Analytics**: Check the "📊 Analytics" tab in dashboard

---

## 💡 Tips

- **Use Standard Depth**: Best balance of questions vs. quality
- **Be Specific**: More details in answers = better code
- **Try Multiple Projects**: Each takes only 5-10 minutes
- **Check Costs**: Monitor the "💰 Cost Tracking" in Analytics tab
- **View Files**: Generated code is in `generated_projects/[project-id]/`

---

**Ready to build? Let's go! 🚀**

---

<p align="center">
  <b>YAGO v8.0 - Quick Start Guide</b><br>
  Built with ❤️ by Mikail Lekesiz and Claude AI
</p>
