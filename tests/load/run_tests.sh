#!/bin/bash

################################################################################
# YAGO v8.1 Load Testing Automation Script
################################################################################
#
# This script automates the execution of all load test scenarios and generates
# comprehensive reports.
#
# Usage:
#   ./run_tests.sh [scenario] [host]
#
# Examples:
#   ./run_tests.sh all http://localhost:8000
#   ./run_tests.sh normal http://localhost:8000
#   ./run_tests.sh spike http://localhost:8000
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
SCENARIO="${1:-all}"
HOST="${2:-http://localhost:8000}"
RESULTS_DIR="./results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_DIR="${RESULTS_DIR}/${TIMESTAMP}"

# Create results directory
mkdir -p "${REPORT_DIR}"
mkdir -p "${REPORT_DIR}/html"
mkdir -p "${REPORT_DIR}/csv"
mkdir -p "${REPORT_DIR}/logs"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_backend() {
    print_info "Checking backend availability at ${HOST}..."

    if curl -s -f "${HOST}/" > /dev/null 2>&1; then
        print_success "Backend is running"
        return 0
    else
        print_error "Backend is not accessible at ${HOST}"
        print_warning "Please start the backend server first:"
        echo "  cd yago/web/backend"
        echo "  python api.py"
        return 1
    fi
}

run_scenario() {
    local scenario_name=$1
    local users=$2
    local spawn_rate=$3
    local duration=$4
    local user_class=$5

    print_header "Running ${scenario_name}"

    local log_file="${REPORT_DIR}/logs/${scenario_name}.log"
    local csv_file="${REPORT_DIR}/csv/${scenario_name}"
    local html_file="${REPORT_DIR}/html/${scenario_name}.html"

    print_info "Configuration:"
    echo "  Users: ${users}"
    echo "  Spawn Rate: ${spawn_rate}/s"
    echo "  Duration: ${duration}"
    echo "  User Class: ${user_class}"
    echo "  Log: ${log_file}"
    echo ""

    # Run locust test
    locust -f locustfile.py \
        --host="${HOST}" \
        --users="${users}" \
        --spawn-rate="${spawn_rate}" \
        --run-time="${duration}" \
        --headless \
        --html="${html_file}" \
        --csv="${csv_file}" \
        ${user_class} \
        2>&1 | tee "${log_file}"

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        print_success "${scenario_name} completed successfully"
        echo ""
        return 0
    else
        print_error "${scenario_name} failed with exit code ${exit_code}"
        echo ""
        return 1
    fi
}

generate_summary_report() {
    print_header "Generating Summary Report"

    local summary_file="${REPORT_DIR}/SUMMARY.md"

    cat > "${summary_file}" << EOF
# YAGO v8.1 Load Test Results Summary

**Test Date**: $(date +"%Y-%m-%d %H:%M:%S")
**Target Host**: ${HOST}
**Test Duration**: $(date -u -d @$SECONDS +"%T")

---

## Test Configuration

### Performance Targets
- 95% of requests < 200ms ✓
- 99% of requests < 500ms ✓
- 0% error rate under normal load ✓
- < 5% error rate under stress ✓

---

## Scenarios Executed

EOF

    # List all executed scenarios
    for log in "${REPORT_DIR}/logs"/*.log; do
        if [ -f "$log" ]; then
            scenario=$(basename "$log" .log)
            echo "### ${scenario}" >> "${summary_file}"
            echo "" >> "${summary_file}"

            # Extract key metrics from log
            if grep -q "Total Requests:" "$log"; then
                echo "**Results:**" >> "${summary_file}"
                grep "Total Requests:" "$log" | tail -1 >> "${summary_file}"
                grep "Error Rate:" "$log" | tail -1 >> "${summary_file}"
                grep "Average Response Time:" "$log" | tail -1 >> "${summary_file}"
                grep "P95 Response Time:" "$log" | tail -1 >> "${summary_file}"
                grep "P99 Response Time:" "$log" | tail -1 >> "${summary_file}"
                grep "RPS:" "$log" | tail -1 >> "${summary_file}"
                echo "" >> "${summary_file}"
            fi

            # HTML report link
            echo "[View Detailed HTML Report](html/${scenario}.html)" >> "${summary_file}"
            echo "" >> "${summary_file}"
            echo "---" >> "${summary_file}"
            echo "" >> "${summary_file}"
        fi
    done

    cat >> "${summary_file}" << EOF

## Files Generated

### HTML Reports
\`\`\`
$(ls -1 ${REPORT_DIR}/html/*.html 2>/dev/null || echo "No HTML reports generated")
\`\`\`

### CSV Data
\`\`\`
$(ls -1 ${REPORT_DIR}/csv/*.csv 2>/dev/null || echo "No CSV data generated")
\`\`\`

### Log Files
\`\`\`
$(ls -1 ${REPORT_DIR}/logs/*.log 2>/dev/null || echo "No log files generated")
\`\`\`

---

## Performance Analysis

### Key Findings

$(python3 << 'PYTHON_EOF'
import os
import re
import glob

report_dir = os.environ.get('REPORT_DIR', './results')
log_files = glob.glob(f"{report_dir}/logs/*.log")

if not log_files:
    print("No log files found for analysis")
    exit()

findings = []

for log_file in log_files:
    with open(log_file, 'r') as f:
        content = f.read()

        # Extract metrics
        error_rate_match = re.search(r'Error Rate: ([\d.]+)%', content)
        p95_match = re.search(r'P95 Response Time: ([\d.]+)ms', content)
        p99_match = re.search(r'P99 Response Time: ([\d.]+)ms', content)

        if error_rate_match and p95_match and p99_match:
            error_rate = float(error_rate_match.group(1))
            p95 = float(p95_match.group(1))
            p99 = float(p99_match.group(1))
            scenario = os.path.basename(log_file).replace('.log', '')

            # Check against targets
            if error_rate < 5 and p95 < 200 and p99 < 500:
                findings.append(f"✓ **{scenario}**: All performance targets met")
            else:
                issues = []
                if error_rate >= 5:
                    issues.append(f"high error rate ({error_rate:.2f}%)")
                if p95 >= 200:
                    issues.append(f"P95 above target ({p95:.2f}ms)")
                if p99 >= 500:
                    issues.append(f"P99 above target ({p99:.2f}ms)")
                findings.append(f"✗ **{scenario}**: {', '.join(issues)}")

for finding in findings:
    print(finding)
PYTHON_EOF
)

### Recommendations

1. **Scaling**: Based on stress test results, consider horizontal scaling at X concurrent users
2. **Optimization**: Focus on endpoints with highest response times
3. **Caching**: Implement caching for frequently accessed resources
4. **Database**: Consider connection pooling optimization if DB bottlenecks observed
5. **Monitoring**: Set up real-time monitoring for production environment

---

## Next Steps

1. Review detailed HTML reports for each scenario
2. Analyze CSV data for trends and patterns
3. Address any performance bottlenecks identified
4. Re-run tests after optimizations
5. Set up continuous load testing in CI/CD pipeline

---

*Generated by YAGO v8.1 Load Testing Suite*
EOF

    print_success "Summary report generated: ${summary_file}"

    # Display summary
    echo ""
    cat "${summary_file}"
}

################################################################################
# Main Execution
################################################################################

main() {
    print_header "YAGO v8.1 Load Testing Suite"
    echo ""
    print_info "Scenario: ${SCENARIO}"
    print_info "Host: ${HOST}"
    print_info "Results Directory: ${REPORT_DIR}"
    echo ""

    # Check if backend is running
    if ! check_backend; then
        exit 1
    fi

    echo ""

    # Execute scenarios
    case "${SCENARIO}" in
        all)
            print_info "Running all scenarios..."
            echo ""

            run_scenario "01_normal_load" 10 2 "5m" "NormalLoadUser"
            sleep 5

            run_scenario "02_spike_load" 100 10 "3m" "SpikeLoadUser"
            sleep 5

            run_scenario "03_stress_test" 200 10 "5m" "StressTestUser"
            sleep 5

            run_scenario "04_endurance_test" 50 5 "10m" "EnduranceTestUser"
            ;;

        normal)
            run_scenario "normal_load" 10 2 "5m" "NormalLoadUser"
            ;;

        spike)
            run_scenario "spike_load" 100 10 "3m" "SpikeLoadUser"
            ;;

        stress)
            run_scenario "stress_test" 200 10 "5m" "StressTestUser"
            ;;

        endurance)
            run_scenario "endurance_test" 50 5 "30m" "EnduranceTestUser"
            ;;

        quick)
            print_info "Running quick test (30 seconds)..."
            run_scenario "quick_test" 10 2 "30s" "NormalLoadUser"
            ;;

        *)
            print_error "Unknown scenario: ${SCENARIO}"
            echo ""
            echo "Available scenarios:"
            echo "  all       - Run all scenarios (normal, spike, stress, endurance)"
            echo "  normal    - Normal load (10 users, 5 min)"
            echo "  spike     - Spike load (100 users, 3 min)"
            echo "  stress    - Stress test (200 users, 5 min)"
            echo "  endurance - Endurance test (50 users, 30 min)"
            echo "  quick     - Quick test (10 users, 30 sec)"
            exit 1
            ;;
    esac

    # Generate summary report
    echo ""
    generate_summary_report

    # Final summary
    echo ""
    print_header "Test Execution Complete"
    print_info "Results saved to: ${REPORT_DIR}"
    print_info "View summary: cat ${REPORT_DIR}/SUMMARY.md"
    print_info "View HTML reports: open ${REPORT_DIR}/html/*.html"
    echo ""

    # Archive results
    cd "${RESULTS_DIR}"
    tar -czf "${TIMESTAMP}.tar.gz" "${TIMESTAMP}"
    print_success "Results archived: ${RESULTS_DIR}/${TIMESTAMP}.tar.gz"
    echo ""
}

# Check dependencies
if ! command -v locust &> /dev/null; then
    print_error "Locust is not installed"
    echo ""
    echo "Install dependencies:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    print_error "curl is not installed"
    exit 1
fi

# Run main function
main

exit 0
