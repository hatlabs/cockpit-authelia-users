#!/usr/bin/env bash
set -euo pipefail

echo "Installing frontend dependencies..."
cd frontend
npm ci

echo "Building frontend..."
npm run build

echo "Running frontend type check..."
npm run typecheck

echo "Running frontend lint..."
npm run lint
