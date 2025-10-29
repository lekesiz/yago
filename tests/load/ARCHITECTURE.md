# YAGO v8.1 Load Testing Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Testing System                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌──────────────────┐      ┌──────────────┐
│  Test Runner    │      │  Locust Master   │      │  YAGO API    │
│  (run_tests.sh) │─────▶│  (locustfile.py) │─────▶│  (api.py)    │
└─────────────────┘      └──────────────────┘      └──────────────┘
         │                        │                         │
         │                        │                         │
         ▼                        ▼                         ▼
┌─────────────────┐      ┌──────────────────┐      ┌──────────────┐
│  Results Dir    │      │  Metrics Tracker │      │  Database    │
│  - HTML         │      │  - Response Time │      │  - Projects  │
│  - CSV          │      │  - Error Rate    │      │  - State     │
│  - Logs         │      │  - RPS           │      │              │
└─────────────────┘      └──────────────────┘      └──────────────┘
```

## Test Flow

```
1. Test Initialization
   ├── Load locustfile.py
   ├── Initialize metrics tracker
   ├── Connect to YAGO API
   └── Create test data generators

2. User Spawning
   ├── Create virtual users
   ├── Assign tasks based on weights
   ├── Set wait times
   └── Start execution

3. Test Execution
   ├── Execute user tasks
   │   ├── List projects
   │   ├── Create projects
   │   ├── View details
   │   ├── Check status
   │   └── List templates
   ├── Collect metrics
   ├── Track errors
   └── Update real-time stats

4. Results Generation
   ├── Aggregate statistics
   ├── Generate HTML reports
   ├── Export CSV data
   ├── Create summary
   └── Archive results
```

## User Task Execution Flow

```
┌────────────────────────────────────────────────────────────┐
│                     YAGOUser (Base)                         │
├────────────────────────────────────────────────────────────┤
│  Tasks:                                                     │
│  ┌─────────────────────────────────────────────┐          │
│  │ health_check()           [weight: 1]        │          │
│  │ get_status()             [weight: 4]        │          │
│  │ list_templates()         [weight: 3]        │          │
│  │ list_projects()          [weight: 5]        │          │
│  │ create_project()         [weight: 2]        │          │
│  │ get_project_detail()     [weight: 3]        │          │
│  └─────────────────────────────────────────────┘          │
└────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ NormalLoadUser│  │ SpikeLoadUser │  │ StressTestUser│
│ wait: 2-5s    │  │ wait: 1-2s    │  │ wait: 0.5-1.5s│
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│              YAGO Backend API                        │
│  GET  /                                              │
│  GET  /api/status                                    │
│  GET  /api/templates                                 │
│  GET  /api/projects                                  │
│  POST /api/projects                                  │
│  GET  /api/projects/{id}                             │
└─────────────────────────────────────────────────────┘
```

## Test Scenarios Timeline

### Scenario 1: Normal Load
```
Time:    0s ────────────────────── 300s (5 min)
Users:   10 ──────────────────────── 10
Load:    ████████████████████████████ (steady)
```

### Scenario 2: Spike Load
```
Time:    0s ─ 10s ─ 70s ──── 190s ── 220s
Users:   10 ─ 10 ─ 100 ──── 100 ─── 10
Load:    ███▲▲▲▲████████████████▼▼▼██
         [Base][Spike][Hold][Recovery]
```

### Scenario 3: Stress Test
```
Time:    0s ── 60s ── 120s ── 180s ── 240s ── 300s
Users:   50 ── 100 ── 150 ── 200 ── 250 ── 250
Load:    ██▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲████
         [Gradual increase to breaking point]
```

### Scenario 4: Endurance Test
```
Time:    0s ───────────────────────────────── 1800s (30 min)
Users:   50 ────────────────────────────────── 50
Load:    ██████████████████████████████████████████ (sustained)
Monitor: Memory, Connections, Response Time Drift
```

## Data Flow

```
┌──────────────┐
│ Test Request │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Locust Request   │
│ - Method         │
│ - URL            │
│ - Payload        │
│ - Headers        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ YAGO API         │
│ - Route Handler  │
│ - Business Logic │
│ - Database Query │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Response         │
│ - Status Code    │
│ - Data           │
│ - Time           │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Metrics Tracker  │
│ - Record Time    │
│ - Track Errors   │
│ - Update Stats   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Report Generator │
│ - HTML Report    │
│ - CSV Export     │
│ - Summary Stats  │
└──────────────────┘
```

## Metrics Collection

```
┌─────────────────────────────────────────────────────────┐
│                  Metrics Tracker                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Per Request:                                           │
│  ┌────────────────────────────────────────┐            │
│  │ • Request Type (GET/POST)              │            │
│  │ • Endpoint Name                        │            │
│  │ • Response Time (ms)                   │            │
│  │ • Response Length (bytes)              │            │
│  │ • Success/Failure                      │            │
│  │ • Exception Details (if any)           │            │
│  └────────────────────────────────────────┘            │
│                                                          │
│  Aggregated:                                            │
│  ┌────────────────────────────────────────┐            │
│  │ • Total Requests                       │            │
│  │ • Successful Requests                  │            │
│  │ • Failed Requests                      │            │
│  │ • Error Rate (%)                       │            │
│  │ • Average Response Time                │            │
│  │ • P50, P95, P99 Response Times         │            │
│  │ • Requests Per Second (RPS)            │            │
│  │ • Projects Created Count               │            │
│  └────────────────────────────────────────┘            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Report Generation Process

```
┌────────────────────────────────────────────────┐
│           run_tests.sh Workflow                 │
├────────────────────────────────────────────────┤
│                                                 │
│  1. Pre-flight Checks                          │
│     ├── Check backend availability             │
│     ├── Verify dependencies                    │
│     └── Create results directory               │
│                                                 │
│  2. Execute Scenario                           │
│     ├── Run locust with parameters             │
│     ├── Capture stdout/stderr to log           │
│     ├── Generate HTML report                   │
│     └── Export CSV data                        │
│                                                 │
│  3. Post-processing                            │
│     ├── Parse log files                        │
│     ├── Extract key metrics                    │
│     ├── Compare against targets                │
│     └── Generate summary markdown              │
│                                                 │
│  4. Archive Results                            │
│     ├── Create timestamped directory           │
│     ├── Organize files (html/csv/logs)         │
│     └── Create tar.gz archive                  │
│                                                 │
└────────────────────────────────────────────────┘
```

## Performance Target Validation

```
┌──────────────────────────────────────────────────┐
│         Performance Validation Logic              │
├──────────────────────────────────────────────────┤
│                                                   │
│  After Test Completion:                          │
│                                                   │
│  1. Response Time Check                          │
│     IF P95 < 200ms → ✅ PASS                     │
│     ELSE → ❌ FAIL                                │
│                                                   │
│  2. P99 Response Time Check                      │
│     IF P99 < 500ms → ✅ PASS                     │
│     ELSE → ❌ FAIL                                │
│                                                   │
│  3. Error Rate Check                             │
│     IF Normal Load: error_rate < 1% → ✅ PASS    │
│     IF Stress Test: error_rate < 5% → ✅ PASS    │
│     ELSE → ❌ FAIL                                │
│                                                   │
│  4. Overall Result                               │
│     IF all checks PASS → ✅ READY FOR PRODUCTION │
│     ELSE → ❌ OPTIMIZATION NEEDED                 │
│                                                   │
└──────────────────────────────────────────────────┘
```

## Load Shape Implementation

```
LoadTestShape Class
│
├─ tick() method (called every second)
│  │
│  ├─ Get current run_time
│  │
│  ├─ Iterate through stages
│  │  │
│  │  ├─ IF run_time < stage.duration
│  │  │  └─ RETURN (users, spawn_rate)
│  │  │
│  │  └─ ELSE continue to next stage
│  │
│  └─ IF all stages complete
│     └─ RETURN None (stop test)
│
└─ Stages Configuration
   │
   ├─ Stage 1: {duration: 60s, users: 10, spawn_rate: 2}
   ├─ Stage 2: {duration: 120s, users: 50, spawn_rate: 5}
   └─ Stage N: {duration: Xs, users: Y, spawn_rate: Z}
```

## File Organization

```
tests/load/
│
├── Core Files
│   ├── locustfile.py          # Test definitions
│   ├── requirements.txt       # Dependencies
│   ├── run_tests.sh          # Automation script
│   ├── setup.sh              # Setup script
│   └── .gitignore            # Git ignore rules
│
├── Documentation
│   ├── README.md             # Complete guide
│   ├── QUICK_START.md        # Quick reference
│   ├── IMPLEMENTATION_SUMMARY.md  # Technical summary
│   ├── LOAD_TEST_RESULTS.md  # Results template
│   └── ARCHITECTURE.md       # This file
│
└── Generated (runtime)
    └── results/
        └── YYYYMMDD_HHMMSS/
            ├── html/         # HTML reports
            ├── csv/          # CSV data
            ├── logs/         # Execution logs
            ├── SUMMARY.md    # Auto-generated summary
            └── archive.tar.gz # Compressed archive
```

## Integration Points

```
┌────────────────────────────────────────────────────┐
│              System Integration                     │
├────────────────────────────────────────────────────┤
│                                                     │
│  1. YAGO Backend API (FastAPI)                     │
│     └── Tests: All REST endpoints                  │
│                                                     │
│  2. Database                                        │
│     └── Tests: Read/write performance              │
│                                                     │
│  3. WebSocket (future)                             │
│     └── Tests: Real-time updates                   │
│                                                     │
│  4. External APIs (future)                         │
│     └── Tests: Third-party integration latency     │
│                                                     │
│  5. File Storage (future)                          │
│     └── Tests: Upload/download throughput          │
│                                                     │
└────────────────────────────────────────────────────┘
```

## Monitoring Points

```
During Test Execution:

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Client Side    │  │  Network        │  │  Server Side    │
│  (Locust)       │  │                 │  │  (YAGO API)     │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Spawn Rate    │  │ • Latency       │  │ • CPU Usage     │
│ • Active Users  │  │ • Throughput    │  │ • Memory Usage  │
│ • RPS           │  │ • Packet Loss   │  │ • Disk I/O      │
│ • Response Time │  │ • Connection    │  │ • DB Conns      │
│ • Error Count   │  │   Errors        │  │ • Thread Pool   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Scaling Strategy

```
┌─────────────────────────────────────────────────────────┐
│              Horizontal Scaling Model                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   Load Balancer (Nginx/HAProxy)                         │
│         │                                                │
│         ├─────────────────┬──────────────────┐          │
│         │                 │                  │          │
│         ▼                 ▼                  ▼          │
│   ┌─────────┐       ┌─────────┐       ┌─────────┐      │
│   │ YAGO #1 │       │ YAGO #2 │       │ YAGO #3 │      │
│   │ 100 usr │       │ 100 usr │       │ 100 usr │      │
│   └────┬────┘       └────┬────┘       └────┬────┘      │
│        │                 │                  │          │
│        └─────────────────┴──────────────────┘          │
│                          │                              │
│                          ▼                              │
│                   ┌──────────────┐                      │
│                   │  Database    │                      │
│                   │  (Shared)    │                      │
│                   └──────────────┘                      │
│                                                          │
│  Capacity: 300 concurrent users                         │
│  Redundancy: 2x (if 1 instance fails)                   │
│  Scaling: Add more instances as needed                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Why Locust?
- Modern Python-based framework
- Easy to write realistic user behavior
- Excellent reporting and real-time monitoring
- Distributed testing support
- Active community and good documentation

### 2. Test Scenario Choices
- **Normal**: Establishes baseline
- **Spike**: Tests elasticity and recovery
- **Stress**: Finds system limits
- **Endurance**: Detects long-term issues

### 3. Metrics Selection
- Focus on user-facing metrics (response time, errors)
- Include system health metrics (CPU, memory)
- Track business metrics (projects created)
- Enable comparison and trend analysis

### 4. Automation Approach
- Single script runs all scenarios
- Automatic result aggregation
- Built-in performance validation
- CI/CD ready

---

**Last Updated**: 2025-10-29
**Version**: 1.0.0
