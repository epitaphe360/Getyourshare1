# Root Dockerfile for Railway - Monorepo setup
FROM python:3.11-slim

# Copy the entire project
COPY . .

# Install dependencies from backend directory
RUN pip install --no-cache-dir -r backend/requirements.txt

# Change to backend directory
WORKDIR /backend

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "server_complete:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]

