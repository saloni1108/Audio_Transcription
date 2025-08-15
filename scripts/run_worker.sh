#!/usr/bin/env bash
set -e

echo "Starting Celery worker..."
celery -A darwix_ai worker -l INFO

chmod +x scripts/run_worker.sh
echo "Celery worker started successfully."