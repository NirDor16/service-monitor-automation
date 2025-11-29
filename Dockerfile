# Base image: official lightweight Python
FROM python:3.12-slim

# Install missing system-level tools (including ping)
RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping && \
    rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . /app

# Make sure the bash script is executable (on Linux)
RUN chmod +x scripts/run_checks.sh || true

# Default command: run all checks (API, network, pytest)
CMD ["bash", "scripts/run_checks.sh"]
