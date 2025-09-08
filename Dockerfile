# PodcastHarvester Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install yt-dlp (latest version)
RUN pip install --no-cache-dir yt-dlp

# Copy application files
COPY *.py ./
COPY *.sh ./
COPY *.json ./
COPY *.html ./
COPY README.md ./
COPY LICENSE ./

# Make scripts executable
RUN chmod +x *.py *.sh

# Create directories for data persistence
RUN mkdir -p /app/downloads /app/sources /app/config

# Create non-root user for security
RUN useradd -m -u 1000 harvester && \
    chown -R harvester:harvester /app
USER harvester

# Expose port for web application
EXPOSE 8080

# Default command (can be overridden in docker-compose)
CMD ["python3", "podcast_harvester.py", "--help"]
