#!/bin/bash
# Simple run script for Invoice Sorter

set -e

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the processor
echo "Starting Invoice Sorter..."
python -m src.core.processor

echo "Done!"
