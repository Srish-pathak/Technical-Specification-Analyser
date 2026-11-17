# =========================================================================
# Dockerfile for TechSpecAnalyser Deployment on Render
# =========================================================================
FROM python:3.12-slim

WORKDIR /app

# Install curl for Render health check probing
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend and frontend source code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Ensure directory for SQLite database exists
RUN mkdir -p /app/backend/data

# Environment configuration
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV TSA_DB_PATH=/app/backend/data/techspecanalyser.db
EXPOSE 8000

# Start Uvicorn bound to 0.0.0.0 and dynamic $PORT provided by Render
WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
