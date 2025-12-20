# Multi-stage Dockerfile for Awesome Skills Platform Backend
# Optimized for production deployment to AWS ECS Fargate

# Stage 1: Base Python image with uv
FROM python:3.12-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 3: Application
FROM base as application

# Copy virtual environment from dependencies stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy application code
COPY src/ /app/src/
COPY scripts/ /app/scripts/

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Set Python path
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
