# =============================================================================
# Multi-stage Dockerfile — Production hardened
# =============================================================================

# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# =============================================================================
# Production stage — minimal attack surface
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (no gcc/build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/false -u 1000 django

# Copy installed packages from builder
COPY --from=builder /root/.local /home/django/.local

# Add to PATH
ENV PATH=/home/django/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy application code
COPY . .

# Collect static files at build time
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Change ownership
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Run with Gunicorn (overridable via docker-compose command)
CMD ["gunicorn", "politicians_tracker.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "gthread", \
     "--threads", "4", \
     "--timeout", "30", \
     "--keep-alive", "75"]
