# Root Dockerfile for Railway - Monorepo setup
FROM python:3.11-slim

# Copy the entire project
COPY . .

# Change to backend directory and install dependencies
WORKDIR /backend
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "server_complete:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]

