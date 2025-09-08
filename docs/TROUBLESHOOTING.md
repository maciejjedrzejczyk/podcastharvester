# Troubleshooting Guide

## Installation Issues

### Python Version Problems

**Problem**: `python3: command not found` or version conflicts

**Solutions:**
```bash
# Check Python version
python3 --version

# Install Python 3 (Ubuntu/Debian)
sudo apt update && sudo apt install python3 python3-pip

# Install Python 3 (macOS)
brew install python3

# Use specific Python version
python3.9 -m venv venv
```

### yt-dlp Installation Issues

**Problem**: `yt-dlp: command not found` or outdated version

**Solutions:**
```bash
# Install/update yt-dlp
pip install -U yt-dlp

# Alternative installation
python3 -m pip install -U yt-dlp

# System-wide installation (macOS)
brew install yt-dlp

# Verify installation
yt-dlp --version
```

### Permission Denied Errors

**Problem**: Scripts not executable or file permission issues

**Solutions:**
```bash
# Make scripts executable
chmod +x *.py *.sh

# Fix ownership of downloads directory
sudo chown -R $USER:$USER downloads/

# Fix permissions recursively
chmod -R 755 downloads/
```

### Virtual Environment Issues

**Problem**: Virtual environment activation fails or packages not found

**Solutions:**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Windows activation
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

## Configuration Issues

### Invalid JSON Configuration

**Problem**: JSON syntax errors in configuration files

**Solutions:**
```bash
# Validate JSON syntax
python3 -m json.tool channels_config.json
python3 -m json.tool llm_config.json

# Common JSON errors to check:
# - Missing commas between objects
# - Trailing commas
# - Unescaped quotes in strings
# - Missing closing brackets/braces
```

### Channel Configuration Errors

**Problem**: Channels not downloading or configuration not recognized

**Solutions:**
```bash
# Verify required fields are present
# Required: url, channel_name, content_type, cutoff_date

# Check channel URL format
# Correct: https://www.youtube.com/@channelname
# Incorrect: https://www.youtube.com/c/channelname

# Validate date format (YYYY-MM-DD)
"cutoff_date": "2025-01-01"  # Correct
"cutoff_date": "01/01/2025"  # Incorrect
```

### LLM Configuration Problems

**Problem**: AI summarization not working or connection errors

**Solutions:**
```bash
# Test LLM server connection
curl http://localhost:1234/v1/models

# Common LLM server URLs:
# Ollama: http://localhost:11434
# LM Studio: http://localhost:1234
# text-generation-webui: http://localhost:5000

# Verify model name matches server
# Check server logs for model availability
```

## Download Issues

### Network Connection Problems

**Problem**: Downloads failing with network errors

**Solutions:**
```bash
# Test internet connection
ping google.com

# Test YouTube access
yt-dlp --list-formats "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Use proxy if needed
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

### YouTube API Rate Limiting

**Problem**: Downloads slow or failing due to rate limits

**Solutions:**
```bash
# Add delays between downloads (built into system)
# Use --max-channels to limit concurrent processing
python3 podcast_harvester.py --config channels_config.json --max-channels 3

# Check for yt-dlp updates
pip install -U yt-dlp
```

### Disk Space Issues

**Problem**: Downloads failing due to insufficient disk space

**Solutions:**
```bash
# Check available disk space
df -h

# Check downloads directory size
du -sh downloads/

# Clean up old content
# Use web interface delete functions
# Or manually remove old folders

# Configure custom output directory
"output_directory": "/external/drive/downloads/Channel_Name"
```

### Video Unavailability

**Problem**: Specific videos not downloading

**Solutions:**
```bash
# Check if video is available
yt-dlp --simulate "https://www.youtube.com/watch?v=VIDEO_ID"

# Common reasons for unavailability:
# - Video is private/unlisted
# - Geographic restrictions
# - Age restrictions
# - Video deleted by uploader

# Check channel accessibility
yt-dlp --simulate "https://www.youtube.com/@channelname"
```

## Web Interface Issues

### Server Won't Start

**Problem**: Web server fails to start or crashes

**Solutions:**
```bash
# Check if port is already in use
lsof -i :8080
netstat -tulpn | grep :8080

# Use different port
./start_web_app.sh --port 8081

# Check for Python errors
python3 content_server.py --port 8080

# Verify downloads directory exists
mkdir -p downloads
```

### Settings Button Not Visible

**Problem**: Settings button missing from web interface

**Solutions:**
```bash
# Hard refresh browser
# Chrome/Firefox: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (macOS)

# Clear browser cache
# Or use incognito/private browsing mode

# Check browser console for JavaScript errors
# F12 → Console tab

# Restart web server
pkill -f content_server.py
./start_web_app.sh
```

### Configuration Not Saving

**Problem**: Changes in web interface not persisting

**Solutions:**
```bash
# Check file permissions
ls -la *.json

# Ensure files are writable
chmod 644 channels_config.json llm_config.json

# Check browser console for errors
# F12 → Console tab → look for API errors

# Verify server logs
# Check terminal where web server is running
```

### Media Playback Issues

**Problem**: Audio/video not playing in web interface

**Solutions:**
```bash
# Check browser media support
# Ensure browser supports HTML5 audio/video

# Verify media files exist
ls -la downloads/Channel_Name/Video_Title/

# Check file formats
file downloads/Channel_Name/Video_Title/*.mp3

# Try different browser
# Chrome, Firefox, Safari, Edge
```

## AI Summarization Issues

### LLM Server Connection Failed

**Problem**: Cannot connect to LLM server

**Solutions:**
```bash
# Verify server is running
# Ollama: ollama serve
# LM Studio: Start server in LM Studio app

# Test connection manually
curl http://localhost:1234/v1/models

# Check firewall settings
# Ensure port is not blocked

# Verify server URL in config
# Check llm_config.json server_url field
```

### No Transcripts Found

**Problem**: Summarization skips videos due to missing transcripts

**Solutions:**
```bash
# Check if transcripts were downloaded
ls -la downloads/Channel_Name/Video_Title/*.srt

# Verify transcript languages in config
"transcript_languages": ["en", "pl"]

# Some videos may not have transcripts available
# Check YouTube video manually for captions

# Re-download with transcript options
python3 podcast_harvester.py --config channels_config.json --force-reindex
```

### Summarization Takes Too Long

**Problem**: AI summarization is very slow or hangs

**Solutions:**
```bash
# Check LLM server performance
# Monitor CPU/memory usage during summarization

# Reduce context length
"context_length": 2048  # Instead of 4096

# Use faster model
# Smaller models process faster but may be less accurate

# Process fewer channels at once
python3 content_summarizer.py --config channels_config.json --channels "SingleChannel"
```

### Poor Summary Quality

**Problem**: AI summaries are inaccurate or unhelpful

**Solutions:**
```bash
# Try different model
# Larger models generally produce better summaries

# Adjust temperature
"temperature": 0.3  # More focused (less creative)
"temperature": 0.9  # More creative (less focused)

# Check transcript quality
# Poor transcripts lead to poor summaries

# Customize system prompts in llm_config.json
```

## Docker Issues

### Container Build Failures

**Problem**: Docker build fails or takes too long

**Solutions:**
```bash
# Clean Docker cache
docker system prune -f

# Rebuild without cache
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test .

# Verify base image availability
docker pull python:3.9-slim
```

### Volume Mount Issues

**Problem**: Files not accessible in container or permission errors

**Solutions:**
```bash
# Fix file ownership
sudo chown -R $USER:$USER downloads/

# Use user mapping
docker-compose run --user $(id -u):$(id -g) podcast-harvester-download

# Check volume mounts
docker-compose config

# Verify paths exist
mkdir -p downloads config
```

### Port Conflicts

**Problem**: Port already in use errors

**Solutions:**
```bash
# Find process using port
lsof -i :8080

# Kill process if needed
kill -9 PID

# Use different port
docker-compose up -p 8081:8080

# Check Docker port mapping
docker ps
```

## Performance Issues

### Slow Downloads

**Problem**: Content downloads are very slow

**Solutions:**
```bash
# Check internet speed
speedtest-cli

# Limit concurrent downloads
python3 podcast_harvester.py --config channels_config.json --max-channels 2

# Use audio instead of video
"content_type": "audio"  # Faster downloads

# Check system resources
top
htop
```

### High Memory Usage

**Problem**: System running out of memory during processing

**Solutions:**
```bash
# Monitor memory usage
free -h
htop

# Process fewer channels at once
--max-channels 1

# Close other applications
# Ensure adequate RAM available

# Use Docker with memory limits
docker run --memory=2g podcast-harvester
```

### Disk I/O Issues

**Problem**: Slow file operations or disk errors

**Solutions:**
```bash
# Check disk health
sudo fsck /dev/sda1

# Monitor disk I/O
iotop
iostat

# Use faster storage (SSD)
# Move downloads to faster drive

# Check available inodes
df -i
```

## Debugging Tips

### Enable Verbose Logging

```bash
# Run with debug output
python3 podcast_harvester.py --config channels_config.json --verbose

# Check system logs
tail -f /var/log/syslog

# Monitor network activity
netstat -tulpn
```

### Collect Debug Information

```bash
# System information
uname -a
python3 --version
yt-dlp --version

# Configuration validation
python3 -m json.tool channels_config.json
python3 -m json.tool llm_config.json

# File permissions
ls -la *.json *.py *.sh
ls -la downloads/
```

### Test Individual Components

```bash
# Test channel listing
python3 list_channels.py --search "test"

# Test single channel download
python3 podcast_harvester.py --config test_channels.json --max-channels 1

# Test LLM connection
python3 content_summarizer.py --config test_channels.json --channels "test"

# Test web server
python3 content_server.py --port 8080
```

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Review the [FAQ](FAQ.md)
3. Search existing GitHub issues
4. Try the suggested solutions

### When Reporting Issues

Include this information:
- Operating system and version
- Python version (`python3 --version`)
- yt-dlp version (`yt-dlp --version`)
- Error messages (full text)
- Configuration files (remove sensitive data)
- Steps to reproduce the issue

### Useful Commands for Bug Reports

```bash
# System information
uname -a
python3 --version
yt-dlp --version
docker --version

# Configuration validation
python3 -m json.tool channels_config.json

# Test basic functionality
python3 podcast_harvester.py --config test_channels.json --max-channels 1
```
