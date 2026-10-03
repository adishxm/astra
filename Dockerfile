# ASTRA - Enterprise Cryptographic Discovery & Analysis Tool (SIH26164 ECDAT)
FROM python:3.10-slim

WORKDIR /app

# Install system utilities needed for safe extraction and crypto
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code and config
COPY backend/ ./backend/
COPY pytest.ini pyproject.toml ./

ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Non-root user for security sandbox containment
RUN useradd -m -u 1000 astra && \
    mkdir -p /app/temp_scans /app/sandbox_tmp && \
    chown -R astra:astra /app

USER astra

EXPOSE 8000

CMD ["python", "-m", "pytest", "backend/tests", "-v"]
