# YAGO v8.1 Load Testing Suite

Comprehensive load testing framework for YAGO backend using Locust.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Test Scenarios](#test-scenarios)
- [Usage](#usage)
- [Performance Targets](#performance-targets)
- [Results Analysis](#results-analysis)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## Overview

This load testing suite provides comprehensive performance testing for the YAGO v8.1 backend API. It includes multiple test scenarios designed to evaluate system performance under various load conditions.

### Features

- **4 Test Scenarios**: Normal, Spike, Stress, and Endurance tests
- **Automated Execution**: Run all tests with a single command
- **Comprehensive Reporting**: HTML reports, CSV data, and summary analytics
- **Custom Metrics**: Track response times, error rates, and RPS
- **Performance Validation**: Automatic comparison against targets
- **Realistic Workloads**: Simulates actual user behavior patterns

### Test Architecture

```
tests/load/
├── locustfile.py          # Main test scenarios and user classes
├── requirements.txt       # Python dependencies
├── run_tests.sh          # Automated test execution script
├── README.md             # This file
├── LOAD_TEST_RESULTS.md  # Results template and documentation
└── results/              # Test results (generated)
    └── YYYYMMDD_HHMMSS/
        ├── html/         # HTML reports
        ├── csv/          # CSV data files
        ├── logs/         # Execution logs
        └── SUMMARY.md    # Aggregated results
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- YAGO backend server running
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
cd tests/load
pip install -r requirements.txt
```

This installs:
- `locust` - Load testing framework
- `faker` - Test data generation
- `pandas`, `numpy` - Data analysis
- `matplotlib`, `seaborn` - Visualization
- Other utilities

### Step 2: Verify Installation

```bash
locust --version
```

You should see: `locust 2.20.0` or similar.

### Step 3: Start YAGO Backend

Before running tests, ensure the backend is running:

```bash
# In a separate terminal
cd /Users/mikail/Desktop/YAGO/yago/web/backend
python api.py
```

Backend should be accessible at: `http://localhost:8000`

---

## Quick Start

### Option 1: Automated Test Suite (Recommended)

Run all test scenarios automatically:

```bash
./run_tests.sh all http://localhost:8000
```

This will:
1. Check backend availability
2. Run all 4 test scenarios sequentially
3. Generate HTML reports and CSV data
4. Create a comprehensive summary report
5. Archive results for future reference

### Option 2: Single Scenario

Run a specific scenario:

```bash
# Normal load test (5 minutes)
./run_tests.sh normal http://localhost:8000

# Spike load test (3 minutes)
./run_tests.sh spike http://localhost:8000

# Stress test (5 minutes)
./run_tests.sh stress http://localhost:8000

# Quick test (30 seconds) - for development
./run_tests.sh quick http://localhost:8000
```

### Option 3: Interactive Web UI

Launch Locust with web interface:

```bash
locust -f locustfile.py --host=http://localhost:8000
```

Then open: `http://localhost:8089`

Configure users, spawn rate, and duration in the web UI.

---

## Test Scenarios

### Scenario 1: Normal Load Test

**Purpose**: Simulate typical production load
**Duration**: 5 minutes
**Users**: 10 concurrent users
**Spawn Rate**: 2 users/second

**User Behavior**:
- List projects (weight: 5)
- View project details (weight: 3)
- Create projects (weight: 2)
- Check status (weight: 4)
- List templates (weight: 3)

**Expected Results**:
- 0% error rate
- P95 response time < 200ms
- P99 response time < 500ms

**Run Command**:
```bash
locust -f locustfile.py --host=http://localhost:8000 \
       --users 10 --spawn-rate 2 --run-time 5m \
       --headless NormalLoadUser
```

---

### Scenario 2: Spike Load Test

**Purpose**: Test system behavior under sudden traffic spikes
**Duration**: 3 minutes
**Users**: 10 → 100 users (ramp in 1 minute)
**Spawn Rate**: 10 users/second during spike

**Load Pattern**:
1. Start: 10 users (10 seconds)
2. Spike: Ramp to 100 users (1 minute)
3. Hold: 100 users (2 minutes)
4. Ramp down: Back to 10 users

**Expected Results**:
- < 5% error rate during spike
- System recovers quickly after spike
- No permanent degradation

**Run Command**:
```bash
locust -f locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 3m \
       --headless SpikeLoadUser
```

---

### Scenario 3: Stress Test

**Purpose**: Find system breaking point
**Duration**: 5 minutes
**Users**: 50 → 250 users (gradual increase)
**Spawn Rate**: 5 users/second

**Load Pattern**:
- 0-1 min: 50 users
- 1-2 min: 100 users
- 2-3 min: 150 users
- 3-4 min: 200 users
- 4-5 min: 250 users

**What to Monitor**:
- At what user count do errors start?
- Response time degradation curve
- Database connection pool saturation
- Memory usage growth

**Run Command**:
```bash
locust -f locustfile.py --host=http://localhost:8000 \
       --users 200 --spawn-rate 10 --run-time 5m \
       --headless StressTestUser
```

---

### Scenario 4: Endurance Test

**Purpose**: Detect memory leaks and resource exhaustion
**Duration**: 30 minutes (configurable)
**Users**: 50 concurrent users
**Spawn Rate**: 5 users/second

**What to Monitor**:
- Memory usage over time
- Response time drift
- Connection pool health
- Database performance degradation

**Run Command**:
```bash
locust -f locustfile.py --host=http://localhost:8000 \
       --users 50 --spawn-rate 5 --run-time 30m \
       --headless EnduranceTestUser
```

---

## Performance Targets

### Response Time Targets

| Metric | Target | Critical |
|--------|--------|----------|
| P50 (Median) | < 100ms | < 150ms |
| P95 | < 200ms | < 300ms |
| P99 | < 500ms | < 800ms |
| Average | < 150ms | < 250ms |

### Error Rate Targets

| Load Type | Target | Critical |
|-----------|--------|----------|
| Normal Load | 0% | < 1% |
| Spike Load | < 2% | < 5% |
| Stress Test | < 5% | < 10% |

### Throughput Targets

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| RPS (Requests/sec) | 10 | 50 | 100+ |
| Projects Created/min | 5 | 20 | 50+ |

---

## Usage

### Basic Commands

```bash
# Run with web UI (recommended for development)
locust -f locustfile.py --host=http://localhost:8000

# Run headless (recommended for CI/CD)
locust -f locustfile.py --host=http://localhost:8000 \
       --users 10 --spawn-rate 2 --run-time 5m --headless

# Run with HTML report
locust -f locustfile.py --host=http://localhost:8000 \
       --users 10 --spawn-rate 2 --run-time 5m \
       --headless --html=report.html

# Run with CSV output
locust -f locustfile.py --host=http://localhost:8000 \
       --users 10 --spawn-rate 2 --run-time 5m \
       --headless --csv=results
```

### Advanced Options

```bash
# Run specific user class
locust -f locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 StressTestUser

# Run with custom tags (only health and status endpoints)
locust -f locustfile.py --host=http://localhost:8000 \
       --users 10 --tags health status

# Exclude specific tags
locust -f locustfile.py --host=http://localhost:8000 \
       --users 10 --exclude-tags create

# Run in distributed mode (master)
locust -f locustfile.py --master --expect-workers=4

# Run in distributed mode (worker)
locust -f locustfile.py --worker --master-host=localhost
```

### Automated Script Options

```bash
# Run all scenarios
./run_tests.sh all http://localhost:8000

# Run specific scenario
./run_tests.sh normal http://localhost:8000
./run_tests.sh spike http://localhost:8000
./run_tests.sh stress http://localhost:8000
./run_tests.sh endurance http://localhost:8000

# Quick test (30 seconds)
./run_tests.sh quick http://localhost:8000

# Test against staging server
./run_tests.sh all https://yago-staging.example.com
```

---

## Results Analysis

### Understanding HTML Reports

After running tests, open the HTML report:

```bash
open results/YYYYMMDD_HHMMSS/html/scenario_name.html
```

The report includes:
- **Statistics**: Request counts, failure rates, response times
- **Charts**: Response time distribution, RPS over time
- **Percentiles**: P50, P75, P90, P95, P99 response times
- **Failures**: Detailed error messages

### Reading CSV Data

Three CSV files are generated per test:
- `scenario_stats.csv` - Request statistics
- `scenario_stats_history.csv` - Time-series data
- `scenario_failures.csv` - Failed requests

Example analysis with pandas:

```python
import pandas as pd

# Load statistics
stats = pd.read_csv('results/YYYYMMDD_HHMMSS/csv/scenario_stats.csv')

# Calculate average response time
avg_response = stats['Average Response Time'].mean()
print(f"Average Response Time: {avg_response}ms")

# Load time-series data
history = pd.read_csv('results/YYYYMMDD_HHMMSS/csv/scenario_stats_history.csv')

# Plot RPS over time
import matplotlib.pyplot as plt
plt.plot(history['Timestamp'], history['Requests/s'])
plt.xlabel('Time')
plt.ylabel('Requests per Second')
plt.title('RPS Over Time')
plt.show()
```

### Summary Report

The automated script generates a comprehensive summary:

```bash
cat results/YYYYMMDD_HHMMSS/SUMMARY.md
```

This includes:
- Test configuration and duration
- Key metrics for each scenario
- Performance target validation
- Recommendations for optimization

---

## Troubleshooting

### Issue: Backend Not Accessible

**Error**: `Backend is not accessible at http://localhost:8000`

**Solutions**:
1. Ensure backend is running:
   ```bash
   cd /Users/mikail/Desktop/YAGO/yago/web/backend
   python api.py
   ```
2. Check if port 8000 is in use:
   ```bash
   lsof -i :8000
   ```
3. Try a different port:
   ```bash
   ./run_tests.sh all http://localhost:8001
   ```

---

### Issue: High Error Rate

**Symptoms**: Error rate > 5%

**Common Causes**:
1. **Backend overload**: Reduce concurrent users
2. **Database connection limits**: Increase pool size
3. **Timeout issues**: Increase request timeout
4. **Resource exhaustion**: Monitor CPU/memory

**Investigation**:
```bash
# Check backend logs
tail -f yago/web/backend/logs/api.log

# Monitor system resources
top -p $(pgrep -f "python api.py")

# Check database connections
# (depends on your database)
```

---

### Issue: Slow Response Times

**Symptoms**: P95 > 200ms or P99 > 500ms

**Common Causes**:
1. **Database queries**: Add indexes, optimize queries
2. **External API calls**: Add caching, use async
3. **CPU-intensive operations**: Use background tasks
4. **Network latency**: Check network configuration

**Profiling**:
```python
# Add profiling to backend
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your endpoint code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

---

### Issue: Memory Leaks (Endurance Test)

**Symptoms**: Memory usage grows continuously

**Detection**:
```bash
# Monitor memory during test
while true; do
    ps aux | grep "python api.py" | grep -v grep | awk '{print $6}'
    sleep 10
done
```

**Solutions**:
1. **Close connections**: Ensure proper cleanup
2. **Clear caches**: Implement cache eviction
3. **Fix circular references**: Use weak references
4. **Profile memory**: Use `pympler` or `memory_profiler`

---

### Issue: Locust Installation Fails

**Error**: `pip install locust` fails

**Solutions**:
1. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```
2. Use virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Install system dependencies (Ubuntu):
   ```bash
   sudo apt-get install python3-dev build-essential
   ```

---

## Advanced Usage

### Custom Load Shapes

Create custom load patterns by defining a `LoadTestShape` class:

```python
from locust import LoadTestShape

class CustomLoadShape(LoadTestShape):
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},
        {"duration": 120, "users": 50, "spawn_rate": 5},
        {"duration": 180, "users": 20, "spawn_rate": 5},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None
```

Run with:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

### Distributed Load Testing

For very high loads, run Locust in distributed mode:

**Start Master**:
```bash
locust -f locustfile.py --master --expect-workers=4
```

**Start Workers** (on same or different machines):
```bash
# Worker 1
locust -f locustfile.py --worker --master-host=localhost

# Worker 2
locust -f locustfile.py --worker --master-host=localhost

# Worker 3
locust -f locustfile.py --worker --master-host=localhost

# Worker 4
locust -f locustfile.py --worker --master-host=localhost
```

Access master UI: `http://localhost:8089`

---

### Custom Metrics and Monitoring

Integrate with monitoring systems:

```python
from locust import events
import statsd

# Send metrics to StatsD
stats_client = statsd.StatsClient('localhost', 8125)

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    stats_client.timing(f'locust.{name}', response_time)
    if exception:
        stats_client.incr(f'locust.{name}.error')
```

---

### Integration with CI/CD

**GitHub Actions Example**:

```yaml
name: Load Test

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd tests/load
          pip install -r requirements.txt

      - name: Start backend
        run: |
          cd yago/web/backend
          python api.py &
          sleep 10

      - name: Run load tests
        run: |
          cd tests/load
          ./run_tests.sh quick http://localhost:8000

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: tests/load/results/
```

---

## Best Practices

### 1. Test Environment

- Use a dedicated test environment
- Mirror production configuration
- Isolate from other services
- Use realistic data volumes

### 2. Test Data

- Generate realistic payloads
- Vary request parameters
- Clean up test data after runs
- Don't hardcode values

### 3. Monitoring

- Monitor backend during tests
- Track database performance
- Watch system resources
- Log errors comprehensively

### 4. Analysis

- Compare results over time
- Identify trends and regressions
- Document findings
- Share results with team

### 5. Continuous Testing

- Automate in CI/CD
- Run regularly (daily/weekly)
- Alert on regressions
- Track improvements

---

## Resources

### Documentation
- [Locust Documentation](https://docs.locust.io/)
- [Performance Testing Guide](https://www.perfmatrix.com/performance-testing-guide/)
- [Load Testing Best Practices](https://k6.io/docs/testing-guides/load-testing/)

### Tools
- [Grafana](https://grafana.com/) - Visualization
- [Prometheus](https://prometheus.io/) - Metrics
- [Jaeger](https://www.jaegertracing.io/) - Tracing

### Community
- [Locust GitHub](https://github.com/locustio/locust)
- [Locust Slack](https://locust-io.slack.com/)

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Locust documentation
3. Open an issue in the YAGO repository
4. Contact the development team

---

## License

This load testing suite is part of the YAGO project.

---

**Last Updated**: 2025-10-29
**Version**: 1.0.0
**Author**: YAGO Team
