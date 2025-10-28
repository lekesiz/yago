#!/bin/bash

# YAGO v7.1 - API Endpoint Integration Tests
# Tests all backend API endpoints

echo "🚀 YAGO v7.1 API Integration Tests"
echo "=================================="
echo ""

BASE_URL="http://localhost:8000"
TEST_PROJECT_ID="test-project-$(date +%s)"
PASSED=0
FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_code="$5"

    echo -n "Testing: $name... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Expected $expected_code, Got $http_code)"
        echo "Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "📊 Cost Tracking API Tests"
echo "-------------------------"
test_endpoint "Cost Health Check" "GET" "/api/v1/costs/health" "" "200"
test_endpoint "Get Cost Summary (404 expected)" "GET" "/api/v1/costs/summary/$TEST_PROJECT_ID" "" "404"
test_endpoint "Track API Call" "POST" "/api/v1/costs/track" \
    '{"project_id":"'$TEST_PROJECT_ID'","agent_id":"agent-001","agent_type":"Planner","phase":"planning","model":"gpt-4o","provider":"openai","tokens_input":100,"tokens_output":50,"tokens_total":150,"cost":0.003,"duration_ms":1500,"success":true}' \
    "200"
test_endpoint "Get Cost Summary (After Tracking)" "GET" "/api/v1/costs/summary/$TEST_PROJECT_ID" "" "200"
echo ""

echo "🤝 Collaboration API Tests"
echo "-------------------------"
test_endpoint "Collaboration Health Check" "GET" "/api/v1/collaboration/health" "" "200"
test_endpoint "Register Agent" "POST" "/api/v1/collaboration/agents/$TEST_PROJECT_ID/register?agent_type=Planner" "" "200"
test_endpoint "Get Agents Status" "GET" "/api/v1/collaboration/agents/$TEST_PROJECT_ID/status" "" "200"
test_endpoint "Get Shared Context" "GET" "/api/v1/collaboration/context/$TEST_PROJECT_ID" "" "200"
test_endpoint "Send Message" "POST" "/api/v1/collaboration/messages/send" \
    '{"project_id":"'$TEST_PROJECT_ID'","from_agent":"Planner","to_agent":"Coder","message_type":"code_ready","priority":"MEDIUM","data":{"code":"print(\"hello\")"},"requires_ack":false}' \
    "200"
test_endpoint "Get Messages" "GET" "/api/v1/collaboration/messages/$TEST_PROJECT_ID" "" "200"
echo ""

echo "📈 Benchmark API Tests"
echo "----------------------"
test_endpoint "Benchmark Health Check" "GET" "/api/v1/benchmarks/health" "" "200"
test_endpoint "Run Benchmark" "POST" "/api/v1/benchmarks/run/full-suite" \
    '{"project_id":"'$TEST_PROJECT_ID'","iterations":5}' \
    "200"
echo ""

echo "📋 Template API Tests"
echo "---------------------"
test_endpoint "Get All Templates" "GET" "/api/v1/templates/" "" "200"
echo ""

echo "🔍 Clarification API Tests"
echo "--------------------------"
test_endpoint "Start Clarification" "POST" "/api/v1/clarifications/start" \
    '{"project_idea":"A simple task management app","depth":"standard"}' \
    "200"
echo ""

echo ""
echo "=================================="
echo "📊 Test Summary"
echo "=================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))
echo "Success Rate: $PERCENTAGE%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
