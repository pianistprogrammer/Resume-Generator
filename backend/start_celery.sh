#!/bin/bash

# Start Celery Worker and Beat Scheduler
# This script starts both the worker and beat scheduler in the background

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A app.workers.celery_worker worker --loglevel=info --concurrency=4 > celery_worker.log 2>&1 &
WORKER_PID=$!
echo "Celery worker started with PID: $WORKER_PID"

# Start Celery beat scheduler in background
echo "Starting Celery beat scheduler..."
celery -A app.workers.celery_worker beat --loglevel=info > celery_beat.log 2>&1 &
BEAT_PID=$!
echo "Celery beat scheduler started with PID: $BEAT_PID"

# Save PIDs to file for easy stopping
echo $WORKER_PID > celery_worker.pid
echo $BEAT_PID > celery_beat.pid

echo ""
echo "Celery services started successfully!"
echo "Worker PID: $WORKER_PID (log: celery_worker.log)"
echo "Beat PID: $BEAT_PID (log: celery_beat.log)"
echo ""
echo "To stop Celery services, run: ./stop_celery.sh"
echo "To view logs: tail -f celery_worker.log celery_beat.log"
