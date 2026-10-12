#!/bin/bash
set -e

# OrionAI Setup Script
# Consolidated setup for CPU and GPU environments

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
DEVICE="auto"
SKIP_OLLAMA=false
SKIP_INGESTION=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --cpu)
            DEVICE="cpu"
            shift
            ;;
        --gpu)
            DEVICE="cuda"
            shift
            ;;
        --skip-ollama)
            SKIP_OLLAMA=true
            shift
            ;;
        --skip-ingestion)
            SKIP_INGESTION=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --cpu              Force CPU-only setup"
            echo "  --gpu              Force GPU setup (requires CUDA)"
            echo "  --skip-ollama      Skip Ollama installation"
            echo "  --skip-ingestion   Skip document ingestion"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_info "Starting OrionAI setup (device: $DEVICE)"

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_error "Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi
print_info "Python version: $PYTHON_VERSION ✓"

# Create virtual environment
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install PyTorch based on device
print_info "Installing PyTorch..."
if [ "$DEVICE" = "cuda" ]; then
    print_info "Installing PyTorch with CUDA support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
elif [ "$DEVICE" = "cpu" ]; then
    print_info "Installing PyTorch (CPU-only)..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
else
    print_info "Installing PyTorch (auto-detect)..."
    pip install torch torchvision torchaudio
fi

# Install requirements
print_info "Installing dependencies..."
if [ "$DEVICE" = "cpu" ]; then
    pip install -r requirements-cpu.txt
elif [ "$DEVICE" = "cuda" ]; then
    pip install -r requirements-gpu.txt
else
    pip install -r requirements.txt
fi

# Validate environment
print_info "Validating environment..."
python scripts/validate_environment.py

# Setup Ollama (optional)
if [ "$SKIP_OLLAMA" = false ]; then
    print_info "Setting up Ollama..."
    if command -v ollama &> /dev/null; then
        print_info "Ollama already installed ✓"
        
        # Check if model is available
        if ollama list | grep -q "llama3.2:1b"; then
            print_info "Model llama3.2:1b already available ✓"
        else
            print_info "Pulling llama3.2:1b model..."
            ollama pull llama3.2:1b
        fi
    else
        print_warn "Ollama not found. Install from: https://ollama.ai"
        print_warn "Or run: curl -fsSL https://ollama.ai/install.sh | sh"
    fi
else
    print_info "Skipping Ollama setup"
fi

# Create necessary directories
print_info "Creating directories..."
mkdir -p artifacts/index
mkdir -p logs

# Copy environment template
if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_warn "Please edit .env with your configuration"
else
    print_info ".env file already exists"
fi

# Ingest documents (optional)
if [ "$SKIP_INGESTION" = false ]; then
    if [ -d "sample_docs" ] && [ "$(ls -A sample_docs)" ]; then
        print_info "Ingesting sample documents..."
        python scripts/ingest_documents.py sample_docs/
    else
        print_warn "No sample documents found in sample_docs/"
    fi
else
    print_info "Skipping document ingestion"
fi

print_info ""
print_info "========================================="
print_info "Setup complete! ✓"
print_info "========================================="
print_info ""
print_info "Next steps:"
print_info "  1. Edit .env with your configuration"
print_info "  2. Start the API: python main.py"
print_info "  3. Test: curl http://localhost:8011/health"
print_info ""
print_info "For Docker deployment:"
print_info "  docker-compose up orionai-cpu"
print_info ""
print_info "For Kubernetes deployment:"
print_info "  kubectl apply -f k8s/"
print_info ""
