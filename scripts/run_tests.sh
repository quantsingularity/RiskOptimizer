#!/bin/bash
# run_tests.sh
# Comprehensive test runner for RiskOptimizer
# This script automates running tests across all components of the RiskOptimizer platform

# Color definitions for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Log function for consistent output
log() {
    local level=$1
    local message=$2
    local color=$NC
    
    case $level in
        "INFO") color=$BLUE ;;
        "SUCCESS") color=$GREEN ;;
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac
    
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message${NC}"
}

# Error handling function
handle_error() {
    log "ERROR" "An error occurred on line $1"
    exit 1
}

# Set up error handling
trap 'handle_error $LINENO' ERR

# Enable strict mode
set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse command line arguments
COMPONENT="all"
COVERAGE=false
PARALLEL=false
VERBOSE=false
QUICK=false

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Run tests for RiskOptimizer components"
    echo ""
    echo "Options:"
    echo "  -c, --component COMPONENT  Run tests for specific component"
    echo "                             (all, backend, frontend, ai_models, blockchain)"
    echo "  --coverage                 Generate test coverage reports"
    echo "  -p, --parallel             Run tests in parallel"
    echo "  -v, --verbose              Show verbose output"
    echo "  -q, --quick                Run only quick tests (subset of all tests)"
    echo "  -h, --help                 Show this help message"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--component)
            COMPONENT="$2"
            shift 2
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quick)
            QUICK=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Validate component argument
if [[ ! "$COMPONENT" =~ ^(all|backend|frontend|ai_models|blockchain)$ ]]; then
    log "ERROR" "Invalid component: $COMPONENT"
    print_usage
    exit 1
fi

# Function to activate virtual environment
activate_venv() {
    if [ -d "$PROJECT_ROOT/venv" ]; then
        source "$PROJECT_ROOT/venv/bin/activate"
        log "INFO" "Activated virtual environment"
    else
        log "WARNING" "Virtual environment not found at $PROJECT_ROOT/venv"
        log "INFO" "Creating virtual environment..."
        python3 -m venv "$PROJECT_ROOT/venv"
        source "$PROJECT_ROOT/venv/bin/activate"
        log "SUCCESS" "Created and activated virtual environment"
    fi
}

# Function to run backend tests
run_backend_tests() {
    log "INFO" "Running backend tests..."
    cd "$PROJECT_ROOT/code/backend"
    
    # Install test dependencies if needed
    pip install pytest pytest-cov pytest-xdist > /dev/null
    
    # Build test command
    TEST_CMD="python -m pytest"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --cov=. --cov-report=html:$PROJECT_ROOT/test_reports/backend/coverage"
    fi
    
    if [ "$PARALLEL" = true ]; then
        TEST_CMD="$TEST_CMD -xvs -n auto"
    fi
    
    if [ "$QUICK" = true ]; then
        TEST_CMD="$TEST_CMD -k 'not slow'"
    fi
    
    # Run tests
    mkdir -p "$PROJECT_ROOT/test_reports/backend"
    $TEST_CMD --junitxml="$PROJECT_ROOT/test_reports/backend/results.xml"
    
    if [ "$COVERAGE" = true ]; then
        log "SUCCESS" "Backend test coverage report generated at $PROJECT_ROOT/test_reports/backend/coverage"
    fi
    
    log "SUCCESS" "Backend tests completed"
}

# Function to run frontend tests
run_frontend_tests() {
    log "INFO" "Running frontend tests..."
    cd "$PROJECT_ROOT/code/web-frontend"
    
    # Build test command
    TEST_CMD="npm test"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -- --verbose"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD -- --coverage --coverageDirectory=$PROJECT_ROOT/test_reports/frontend/coverage"
    fi
    
    if [ "$QUICK" = true ]; then
        TEST_CMD="$TEST_CMD -- --testPathIgnorePatterns=integration"
    fi
    
    # Run tests
    mkdir -p "$PROJECT_ROOT/test_reports/frontend"
    $TEST_CMD
    
    if [ "$COVERAGE" = true ]; then
        log "SUCCESS" "Frontend test coverage report generated at $PROJECT_ROOT/test_reports/frontend/coverage"
    fi
    
    log "SUCCESS" "Frontend tests completed"
}

# Function to run AI model tests
run_ai_model_tests() {
    log "INFO" "Running AI model tests..."
    cd "$PROJECT_ROOT/code/ai_models"
    
    # Install test dependencies if needed
    pip install pytest pytest-cov > /dev/null
    
    # Build test command
    TEST_CMD="python -m pytest"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --cov=. --cov-report=html:$PROJECT_ROOT/test_reports/ai_models/coverage"
    fi
    
    if [ "$PARALLEL" = true ]; then
        TEST_CMD="$TEST_CMD -xvs -n auto"
    fi
    
    if [ "$QUICK" = true ]; then
        TEST_CMD="$TEST_CMD -k 'not slow'"
    fi
    
    # Run tests
    mkdir -p "$PROJECT_ROOT/test_reports/ai_models"
    $TEST_CMD --junitxml="$PROJECT_ROOT/test_reports/ai_models/results.xml"
    
    if [ "$COVERAGE" = true ]; then
        log "SUCCESS" "AI model test coverage report generated at $PROJECT_ROOT/test_reports/ai_models/coverage"
    fi
    
    log "SUCCESS" "AI model tests completed"
}

# Function to run blockchain tests
run_blockchain_tests() {
    log "INFO" "Running blockchain tests..."
    cd "$PROJECT_ROOT/code/blockchain"
    
    # Build test command
    TEST_CMD="npx hardhat test"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD --verbose"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="npx hardhat coverage"
        mkdir -p "$PROJECT_ROOT/test_reports/blockchain/coverage"
    fi
    
    # Run tests
    mkdir -p "$PROJECT_ROOT/test_reports/blockchain"
    $TEST_CMD
    
    if [ "$COVERAGE" = true ]; then
        # Move coverage report to standard location
        cp -r coverage/* "$PROJECT_ROOT/test_reports/blockchain/coverage/"
        log "SUCCESS" "Blockchain test coverage report generated at $PROJECT_ROOT/test_reports/blockchain/coverage"
    fi
    
    log "SUCCESS" "Blockchain tests completed"
}

# Function to run integration tests
run_integration_tests() {
    if [ "$QUICK" = true ]; then
        log "INFO" "Skipping integration tests in quick mode"
        return 0
    fi
    
    log "INFO" "Running integration tests..."
    cd "$PROJECT_ROOT"
    
    # Start services in background for integration testing
    log "INFO" "Starting services for integration testing..."
    
    # Start backend
    cd "$PROJECT_ROOT/code/backend"
    python app.py > /dev/null 2>&1 &
    BACKEND_PID=$!
    
    # Start frontend
    cd "$PROJECT_ROOT/code/web-frontend"
    npm start > /dev/null 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for services to start
    log "INFO" "Waiting for services to start..."
    sleep 10
    
    # Run integration tests
    cd "$PROJECT_ROOT/tests/integration"
    
    # Build test command
    TEST_CMD="python -m pytest"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --cov=. --cov-report=html:$PROJECT_ROOT/test_reports/integration/coverage"
    fi
    
    # Run tests
    mkdir -p "$PROJECT_ROOT/test_reports/integration"
    $TEST_CMD --junitxml="$PROJECT_ROOT/test_reports/integration/results.xml"
    
    # Clean up background processes
    kill $BACKEND_PID $FRONTEND_PID
    
    log "SUCCESS" "Integration tests completed"
}

# Function to generate combined test report
generate_test_report() {
    log "INFO" "Generating combined test report..."
    
    # Create report directory
    REPORT_DIR="$PROJECT_ROOT/test_reports"
    mkdir -p "$REPORT_DIR"
    
    # Generate HTML report
    cat > "$REPORT_DIR/index.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>RiskOptimizer Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        h1 { color: #333; }
        .summary { background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .component { margin-bottom: 30px; }
        .success { color: green; }
        .warning { color: orange; }
        .error { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>RiskOptimizer Test Report</h1>
    <div class="summary">
        <h2>Test Summary</h2>
        <p>Generated on: $(date)</p>
        <p>Components tested: $COMPONENT</p>
    </div>
    
    <div class="component">
        <h2>Test Results</h2>
        <p>For detailed results, see the individual component reports in the test_reports directory.</p>
    </div>
    
    <div class="component">
        <h2>Coverage Reports</h2>
        <ul>
EOF

    # Add links to coverage reports if generated
    if [ "$COVERAGE" = true ]; then
        if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "backend" ]; then
            echo '<li><a href="backend/coverage/index.html">Backend Coverage</a></li>' >> "$REPORT_DIR/index.html"
        fi
        if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "frontend" ]; then
            echo '<li><a href="frontend/coverage/index.html">Frontend Coverage</a></li>' >> "$REPORT_DIR/index.html"
        fi
        if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "ai_models" ]; then
            echo '<li><a href="ai_models/coverage/index.html">AI Models Coverage</a></li>' >> "$REPORT_DIR/index.html"
        fi
        if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "blockchain" ]; then
            echo '<li><a href="blockchain/coverage/index.html">Blockchain Coverage</a></li>' >> "$REPORT_DIR/index.html"
        fi
        if [ "$COMPONENT" = "all" ] && [ "$QUICK" = false ]; then
            echo '<li><a href="integration/coverage/index.html">Integration Tests Coverage</a></li>' >> "$REPORT_DIR/index.html"
        fi
    fi

    # Complete the HTML
    cat >> "$REPORT_DIR/index.html" << EOF
        </ul>
    </div>
</body>
</html>
EOF

    log "SUCCESS" "Test report generated at $REPORT_DIR/index.html"
}

# Main execution
log "INFO" "Starting RiskOptimizer test runner..."

# Activate virtual environment for Python tests
activate_venv

# Run tests based on component selection
if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "backend" ]; then
    run_backend_tests
fi

if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "frontend" ]; then
    run_frontend_tests
fi

if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "ai_models" ]; then
    run_ai_model_tests
fi

if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "blockchain" ]; then
    run_blockchain_tests
fi

if [ "$COMPONENT" = "all" ]; then
    run_integration_tests
fi

# Generate combined test report
generate_test_report

# Deactivate virtual environment
deactivate

log "SUCCESS" "All tests completed successfully!"
exit 0
