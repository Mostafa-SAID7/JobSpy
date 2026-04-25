#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
FRONTEND_PASS=0
BACKEND_PASS=0
TOTAL_TESTS=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}JobSpy Testing Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to run tests
run_test() {
    local test_name=$1
    local test_command=$2
    local test_dir=$3
    
    echo -e "${YELLOW}Running: $test_name${NC}"
    
    if [ -n "$test_dir" ]; then
        cd "$test_dir" || exit 1
    fi
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ $test_name passed${NC}\n"
        return 0
    else
        echo -e "${RED}✗ $test_name failed${NC}\n"
        return 1
    fi
}

# Frontend Tests
echo -e "${BLUE}--- Frontend Tests ---${NC}\n"

if run_test "Frontend Unit Tests" "npm run test -- --run" "Frontend"; then
    FRONTEND_PASS=$((FRONTEND_PASS + 1))
fi

if run_test "Frontend Type Check" "npm run type-check" "Frontend"; then
    FRONTEND_PASS=$((FRONTEND_PASS + 1))
fi

if run_test "Frontend Lint" "npm run lint" "Frontend"; then
    FRONTEND_PASS=$((FRONTEND_PASS + 1))
fi

# Backend Tests
echo -e "${BLUE}--- Backend Tests ---${NC}\n"

cd Backend || exit 1

if run_test "Backend Unit Tests" "pytest tests/unit/ -v"; then
    BACKEND_PASS=$((BACKEND_PASS + 1))
fi

if run_test "Backend Integration Tests" "pytest tests/integration/ -v"; then
    BACKEND_PASS=$((BACKEND_PASS + 1))
fi

if run_test "Backend Security Tests" "pytest tests/security/ -v"; then
    BACKEND_PASS=$((BACKEND_PASS + 1))
fi

if run_test "Backend with Coverage" "pytest --cov=app --cov-report=term-missing"; then
    BACKEND_PASS=$((BACKEND_PASS + 1))
fi

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "Frontend Tests Passed: ${GREEN}$FRONTEND_PASS/3${NC}"
echo -e "Backend Tests Passed: ${GREEN}$BACKEND_PASS/4${NC}"

TOTAL_PASS=$((FRONTEND_PASS + BACKEND_PASS))
TOTAL_TESTS=7

if [ $TOTAL_PASS -eq $TOTAL_TESTS ]; then
    echo -e "\n${GREEN}All tests passed! ✓${NC}\n"
    exit 0
else
    echo -e "\n${RED}Some tests failed. Please review the output above.${NC}\n"
    exit 1
fi
