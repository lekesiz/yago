# YAGO v7.0 - Quick Start Guide

Get started with YAGO v7.0 enhanced features in 5 minutes!

---

## 🚀 Quick Example

### Example 1: E-commerce Site (Auto Mode - Fastest)

```bash
cd /Users/mikail/Desktop/YAGO/yago

python main.py --idea "E-commerce site with Stripe payment" \
  --mode enhanced \
  --clarification-depth auto \
  --approval-mode professional
```

**What happens:**
- ✅ AI infers requirements automatically (no questions)
- ✅ Creates 7 agents (5 base + SecurityAgent + DevOpsAgent)
- ✅ Builds complete e-commerce project
- ✅ Super Admin monitors everything
- ⏱️ ~5-10 minutes

---

### Example 2: Dashboard (Interactive Mode - Full Control)

```bash
python main.py --idea "Analytics dashboard" \
  --mode enhanced \
  --clarification-depth full \
  --approval-mode interactive
```

**What happens:**
- 📋 Asks 8-12 clarification questions
- 🤖 Creates agents based on answers
- 🎯 Asks approval for major decisions
- ⏱️ ~3 minutes clarification + 5-10 minutes execution

---

### Example 3: Simple API (Minimal Questions)

```bash
python main.py --idea "REST API for user management" \
  --mode enhanced \
  --clarification-depth minimal \
  --approval-mode professional
```

**What happens:**
- 📋 Asks only 4-5 essential questions
- 🤖 Creates 5-6 agents
- ✅ Fully automated execution
- ⏱️ ~1 minute clarification + 3-5 minutes execution

---

## 📊 Mode Comparison

| Feature | minimal | full | **enhanced (v7.0)** |
|---------|---------|------|---------------------|
| Clarification | ❌ None | ❌ None | ✅ Intelligent Q&A |
| Dynamic Agents | ❌ Fixed 5 | ✅ Fixed 5 | ✅ 5-10 (adaptive) |
| Supervision | ❌ None | ❌ None | ✅ Super Admin |
| Quality Gates | ❌ None | ⚠️ Basic | ✅ Automated |
| Cost | $ | $$ | $$ (optimized) |
| Duration | 2-3 min | 5-8 min | 5-10 min |

---

## 🎯 Clarification Depth Options

### 1. `--clarification-depth full` (Default)
**Best for:** New projects, complex requirements

```bash
--clarification-depth full
```

**Questions asked:** 8-12 questions
- Tech stack (language, frontend, backend, database)
- Project scope (features, integrations)
- Infrastructure (deployment, CI/CD)
- Quality standards (tests, docs)

**Example output:**
```
🤖 YAGO: What programming language do you prefer?
   1. Python
   2. JavaScript
   3. TypeScript
   4. Go
   5. Other
>>> Your answer: 1

🤖 YAGO: Frontend framework?
   1. React
   2. Vue
   3. Next.js
   4. Angular
   5. None
>>> Your answer: 3

... (6-10 more questions)
```

---

### 2. `--clarification-depth minimal`
**Best for:** Quick prototypes, simple projects

```bash
--clarification-depth minimal
```

**Questions asked:** 4-5 questions
- Language & main framework
- Database
- Deployment method

**Example:**
```
🤖 YAGO: Tech stack? (Python+FastAPI / Node+Express / Go)
>>> Your answer: Python+FastAPI

🤖 YAGO: Database? (PostgreSQL / MongoDB)
>>> Your answer: PostgreSQL

... (2-3 more questions)
```

---

### 3. `--clarification-depth auto`
**Best for:** Well-defined inputs, urgent projects

```bash
--clarification-depth auto
```

**Questions asked:** 0 (AI infers everything)

**Example:**
```
🤖 YAGO: Analyzing input... ✓
🤖 YAGO: Inferred tech stack: Next.js + FastAPI + PostgreSQL
🤖 YAGO: Payment: Stripe (detected from input)
🤖 YAGO: Proceeding with auto-generated brief...
```

---

## 🤝 Approval Mode Options

### 1. `--approval-mode professional` (Default)
**Best for:** Experienced users, production projects

```bash
--approval-mode professional
```

**Behavior:**
- ✅ Fully automated
- ✅ Auto-fixes issues (test coverage, missing docs)
- ✅ No interruptions
- 📊 Final report only

**Example:**
```
⚠️ Test coverage 65% < 80%
🛠️ Auto-fix: Instructed Tester to complete missing tests
✅ Coverage now 92%
```

---

### 2. `--approval-mode standard`
**Best for:** Learning, monitoring

```bash
--approval-mode standard
```

**Behavior:**
- ⚠️ Notifies user of issues
- ❌ Does NOT auto-fix
- 📊 Real-time progress updates

**Example:**
```
⚠️ [MEDIUM] Documentation 85% < 90%
   Agent: Documenter | Action: User review recommended
```

---

### 3. `--approval-mode interactive`
**Best for:** Critical projects, full control

```bash
--approval-mode interactive
```

**Behavior:**
- ❓ Asks user for major decisions
- 🛡️ Escalates security issues
- 📊 Detailed progress reports

**Example:**
```
🤖 YAGO: Security issue detected: Hardcoded API key
   Options:
   1. Auto-fix (use environment variable)
   2. Skip for now
   3. Abort
>>> Your choice: 1
```

---

## 📁 Output Structure

After running YAGO v7.0:

```
workspace/
├── .clarifications/
│   └── ecommerce_20251027_143022.json    # Project brief
├── your_project/
│   ├── backend/                          # Generated code
│   ├── frontend/
│   ├── tests/
│   ├── docs/
│   └── README.md
└── reports/
    ├── ecommerce_20251027_admin_report.html   # Super Admin report
    └── ecommerce_20251027_summary.json        # Metrics
```

---

## 🧪 Testing v7.0

### Test ClarificationAgent
```bash
cd /Users/mikail/Desktop/YAGO/yago

python -m pytest tests/v7.0/test_clarification.py -v
```

### Test DynamicRoleManager
```bash
python -m pytest tests/v7.0/test_dynamic_roles.py -v
```

### Test Super Admin
```bash
python core/super_admin.py
```

### Standalone Clarification Test
```bash
python agents/clarification_agent.py "E-commerce site with payment"
```

---

## 💡 Real-World Examples

### Example 1: Startup MVP (Professional Mode)
```bash
python main.py \
  --idea "SaaS platform for project management with team collaboration, Stripe billing, and Slack integration" \
  --mode enhanced \
  --clarification-depth auto \
  --approval-mode professional
```

**Result:**
- 🤖 9 agents created (including SecurityAgent, APIDesignAgent, DevOpsAgent)
- 💰 Est. cost: $3.50
- ⏱️ Duration: ~8 minutes
- ✅ Production-ready code

---

### Example 2: Client Project (Interactive Mode)
```bash
python main.py \
  --idea "Healthcare appointment booking system" \
  --mode enhanced \
  --clarification-depth full \
  --approval-mode interactive
```

**Result:**
- 📋 12 clarification questions
- 🤖 8 agents (including SecurityAgent for HIPAA compliance)
- 🔒 User approval for security decisions
- ⏱️ ~12 minutes total

---

### Example 3: Internal Tool (Minimal)
```bash
python main.py \
  --idea "CLI tool to backup PostgreSQL databases to S3" \
  --mode enhanced \
  --clarification-depth minimal \
  --approval-mode professional
```

**Result:**
- 📋 5 questions
- 🤖 6 agents (base 5 + DevOpsAgent)
- ⏱️ ~4 minutes
- ✅ Ready to use

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'agents.clarification_agent'"

**Solution:**
```bash
cd /Users/mikail/Desktop/YAGO/yago
python -m pip install -r requirements.txt
```

---

### Issue: Clarification agent not asking questions

**Cause:** Using `--clarification-depth auto`

**Solution:** Use `full` or `minimal` for interactive questions
```bash
--clarification-depth full
```

---

### Issue: Too many agents created (high cost)

**Solution:** Limit dynamic agents in config:
```bash
# Edit yago_config.yaml
dynamic_roles:
  max_agents: 3  # Default: 5
  cost_limit: 5.0  # Default: 10.0
```

---

### Issue: Super Admin not intervening

**Cause:** Thresholds too low or no issues detected

**Solution:** Check thresholds in code or logs:
```python
# core/super_admin.py
thresholds = {
    "test_coverage": 0.80,    # Adjust here
    "doc_completeness": 0.90,
}
```

---

## 📞 Getting Help

- **Documentation:** `docs/v7.0/OVERVIEW.md`
- **Issues:** https://github.com/lekesiz/yago/issues
- **Discussions:** https://github.com/lekesiz/yago/discussions

---

## 🎉 You're Ready!

Start with a simple example:

```bash
python main.py --idea "Todo API with FastAPI" --mode enhanced
```

YAGO v7.0 will guide you through the rest! 🚀
