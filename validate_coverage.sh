#!/bin/bash
# Test Coverage Validation Script

set -e

echo "=========================================="
echo "OrionAI Test Coverage Validation"
echo "=========================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
python --version
echo ""

# Check if pytest is available
echo "2. Checking pytest installation..."
python -m pytest --version
echo ""

# List new test files
echo "3. New test files created:"
echo "   - tests/unit/test_orchestrator_async.py"
echo "   - tests/unit/test_router_async.py"
echo "   - tests/unit/test_cache_manager.py"
echo "   - tests/unit/test_observability.py"
echo "   - tests/unit/test_main_app.py"
echo "   - tests/unit/test_evaluation.py"
echo "   - tests/unit/test_retrieval_async.py"
echo "   - tests/unit/test_config_validation.py"
echo ""

# Count total tests
echo "4. Counting test files..."
TEST_COUNT=$(find tests -name "test_*.py" | wc -l)
echo "   Total test files: $TEST_COUNT"
echo ""

# Verify .coveragerc exists
echo "5. Verifying coverage configuration..."
if [ -f ".coveragerc" ]; then
    echo "   ✓ .coveragerc exists"
else
    echo "   ✗ .coveragerc missing"
    exit 1
fi
echo ""

# Check package structure
echo "6. Verifying package structure..."
for module in agents api core evaluation llm observability retrieval; do
    if [ -f "$module/__init__.py" ]; then
        echo "   ✓ $module/__init__.py exists"
    else
        echo "   ✗ $module/__init__.py missing"
        exit 1
    fi
done
echo ""

echo "=========================================="
echo "Validation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install -r requirements-dev.txt"
echo "2. Run tests: pytest tests/ -v"
echo "3. Generate coverage: pytest --cov=. --cov-report=html"
echo "4. View report: open htmlcov/index.html"
echo ""
