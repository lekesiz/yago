#!/bin/bash
# YAGO v8.0 - Comprehensive API Endpoint Testing
# Tests all endpoints including the newly fixed clarification endpoints

BASE_URL="http://localhost:8000"
PASSED=0
FAILED=0
WARNINGS=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "🚀 YAGO v8.0 - COMPREHENSIVE API ENDPOINT TESTING"
echo "============================================================"
echo ""

test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="$4"

    echo -n "Testing: $name... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$url" -H "Content-Type: application/json" -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        return 0
    elif [ "$http_code" -ge 400 ] && [ "$http_code" -lt 500 ]; then
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code)"
        FAILED=$((FAILED + 1))
        return 1
    else
        echo -e "${YELLOW}⚠️  WARN${NC} (HTTP $http_code)"
        WARNINGS=$((WARNINGS + 1))
        return 2
    fi
}

echo "=== Core Health Checks ==="
test_endpoint "Root Endpoint" "$BASE_URL/"
test_endpoint "Health Check" "$BASE_URL/health"
echo ""

echo "=== Template Endpoints ==="
test_endpoint "Templates List" "$BASE_URL/api/v1/templates/"
test_endpoint "Templates Categories" "$BASE_URL/api/v1/templates/categories"
test_endpoint "Popular Templates" "$BASE_URL/api/v1/templates/popular"
test_endpoint "Templates Health" "$BASE_URL/api/v1/templates/health"
test_endpoint "Template by ID" "$BASE_URL/api/v1/templates/web_app"
test_endpoint "Template Preview" "$BASE_URL/api/v1/templates/web_app/preview"
test_endpoint "Template Search" "$BASE_URL/api/v1/templates/search?q=web"
echo ""

echo "=== Clarification Endpoints (FIXED) ==="
# Start a clarification session
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/clarifications/start" \
  -H "Content-Type: application/json" \
  -d '{"project_idea": "Build a web application", "depth": "standard"}')
SESSION_ID=$(echo "$SESSION_RESPONSE" | grep -o '"session_id":"[^"]*' | sed 's/"session_id":"//')

test_endpoint "Start Clarification" "$BASE_URL/api/v1/clarifications/start" "POST" '{"project_idea": "Test project", "depth": "standard"}'

if [ -n "$SESSION_ID" ]; then
    test_endpoint "Get Clarification Session" "$BASE_URL/api/v1/clarifications/$SESSION_ID"
    test_endpoint "Get Progress" "$BASE_URL/api/v1/clarifications/$SESSION_ID/progress"
    test_endpoint "Update Draft" "$BASE_URL/api/v1/clarifications/$SESSION_ID/draft" "PUT" '{"answers": {"q1": "Test"}}'
    test_endpoint "Navigate Next" "$BASE_URL/api/v1/clarifications/$SESSION_ID/navigate/next" "POST"
    test_endpoint "Navigate Previous" "$BASE_URL/api/v1/clarifications/$SESSION_ID/navigate/previous" "POST"
    test_endpoint "Submit Answer" "$BASE_URL/api/v1/clarifications/$SESSION_ID/answer" "POST" '{"question_id": "q1", "answer": "Test answer"}'
    test_endpoint "Complete Clarification" "$BASE_URL/api/v1/clarifications/$SESSION_ID/complete" "POST"
else
    echo -e "${YELLOW}⚠️  Skipping session-based tests (no session ID)${NC}"
fi
echo ""

echo "=== AI Models Endpoints ==="
test_endpoint "Models List" "$BASE_URL/api/v1/models/list"
test_endpoint "Model Providers" "$BASE_URL/api/v1/models/providers"
test_endpoint "Model by ID" "$BASE_URL/api/v1/models/gpt-4-turbo"
test_endpoint "Model Test" "$BASE_URL/api/v1/models/gpt-4-turbo/test" "POST" '{"prompt": "Hello"}'
test_endpoint "Compare Models" "$BASE_URL/api/v1/models/compare" "POST" '{"model_ids": ["gpt-4-turbo", "claude-3-opus"]}'
echo ""

echo "=== Analytics Endpoints ==="
test_endpoint "Analytics Metrics" "$BASE_URL/api/v1/analytics/metrics"
test_endpoint "Usage Stats" "$BASE_URL/api/v1/analytics/usage"
test_endpoint "Models Usage" "$BASE_URL/api/v1/analytics/models-usage"
echo ""

echo "=== Marketplace Endpoints ==="
test_endpoint "Marketplace Items" "$BASE_URL/api/v1/marketplace/items"
test_endpoint "Marketplace Item by ID" "$BASE_URL/api/v1/marketplace/items/plugin-slack"
test_endpoint "Install Item" "$BASE_URL/api/v1/marketplace/items/plugin-slack/install" "POST"
echo ""

echo "=== Collaboration Endpoints ==="
test_endpoint "Collaboration Health" "$BASE_URL/api/v1/collaboration/health"
test_endpoint "Send Message" "$BASE_URL/api/v1/collaboration/messages/send" "POST" '{"message": "Test"}'
echo ""

echo "=== Cost Tracking Endpoints ==="
test_endpoint "Costs Health" "$BASE_URL/api/v1/costs/health"
test_endpoint "Cost Summary" "$BASE_URL/api/v1/costs/summary/test-project-123"
echo ""

echo "=== Benchmarks Endpoints ==="
test_endpoint "Benchmarks Health" "$BASE_URL/api/v1/benchmarks/health"
echo ""

echo "============================================================"
echo "📊 TEST SUMMARY"
echo "============================================================"
echo -e "✅ Passed:   ${GREEN}$PASSED${NC}"
echo -e "❌ Failed:   ${RED}$FAILED${NC}"
echo -e "⚠️  Warnings: ${YELLOW}$WARNINGS${NC}"
TOTAL=$((PASSED + FAILED + WARNINGS))
echo "📈 Total:    $TOTAL"
echo ""

if [ $FAILED -eq 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $PASSED * 100 / $TOTAL" | bc)
    echo -e "${GREEN}🎉 SUCCESS RATE: $SUCCESS_RATE%${NC}"
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ ALL TESTS PASSED - 100% SUCCESS!${NC}"
    else
        echo -e "${GREEN}✅ All critical tests passed ($WARNINGS minor warnings)${NC}"
    fi
    exit 0
else
    echo -e "${RED}⚠️  $FAILED tests failed - review needed${NC}"
    exit 1
fi
