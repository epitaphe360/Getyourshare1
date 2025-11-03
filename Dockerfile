# ============================================
# GetYourShare - Production Dockerfile
# Optimized for Railway deployment
# ============================================

FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire repository into the /app directory
COPY . .

# Now, set the working directory to the backend subfolder
WORKDIR /app/backend

# Install Python dependencies from requirements.txt located in the backend folder
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories if they don't exist
RUN mkdir -p uploads logs invoices

# Set environment variables for the container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose the port. Railway will automatically map this.
EXPOSE 8000

# The command to run the application
# This is executed from the /app/backend directory
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]


