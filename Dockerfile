# Stage 1: Build Frontend
FROM node:20-slim AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Test Environment Target
FROM python:3.10-slim AS test

WORKDIR /app

# Install system utilities and nodejs required for frontend semantic AST tests
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications and install test requirements
COPY requirements.txt pyproject.toml pytest.ini ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pytest pytest-cov httpx

# Copy full repository source required by test suite
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY README.md LICENSE Dockerfile ./
COPY scripts/ ./scripts/
COPY examples/ ./examples/

# Copy compiled frontend assets into frontend/dist for static contract tests
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 1000 astra && \
    mkdir -p /app/temp_scans /app/sandbox_tmp && \
    chown -R astra:astra /app

USER astra

CMD ["python", "-m", "pytest", "backend/tests", "-v"]

# Stage 3: Minimal Production Runtime Target (Default)
FROM python:3.10-slim AS runtime

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

# Copy compiled frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 1000 astra && \
    mkdir -p /app/temp_scans /app/sandbox_tmp && \
    chown -R astra:astra /app

USER astra

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
