# Installation Guide

## Prerequisites

### System Requirements
- **Python 3.6+**
- **yt-dlp** (for YouTube content download)
- **ffprobe** (for media duration analysis)
- **Git** (for cloning the repository)

### Optional Requirements
- **Docker** (for containerized deployment)
- **LLM Server** (Ollama, LM Studio, or OpenAI-compatible API for AI summarization)

## Installation Methods

### Method 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd PodcastHarvester

# Run automated setup
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install required dependencies
- Set up example configurations
- Make scripts executable

### Method 2: Manual Setup

```bash
# Clone the repository
git clone <repository-url>
cd PodcastHarvester

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install yt-dlp

# Make scripts executable
chmod +x *.py *.sh

# Copy configuration examples
cp channels_config.example.json channels_config.json
cp llm_config.example.json llm_config.json
```

### Method 3: Docker Installation

```bash
# Clone the repository
git clone <repository-url>
cd PodcastHarvester

# Build and start with Docker Compose
docker-compose up --build
```

## Post-Installation Setup

### 1. Configure Channels
Edit `channels_config.json` with your desired YouTube channels:

```json
[
  {
    "url": "https://www.youtube.com/@channelname",
    "channel_name": "Channel_Name",
    "content_type": "audio",
    "cutoff_date": "2025-01-01",
    "summarize": "yes"
  }
]
```

### 2. Setup LLM Server (Optional)
For AI summarization, configure `llm_config.json`:

```json
{
  "server_url": "http://localhost:1234",
  "model_name": "your-model-name",
  "context_length": 4096,
  "temperature": 0.7
}
```

### 3. Test Installation
```bash
# Test with sample configuration
python3 podcast_harvester.py --config test_channels.json --max-channels 1

# Start web interface
./start_web_app.sh
```

## Verification

### Check Dependencies
```bash
# Verify yt-dlp installation
yt-dlp --version

# Verify Python version
python3 --version

# Test ffprobe (part of ffmpeg)
ffprobe -version
```

### Test Basic Functionality
```bash
# Test channel listing
python3 list_channels.py --search "tech"

# Test web server
./start_web_app.sh
# Open http://localhost:8080
```

## Troubleshooting Installation

### Common Issues

**yt-dlp not found:**
```bash
pip install yt-dlp
# or
brew install yt-dlp  # macOS
```

**Permission denied:**
```bash
chmod +x *.py *.sh
```

**Python version issues:**
```bash
# Use specific Python version
python3.9 -m venv venv
```

**Virtual environment activation:**
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

## Next Steps

After successful installation:
1. Review the [Configuration Guide](CONFIGURATION.md)
2. Explore the [Web Interface Guide](WEB_INTERFACE.md)
3. Check the [FAQ](FAQ.md) for common questions
