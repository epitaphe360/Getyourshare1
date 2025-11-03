# ============================================# Root Dockerfile for Railway - Monorepo setup - Force rebuild

# Dockerfile - Root Level for Railway Backend ServiceFROM python:3.11-slim

# ============================================

FROM python:3.11-slim# Copy the entire project

COPY . .

# Copy the entire project

COPY . .# Install dependencies from backend directory

RUN pip install --no-cache-dir -r backend/requirements.txt

# Change to backend directory for the build

WORKDIR /backend# Change to backend directory

WORKDIR /backend

# Install dependencies

RUN pip install --no-cache-dir -r requirements.txt# Expose port

EXPOSE 8000

# Expose port

EXPOSE 8000# Run the application

CMD ["uvicorn", "server_complete:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]

# Start the application

CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]