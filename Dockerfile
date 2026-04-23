# Base slim Python image
FROM python:3.11-slim

LABEL maintainer="omtiwari17"
LABEL project="unified-manufacturing-system"
LABEL version="3.0"

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Ensure artifacts directory exists for Orchestrator
RUN mkdir -p /app/artifacts

# Disable telemetry
ENV CREWAI_TRACING_ENABLED=false
ENV CREWAI_TELEMETRY_ENABLED=false
ENV CREWAI_DISABLE_TELEMETRY=true
ENV OTEL_SDK_DISABLED=true

# Streamlit config
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]