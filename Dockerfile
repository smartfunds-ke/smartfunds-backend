# Multi-stage build for production
FROM python:3.11-slim as builder

# Build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=smartfunds.settings.production

WORKDIR /app

# Copy application code
COPY --chown=django:django . .
COPY --chown=django:django ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create directories for static and media files
RUN mkdir -p /app/static /app/media && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=10)" || exit 1

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]