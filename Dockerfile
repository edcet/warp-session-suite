# Multi-stage Dockerfile for Unified Terminal Automation System
FROM ubuntu:22.04 as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    ca-certificates gnupg lsb-release \
    software-properties-common \
    pkg-config libssl-dev \
    python3-pip python3-venv \
    nodejs npm \
    sqlite3 \
    fd-find ripgrep bat \
    direnv \
    && rm -rf /var/lib/apt/lists/*

# Install mise
RUN curl https://mise.run | sh
ENV PATH="/root/.local/bin:$PATH"

# Install tools
COPY .tool-versions .
RUN mise install

FROM base as runtime

WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt || true

# Install plugins
RUN python3 -c "from plugins.registry import install_all; install_all()" || true

# Setup configuration
RUN python3 plugins/code_quality/src/main.py install || true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 unified_cli.py system status || exit 1

# Default command
CMD ["python3", "unified_cli.py", "system", "monitor"]

EXPOSE 8080 8443
