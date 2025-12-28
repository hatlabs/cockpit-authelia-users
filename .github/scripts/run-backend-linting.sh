#!/usr/bin/env bash
set -euo pipefail

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Running ruff check..."
cd backend
ruff check .

echo "Running pyright..."
pyright
