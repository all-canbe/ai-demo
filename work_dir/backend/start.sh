#!/bin/bash

echo "Starting Document Analyzer API..."

if [ "$1" == "worker" ]; then
    echo "Starting Celery worker..."
    celery -A app.celery worker --loglevel=info --concurrency=4
elif [ "$1" == "beat" ]; then
    echo "Starting Celery beat..."
    celery -A app.celery beat --loglevel=info
elif [ "$1" == "flower" ]; then
    echo "Starting Flower..."
    celery -A app.celery flower --port=5555
else
    echo "Starting FastAPI server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
