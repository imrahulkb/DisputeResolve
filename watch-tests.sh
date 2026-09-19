#!/bin/bash

# Watch mode test runner for BillResolve
# Automatically re-runs tests on file changes

echo "Starting pytest in watch mode..."
echo "Tests will re-run automatically when files change."
echo ""

ptw src/tests/ -- -v
