# Docker Deployment Guide

## Overview

PodcastHarvester supports comprehensive Docker deployment with multiple configurations for different use cases.

## Quick Start

### Basic Web Interface

```bash
# Start web UI
docker-compose up --build

# Access at http://localhost:8080
```

### Complete Setup

```bash
# Clone repository
git clone <repository-url>
cd PodcastHarvester

# Copy configurations
cp channels_config.example.json channels_config.json
cp llm_config.example.json llm_config.json

# Edit configurations as needed
# Start all services
docker-compose up --build
```

## Docker Configurations

### 1. Web UI Mode (Default)

**File**: `docker-compose.yml`

```yaml
services:
  podcast-harvester-ui:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./downloads:/app/downloads
      - ./channels_config.json:/app/channels_config.json:ro
    command: python3 content_server.py --host 0.0.0.0 --port 8080
```

**Usage:**
```bash
docker-compose up --build
```

### 2. Download Mode

**File**: `docker-compose.download.yml`

```yaml
services:
  podcast-harvester-download:
    build: .
    volumes:
      - ./downloads:/app/downloads
      - ./channels_config.json:/app/channels_config.json:ro
    command: python3 podcast_harvester.py --config channels_config.json
```

**Usage:**
```bash
# Download all channels
docker-compose -f docker-compose.download.yml up --build

# Download specific channels
docker-compose -f docker-compose.download.yml run podcast-harvester-download \
  python3 podcast_harvester.py --config channels_config.json --channels "MKBHD,TechLinked"
```

### 3. Summarization Mode

**File**: `docker-compose.summary.yml`

```yaml
services:
  content-summarizer:
    build: .
    volumes:
      - ./downloads:/app/downloads
      - ./channels_config.json:/app/channels_config.json:ro
      - ./llm_config.json:/app/llm_config.json:ro
    command: python3 content_summarizer.py --config channels_config.json
```

**Usage:**
```bash
# Summarize all channels with summarize="yes"
docker-compose -f docker-compose.summary.yml up --build

# Summarize specific channels
docker-compose -f docker-compose.summary.yml run content-summarizer \
  python3 content_summarizer.py --config channels_config.json --channels "MKBHD"
```

### 4. Production UI Mode

**File**: `docker-compose.ui.yml`

```yaml
services:
  podcast-harvester-ui:
    build: .
    ports:
      - "80:8080"
    volumes:
      - ./downloads:/app/downloads
      - ./channels_config.json:/app/channels_config.json:ro
      - ./llm_config.json:/app/llm_config.json:ro
    environment:
      - PODCAST_HARVESTER_HOST=0.0.0.0
      - PODCAST_HARVESTER_PORT=8080
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - podcast-harvester-ui
    profiles: ["production"]
```

**Usage:**
```bash
# Basic production
docker-compose -f docker-compose.ui.yml up --build

# With nginx reverse proxy
docker-compose -f docker-compose.ui.yml --profile production up --build
```

## Advanced Docker Usage

### Custom Commands

```bash
# Interactive shell
docker run --rm -it -v $(pwd):/app/host podcast-harvester bash

# One-time download with custom parameters
docker run --rm \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/channels_config.json:/app/channels_config.json:ro \
  podcast-harvester \
  python3 podcast_harvester.py --config channels_config.json --max-channels 5

# Custom web server port
docker run --rm -p 9000:9000 \
  -v $(pwd)/downloads:/app/downloads \
  podcast-harvester \
  python3 content_server.py --host 0.0.0.0 --port 9000
```

### Multi-Stage Builds

The Dockerfile uses multi-stage builds for optimization:

```dockerfile
# Build stage
FROM python:3.9-slim as builder
# ... build dependencies

# Runtime stage
FROM python:3.9-slim
# ... runtime setup
```

### Volume Management

**Persistent Volumes:**
```yaml
volumes:
  - ./downloads:/app/downloads          # Content storage
  - ./config:/app/config               # Runtime config
  - ./channels_config.json:/app/channels_config.json:ro  # Channel list
  - ./llm_config.json:/app/llm_config.json:ro           # LLM settings
```

**Named Volumes:**
```yaml
volumes:
  podcast_downloads:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/downloads
```

## Environment Variables

Configure container behavior:

```yaml
environment:
  - PYTHONUNBUFFERED=1                    # Real-time output
  - PODCAST_HARVESTER_HOST=0.0.0.0       # Server host
  - PODCAST_HARVESTER_PORT=8080          # Server port
  - PODCAST_HARVESTER_DOWNLOADS_DIR=/app/downloads  # Downloads path
```

## Docker Networking

### Internal Communication

Services communicate via Docker's internal network:

```yaml
networks:
  podcast-network:
    driver: bridge

services:
  app:
    networks:
      - podcast-network
```

### External Access

```yaml
ports:
  - "8080:8080"    # Web UI
  - "11434:11434"  # LLM server (if included)
```

## Production Deployment

### With Reverse Proxy

**nginx.conf example:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://podcast-harvester-ui:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL/HTTPS Setup

```yaml
services:
  nginx:
    volumes:
      - ./ssl/cert.pem:/etc/nginx/ssl/cert.pem:ro
      - ./ssl/key.pem:/etc/nginx/ssl/key.pem:ro
```

### Health Checks

```yaml
services:
  podcast-harvester-ui:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/content"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Resource Management

### Memory Limits

```yaml
services:
  podcast-harvester-download:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### CPU Limits

```yaml
services:
  content-summarizer:
    deploy:
      resources:
        limits:
          cpus: '2.0'
```

## Monitoring & Logging

### Log Configuration

```yaml
services:
  podcast-harvester-ui:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Monitoring

```bash
# View logs
docker-compose logs -f

# Monitor resource usage
docker stats

# Check container health
docker-compose ps
```

## Backup & Recovery

### Data Backup

```bash
# Backup downloads
docker run --rm -v podcast_downloads:/data -v $(pwd):/backup alpine \
  tar czf /backup/downloads-backup.tar.gz -C /data .

# Backup configurations
cp channels_config.json config-backup/
cp llm_config.json config-backup/
```

### Recovery

```bash
# Restore downloads
docker run --rm -v podcast_downloads:/data -v $(pwd):/backup alpine \
  tar xzf /backup/downloads-backup.tar.gz -C /data

# Restore configurations
cp config-backup/channels_config.json .
cp config-backup/llm_config.json .
```

## Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Use different port
docker-compose up --build -p 8081:8080
```

**Permission issues:**
```bash
# Fix ownership
sudo chown -R $USER:$USER downloads/

# Run with user mapping
docker-compose run --user $(id -u):$(id -g) podcast-harvester-download
```

**Storage issues:**
```bash
# Check disk usage
docker system df

# Clean up
docker system prune -f
docker volume prune -f
```

### Debugging

```bash
# Interactive debugging
docker-compose run --rm podcast-harvester-ui bash

# Check logs
docker-compose logs podcast-harvester-ui

# Inspect container
docker inspect podcast-harvester_podcast-harvester-ui_1
```

## Performance Optimization

### Build Optimization

```dockerfile
# Use .dockerignore
echo "downloads/" >> .dockerignore
echo "venv/" >> .dockerignore
echo "__pycache__/" >> .dockerignore

# Multi-stage builds
FROM python:3.9-slim as base
# ... common setup

FROM base as development
# ... dev dependencies

FROM base as production
# ... production setup
```

### Runtime Optimization

```yaml
services:
  podcast-harvester-ui:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
```

## Security Considerations

### Container Security

```yaml
services:
  podcast-harvester-ui:
    user: "1000:1000"  # Non-root user
    read_only: true     # Read-only filesystem
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
```

### Network Security

```yaml
networks:
  podcast-network:
    driver: bridge
    internal: true  # No external access
```

### Secrets Management

```yaml
secrets:
  llm_config:
    file: ./llm_config.json

services:
  content-summarizer:
    secrets:
      - llm_config
```
