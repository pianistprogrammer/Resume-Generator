#!/bin/bash

# Stop Celery Worker and Beat Scheduler

cd "$(dirname "$0")"

# Stop worker
if [ -f celery_worker.pid ]; then
    WORKER_PID=$(cat celery_worker.pid)
    echo "Stopping Celery worker (PID: $WORKER_PID)..."
    kill $WORKER_PID 2>/dev/null && echo "Worker stopped" || echo "Worker not running"
    rm celery_worker.pid
fi

# Stop beat
if [ -f celery_beat.pid ]; then
    BEAT_PID=$(cat celery_beat.pid)
    echo "Stopping Celery beat (PID: $BEAT_PID)..."
    kill $BEAT_PID 2>/dev/null && echo "Beat scheduler stopped" || echo "Beat scheduler not running"
    rm celery_beat.pid
fi

# Also kill any remaining celery processes
pkill -f "celery.*celery_worker" 2>/dev/null

echo "Celery services stopped"
