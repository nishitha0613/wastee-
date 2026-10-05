# ===================================================
# Dockerfile for Smart Waste Management Backend API
# Multi-stage / optimized slim Python runtime
# ===================================================

FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set working directory inside container
WORKDIR /app

# Install system dependencies (curl for healthchecks, build tools for packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and migrations
COPY . /app

# Ensure uploads directory exists with write permissions
RUN mkdir -p /app/uploads && chmod -R 755 /app/uploads

# Expose backend port
EXPOSE 8000

# Define container health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start container using production startup script
CMD ["/app/start.sh"]
