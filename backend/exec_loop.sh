#!/bin/bash
# =============================================================================
# JobAlert AI - Simple Execution Loop
# =============================================================================
# Runs the job ingestion poller continuously with automatic restart on failure.
# Inspired by the job_market_intelligence_bot approach but adapted for our stack.
#
# Usage:
#   ./exec_loop.sh                    # Run in foreground
#   nohup ./exec_loop.sh > loop.log 2>&1 &   # Run in background
#
# Stop:
#   pkill -f exec_loop.sh
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
INTERVAL=1800  # 30 minutes between runs (in seconds)
MAX_RETRIES=3
RETRY_DELAY=60

echo "========================================"
echo "JobAlert AI - Simple Execution Loop"
echo "========================================"
echo "Started at: $(date)"
echo "Interval: ${INTERVAL}s ($(($INTERVAL / 60)) minutes)"
echo "Working directory: $(pwd)"
echo "----------------------------------------"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found at .venv"
    echo "Please run 'uv sync' first"
    exit 1
fi

# Function to run the poller
run_poller() {
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting job ingestion (attempt $((retries + 1))/$MAX_RETRIES)..."

        # Run the Python poller script once
        uv run python simple_poller.py --once

        local exit_code=$?

        if [ $exit_code -eq 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Ingestion successful"
            return 0
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ Ingestion failed with exit code $exit_code"
            retries=$((retries + 1))

            if [ $retries -lt $MAX_RETRIES ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] Retrying in ${RETRY_DELAY}s..."
                sleep $RETRY_DELAY
            fi
        fi
    done

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ Max retries reached, giving up on this cycle"
    return 1
}

# Main loop
iteration=0
while true; do
    iteration=$((iteration + 1))
    echo ""
    echo "========================================"
    echo "Iteration #$iteration"
    echo "========================================"

    run_poller

    # Calculate next run time
    next_run=$(date -v+${INTERVAL}S '+%H:%M:%S' 2>/dev/null || date -d "+${INTERVAL} seconds" '+%H:%M:%S' 2>/dev/null || echo "in ${INTERVAL}s")
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Next run at: $next_run"
    echo "----------------------------------------"

    # Sleep until next cycle
    sleep $INTERVAL
done

echo ""
echo "========================================"
echo "Loop ended at: $(date)"
echo "========================================"
