#!/bin/bash

# ZAZAH Startup Script
# This script enforces the use of the project virtual environment
# and provides helpful error messages if the venv is not activated.

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/.venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}[ERROR] Virtual environment not found at $VENV_DIR${NC}"
    echo -e "${YELLOW}Please create the venv first:${NC}"
    echo "  python3 -m venv .venv"
    echo "  .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if venv is activated
if [[ "$VIRTUAL_ENV" != "$VENV_DIR" ]]; then
    echo -e "${YELLOW}[INFO] Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
fi

# Verify Python version
PYTHON_VERSION=$("$VENV_DIR/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}[OK] Using Python $PYTHON_VERSION from venv${NC}"

# Check Python compatibility
"$VENV_DIR/bin/python" "$PROJECT_ROOT/app.py"
