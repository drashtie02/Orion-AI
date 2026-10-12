#!/bin/bash
# Production Readiness Verification Script

echo "=================================="
echo "OrionAI Production Verification"
echo "=================================="
echo ""

PASS=0
FAIL=0

check() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
        ((PASS++))
    else
        echo "❌ $1"
        ((FAIL++))
    fi
}

# Check no shell scripts at root
echo "Checking root directory cleanliness..."
COUNT=$(find . -maxdepth 1 -type f -name "*.sh" 2>/dev/null | wc -l)
[ "$COUNT" -eq 0 ]
check "No shell scripts at root"

# Check no __pycache__
COUNT=$(find . -type d -name "__pycache__" ! -path "./venv/*" 2>/dev/null | wc -l)
[ "$COUNT" -eq 0 ]
check "No __pycache__ directories"

# Check no .env tracked
[ ! -f ".env" ] || [ -z "$(git ls-files .env 2>/dev/null)" ]
check "No .env file tracked"

# Check .env.example exists
[ -f ".env.example" ]
check ".env.example exists"

# Check .gitignore exists
[ -f ".gitignore" ]
check ".gitignore exists"

# Check CONTRIBUTING.md exists
[ -f "CONTRIBUTING.md" ]
check "CONTRIBUTING.md exists"

# Check Makefile exists
[ -f "Makefile" ]
check "Makefile exists"

# Check CI workflow exists
[ -f ".github/workflows/ci.yml" ]
check "CI workflow exists"

# Check examples directory exists
[ -d "examples" ]
check "examples/ directory exists"

# Check consolidated setup script
[ -f "scripts/setup.sh" ] && [ -x "scripts/setup.sh" ]
check "Consolidated setup script exists and is executable"

# Check requirements-dev.txt exists
[ -f "requirements-dev.txt" ]
check "requirements-dev.txt exists"

# Check main.py exists
[ -f "main.py" ]
check "main.py exists"

# Check Dockerfile exists
[ -f "Dockerfile" ]
check "Dockerfile exists"

# Check docker-compose.yml exists
[ -f "docker-compose.yml" ]
check "docker-compose.yml exists"

# Check k8s directory exists
[ -d "k8s" ]
check "k8s/ directory exists"

# Check helm directory exists
[ -d "helm" ]
check "helm/ directory exists"

# Check tests directory exists
[ -d "tests" ]
check "tests/ directory exists"

# Check docs directory exists
[ -d "docs" ]
check "docs/ directory exists"

echo ""
echo "=================================="
echo "Results: $PASS passed, $FAIL failed"
echo "=================================="

if [ $FAIL -eq 0 ]; then
    echo "✅ Repository is production-ready!"
    exit 0
else
    echo "❌ Some checks failed"
    exit 1
fi
