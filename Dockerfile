# ============================================
# Root Dockerfile for Railway - Monorepo setup - Force rebuild
# ============================================

FROM python:3.11-slim

# Copy the entire project
COPY . .

# Copy requirements.txt to root for easier access
RUN cp /backend/requirements.txt /requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# Change to backend directory for the build
WORKDIR /backend

# Expose port
EXPOSE 8000

# Start the application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]