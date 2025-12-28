#!/usr/bin/env bash
set -euo pipefail

echo "Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -e "backend[dev]"

echo "Running backend tests..."
cd backend
pytest -v --cov=cockpit_authelia_users --cov-report=term-missing
