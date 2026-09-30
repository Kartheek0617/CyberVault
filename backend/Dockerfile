FROM python:3.10-slim

WORKDIR /app

# Upgrade packages and install minimal requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Add non-root user (Security Best Practice)
RUN groupadd -r cybervault && useradd -r -g cybervault cybervault

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ensure storage directories exist and have proper permissions
RUN mkdir -p /app/evidence_storage
RUN chown -R cybervault:cybervault /app

# Switch to non-root user
USER cybervault

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
