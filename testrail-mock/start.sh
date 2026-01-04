#!/bin/bash
# Quick start script for TestRail Mock Service (local development)

set -e

echo "🚀 Starting TestRail Mock Service..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the testrail-mock directory"
    echo "   cd mock-services/testrail-mock && ./start.sh"
    exit 1
fi

# Check Python version and recommend compatible version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Detected Python $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  Python 3.13 detected. If you encounter issues, consider using Python 3.11 or 3.12"
    echo "   You can install with: brew install python@3.12"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    # Try Python 3.11 first, fallback to python3
    if command -v python3.11 &> /dev/null; then
        python3.11 -m venv .venv
    else
        python3 -m venv .venv
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and install dependencies
echo "📥 Installing dependencies..."
python -m pip install --upgrade pip --quiet
echo "   Installing FastAPI and dependencies (this may take a moment)..."
pip install -r requirements.txt

# Start the server
echo "✅ Starting TestRail Mock on http://localhost:4002"
echo "   - UI Dashboard: http://localhost:4002/ui"
echo "   - Test Cases: http://localhost:4002/ui/cases"
echo "   - API Docs: http://localhost:4002/docs"
echo "   - Health: http://localhost:4002/health"
echo ""
echo "🧪 Sample test data loaded:"
echo "   - 5 test sections (Authentication, User Management, API Tests, UI Tests, Integration)"
echo "   - 18 sample test cases with steps and results"
echo "   - 1 test run with execution history"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app:app --host 0.0.0.0 --port 4002 --reload
