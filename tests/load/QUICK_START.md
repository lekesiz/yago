# YAGO v8.1 Load Testing - Quick Start Guide

## Setup (One-time)

```bash
cd /Users/mikail/Desktop/YAGO/tests/load
./setup.sh
```

## Start Backend (Required)

```bash
# In a separate terminal
cd /Users/mikail/Desktop/YAGO/yago/web/backend
python api.py
```

## Run Tests

### Quick Test (30 seconds)
```bash
./run_tests.sh quick http://localhost:8000
```

### All Scenarios (~45 minutes)
```bash
./run_tests.sh all http://localhost:8000
```

### Individual Scenarios
```bash
./run_tests.sh normal http://localhost:8000      # 5 min
./run_tests.sh spike http://localhost:8000       # 3 min
./run_tests.sh stress http://localhost:8000      # 5 min
./run_tests.sh endurance http://localhost:8000   # 30 min
```

### Interactive Web UI
```bash
locust -f locustfile.py --host=http://localhost:8000
# Open: http://localhost:8089
```

## View Results

```bash
# Latest results
ls -lt results/ | head -2

# View summary
cat results/YYYYMMDD_HHMMSS/SUMMARY.md

# Open HTML reports
open results/YYYYMMDD_HHMMSS/html/*.html
```

## Test Scenarios

| Scenario | Users | Duration | Purpose |
|----------|-------|----------|---------|
| **Normal** | 10 | 5 min | Baseline performance |
| **Spike** | 10→100 | 3 min | Rapid scaling test |
| **Stress** | 50→250 | 5 min | Find breaking point |
| **Endurance** | 50 | 30 min | Memory leak detection |

## Performance Targets

- ✅ P95 < 200ms
- ✅ P99 < 500ms
- ✅ 0% error rate (normal load)
- ✅ < 5% error rate (stress)

## Troubleshooting

### Backend not accessible?
```bash
curl http://localhost:8000/
# If fails, start backend
```

### Installation issues?
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Need more details?
- See `README.md` for complete guide
- See `IMPLEMENTATION_SUMMARY.md` for technical details
- See `LOAD_TEST_RESULTS.md` for results template

## Files

```
tests/load/
├── locustfile.py          # Test scenarios
├── run_tests.sh          # Automated testing
├── setup.sh              # One-time setup
├── requirements.txt      # Dependencies
├── README.md             # Full documentation
└── results/              # Test results (generated)
```

---

**Quick Commands Reference**

```bash
# Setup
./setup.sh

# Quick test
./run_tests.sh quick http://localhost:8000

# Full test
./run_tests.sh all http://localhost:8000

# Web UI
locust -f locustfile.py --host=http://localhost:8000
```

---

That's it! You're ready to test YAGO's performance.
