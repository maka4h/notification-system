#!/bin/bash

# Test runner script with cleanup functionality
# Usage: ./scripts/test.sh [--clean] [--frontend] [--backend] [--coverage]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
CLEAN_AFTER=false
RUN_FRONTEND=false
RUN_BACKEND=false
SHOW_COVERAGE=false
RUN_ALL=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN_AFTER=true
            shift
            ;;
        --frontend)
            RUN_FRONTEND=true
            RUN_ALL=false
            shift
            ;;
        --backend)
            RUN_BACKEND=true
            RUN_ALL=false
            shift
            ;;
        --coverage)
            SHOW_COVERAGE=true
            shift
            ;;
        -h|--help)
            echo "Test runner script with cleanup functionality"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --clean      Clean up test artifacts after running tests"
            echo "  --frontend   Run only frontend tests"
            echo "  --backend    Run only backend tests"
            echo "  --coverage   Show coverage reports"
            echo "  -h, --help   Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests"
            echo "  $0 --clean           # Run all tests and cleanup afterwards"
            echo "  $0 --backend --clean # Run backend tests and cleanup"
            echo "  $0 --coverage        # Run tests with coverage reports"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# If neither frontend nor backend specified, run all
if [[ "$RUN_ALL" == true ]]; then
    RUN_FRONTEND=true
    RUN_BACKEND=true
fi

echo -e "${BLUE}🧪 Notification System Test Runner${NC}"
echo "========================================"

# Function to clean up test artifacts
cleanup_test_artifacts() {
    echo -e "\n${YELLOW}🧹 Cleaning up test artifacts...${NC}"
    
    # Backend cleanup
    if [[ -d "notification-service" ]]; then
        echo "Cleaning backend test artifacts..."
        cd notification-service
        
        # Remove pytest cache
        rm -rf .pytest_cache
        rm -rf __pycache__
        find . -name "*.pyc" -delete
        find . -name "*.pyo" -delete
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        
        # Remove coverage files
        rm -f .coverage
        rm -f coverage.xml
        rm -rf htmlcov
        
        # Remove test databases
        rm -f test_*.db
        rm -f *test*.sqlite3
        
        # Remove any temp files
        rm -rf .cache
        rm -f *.tmp
        rm -f *.temp
        
        cd ..
    fi
    
    # Frontend cleanup
    if [[ -d "demo-ui" ]]; then
        echo "Cleaning frontend test artifacts..."
        cd demo-ui
        
        # Remove Jest cache
        rm -rf .cache
        
        # Remove coverage reports
        rm -rf coverage
        
        # Remove test results
        rm -f test-results.xml
        rm -f junit.xml
        
        # Remove any temp files
        rm -f *.tmp
        rm -f *.temp
        
        cd ..
    fi
    
    echo -e "${GREEN}✅ Cleanup completed!${NC}"
}

# Function to run backend tests
run_backend_tests() {
    echo -e "\n${BLUE}🐍 Running Backend Tests (Python/FastAPI)${NC}"
    echo "----------------------------------------"
    
    if [[ ! -d "notification-service" ]]; then
        echo -e "${RED}❌ Backend directory not found!${NC}"
        return 1
    fi
    
    cd notification-service
    
    # Check if virtual environment exists
    if [[ ! -d "test_env" ]]; then
        echo -e "${YELLOW}⚠️  Test environment not found. Please run setup first.${NC}"
        cd ..
        return 1
    fi
    
    # Activate virtual environment and run tests
    source test_env/bin/activate
    
    if [[ "$SHOW_COVERAGE" == true ]]; then
        echo "Running tests with coverage..."
        python -m pytest tests/ -v --cov=app --cov-report=term --cov-report=html --cov-report=xml
    else
        echo "Running tests..."
        python -m pytest tests/ -v
    fi
    
    deactivate
    cd ..
    
    echo -e "${GREEN}✅ Backend tests completed!${NC}"
}

# Function to run frontend tests
run_frontend_tests() {
    echo -e "\n${BLUE}⚛️  Running Frontend Tests (React/Jest)${NC}"
    echo "---------------------------------------"
    
    if [[ ! -d "demo-ui" ]]; then
        echo -e "${RED}❌ Frontend directory not found!${NC}"
        return 1
    fi
    
    cd demo-ui
    
    # Check if node_modules exists
    if [[ ! -d "node_modules" ]]; then
        echo -e "${YELLOW}📦 Installing dependencies...${NC}"
        npm install
    fi
    
    if [[ "$SHOW_COVERAGE" == true ]]; then
        echo "Running tests with coverage..."
        npm test -- --coverage --watchAll=false --verbose
    else
        echo "Running tests..."
        npm test -- --watchAll=false --verbose
    fi
    
    cd ..
    
    echo -e "${GREEN}✅ Frontend tests completed!${NC}"
}

# Main execution
echo "Configuration:"
echo "  Frontend tests: $RUN_FRONTEND"
echo "  Backend tests: $RUN_BACKEND"
echo "  Show coverage: $SHOW_COVERAGE"
echo "  Clean after: $CLEAN_AFTER"
echo ""

# Track if any tests failed
TEST_FAILED=false

# Run backend tests
if [[ "$RUN_BACKEND" == true ]]; then
    if ! run_backend_tests; then
        TEST_FAILED=true
        echo -e "${RED}❌ Backend tests failed!${NC}"
    fi
fi

# Run frontend tests
if [[ "$RUN_FRONTEND" == true ]]; then
    if ! run_frontend_tests; then
        TEST_FAILED=true
        echo -e "${RED}❌ Frontend tests failed!${NC}"
    fi
fi

# Show summary
echo -e "\n${BLUE}📊 Test Summary${NC}"
echo "==============="

if [[ "$TEST_FAILED" == true ]]; then
    echo -e "${RED}❌ Some tests failed!${NC}"
    EXIT_CODE=1
else
    echo -e "${GREEN}✅ All tests passed!${NC}"
    EXIT_CODE=0
fi

# Cleanup if requested
if [[ "$CLEAN_AFTER" == true ]]; then
    cleanup_test_artifacts
fi

# Show coverage information if generated
if [[ "$SHOW_COVERAGE" == true ]]; then
    echo -e "\n${BLUE}📈 Coverage Reports Generated:${NC}"
    if [[ -f "notification-service/htmlcov/index.html" ]]; then
        echo "  Backend: notification-service/htmlcov/index.html"
    fi
    if [[ -d "demo-ui/coverage" ]]; then
        echo "  Frontend: demo-ui/coverage/lcov-report/index.html"
    fi
fi

echo -e "\n${BLUE}🏁 Test execution completed!${NC}"

# Exit with appropriate code
exit $EXIT_CODE
