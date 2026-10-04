# Stage 1: Build Frontend
FROM node:20-slim AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend & Runtime
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
