#!/bin/bash
set -e

echo "OrionAI Development Setup"
echo "========================="

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env and add your API keys"
fi

echo "Installing dependencies..."
pip install -r requirements-cpu.txt

echo "Running tests..."
pytest --cov=. --cov-report=term

echo "Starting Redis (if Docker is available)..."
if command -v docker &> /dev/null; then
    docker run -d --name orionai-redis -p 6379:6379 redis:7-alpine || echo "Redis already running"
else
    echo "Docker not found. Please install Redis manually or use Docker."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the application:"
echo "  python main.py"
echo ""
echo "To run tests:"
echo "  make test"
echo ""
echo "To run with Docker:"
echo "  docker-compose up"
