# Installation Guide

## Prerequisites

### System Requirements
- **Python 3.6+**
- **yt-dlp** (for YouTube content download)
- **Git** (for cloning the repository)

### Optional Requirements
- **Docker** (for containerized deployment)
- **LLM Server** (Ollama, LM Studio, or OpenAI-compatible API for AI summarization)

## Quick Installation

### Automated Setup (Recommended)

```bash
# Clone and setup
git clone <repository-url>
cd PodcastHarvester
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install required dependencies (yt-dlp)
- Set up example configurations
- Make scripts executable

### Manual Setup

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
```

## Verification

### Test Installation
```bash
# Check yt-dlp
yt-dlp --version

# Test basic functionality
python3 podcast_harvester.py --help

# Start web interface
./start_web_app.sh
# Open http://localhost:8080
```

### First Run
```bash
# Copy example configuration
cp config/channels_config.example.json channels_config.json

# Edit with your channels
nano channels_config.json

# Test with example channels
python3 podcast_harvester.py --config config/test_channels.json
```

## Docker Installation

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd PodcastHarvester

# Start web interface
docker-compose up --build

# Run content harvesting
docker-compose -f docker-compose.download.yml up --build
```

## Troubleshooting

### Common Issues

**Python not found:**
```bash
# Install Python 3
# Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv
# macOS: brew install python3
# Windows: Download from python.org
```

**yt-dlp installation fails:**
```bash
# Update pip first
pip install --upgrade pip

# Install yt-dlp
pip install yt-dlp

# Alternative: system package manager
# Ubuntu/Debian: sudo apt install yt-dlp
```

**Permission errors:**
```bash
# Fix script permissions
chmod +x *.py *.sh

# Fix directory permissions
chmod -R 755 downloads/
```

## Next Steps

After installation:

1. **Configure Channels** - Edit `channels_config.json` with your YouTube channels
2. **Start Web Interface** - Run `./start_web_app.sh` for the management interface
3. **Run First Harvest** - Execute `python3 podcast_harvester.py --config channels_config.json`

For detailed configuration options, see:
- **[Configuration Guide](CONFIGURATION.md)** - Channel and system setup
- **[Web Interface Guide](WEB_INTERFACE.md)** - Using the management interface
- **[Advanced Features](ADVANCED_FEATURES.md)** - AI summarization, RSS feeds, and more

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
