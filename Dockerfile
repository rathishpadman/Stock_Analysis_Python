# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_agents.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_agents.txt

# Copy the application code
COPY nifty_agents/ ./nifty_agents/

# Create logs directory
RUN mkdir -p /app/nifty_agents/logs

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD exec uvicorn nifty_agents.api:app --host 0.0.0.0 --port ${PORT}
