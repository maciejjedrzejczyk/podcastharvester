# Frequently Asked Questions (FAQ)

## General Questions

### What is PodcastHarvester?

PodcastHarvester is a comprehensive system for downloading, organizing, and summarizing YouTube channel content. It provides automated content harvesting with AI-powered summarization and a modern web interface for management.

### What can I download with PodcastHarvester?

- **YouTube channels**: Entire channels or content after a specific date
- **Individual videos**: Ad-hoc processing of single YouTube URLs
- **Audio or video**: Choose format based on your needs
- **Transcripts**: Multi-language subtitle support
- **Metadata**: Video descriptions, thumbnails, and information

### Do I need technical knowledge to use this?

Basic technical knowledge is helpful, but the system includes:
- Automated setup scripts
- Web-based configuration interface
- Docker deployment options
- Comprehensive documentation

## Installation & Setup

### What are the system requirements?

**Minimum Requirements:**
- Python 3.6+
- 2GB RAM
- 10GB free disk space
- Internet connection

**Recommended:**
- Python 3.9+
- 8GB RAM
- 100GB+ free disk space (for content storage)
- Fast internet connection

### How do I install PodcastHarvester?

1. Clone the repository
2. Run `./setup.sh` for automated setup
3. Configure channels in `channels_config.json`
4. Start with `./start_web_app.sh`

See the [Installation Guide](INSTALLATION.md) for detailed instructions.

### Can I use Docker?

Yes! Docker deployment is fully supported:
```bash
docker-compose up --build
```

Multiple Docker configurations are available for different use cases.

## Configuration

### How do I add YouTube channels?

**Method 1: Web Interface**
1. Open web interface
2. Click Settings → Add Channel
3. Fill in channel details
4. Click Add Channel

**Method 2: Configuration File**
Edit `channels_config.json` and add channel objects.

### What's the difference between audio and video downloads?

- **Audio**: Downloads best quality audio (MP3), smaller files, ideal for podcasts
- **Video**: Downloads best quality video, larger files, preserves visual content

### How do I set up AI summarization?

1. Install a local LLM server (Ollama, LM Studio, etc.)
2. Configure `llm_config.json` with server details
3. Set `"summarize": "yes"` for desired channels
4. Run content summarization

### Can I use cloud AI services?

Yes! The system supports any OpenAI-compatible API:
- OpenAI GPT models
- Anthropic Claude
- Custom API endpoints

## Usage

### How do I download content from a channel?

**Web Interface:**
1. Configure channels in Settings
2. Use batch download feature
3. Monitor progress indicator

**Command Line:**
```bash
python3 podcast_harvester.py --config channels_config.json
```

### How do I process a single YouTube video?

Use the web interface:
1. Click Settings → Process URL
2. Paste YouTube URL
3. Choose options (audio/video, transcript, summary)
4. Click Process URL

### How long does processing take?

**Download times:**
- Audio: 1-5 minutes per hour of content
- Video: 5-15 minutes per hour of content

**Summarization times:**
- 2-10 minutes per video (depends on length and LLM speed)

### Can I pause and resume downloads?

The system is designed to resume interrupted downloads automatically. It tracks what's already downloaded and skips existing content.

## AI Summarization

### What LLM servers are supported?

**Local Servers:**
- Ollama
- LM Studio
- text-generation-webui
- vLLM

**Cloud Services:**
- OpenAI API
- Any OpenAI-compatible endpoint

### How accurate are the AI summaries?

Summary quality depends on:
- LLM model quality
- Transcript accuracy
- Content complexity
- Prompt configuration

Generally, summaries are quite good for clear audio content with good transcripts.

### Can I customize the summarization prompts?

Yes! Edit the `system_prompts` section in `llm_config.json` to customize how summaries are generated.

### Why are some videos not summarized?

Common reasons:
- No transcript available
- Transcript language not supported
- LLM server connection issues
- Content too short/long for processing

## Web Interface

### How do I access the web interface?

1. Start the server: `./start_web_app.sh`
2. Open browser to `http://localhost:8080`

### Can I access it from other devices?

Yes! Start with external access:
```bash
./start_web_app.sh --host 0.0.0.0
```
Then access via your computer's IP address.

### The web interface is slow. How can I improve performance?

- Use content filters to reduce displayed items
- Close expanded content cards
- Clear browser cache
- Ensure adequate system resources

## Troubleshooting

### Downloads are failing. What should I check?

1. **Internet connection**: Ensure stable connection
2. **yt-dlp version**: Update with `pip install -U yt-dlp`
3. **Disk space**: Ensure adequate free space
4. **Channel availability**: Verify channels are accessible
5. **Configuration**: Check JSON syntax and required fields

### AI summarization isn't working. What's wrong?

1. **LLM server**: Verify server is running and accessible
2. **Configuration**: Check `llm_config.json` settings
3. **Transcripts**: Ensure videos have available transcripts
4. **Model compatibility**: Verify model supports your requests

### The web interface won't load. How do I fix it?

1. **Server status**: Ensure server is running
2. **Port conflicts**: Try different port with `--port 8081`
3. **Browser cache**: Clear cache or try incognito mode
4. **Firewall**: Check firewall isn't blocking the port

### I'm getting "permission denied" errors. How do I fix this?

```bash
# Make scripts executable
chmod +x *.py *.sh

# Fix file permissions
sudo chown -R $USER:$USER downloads/
```

## Performance & Storage

### How much disk space do I need?

**Estimates per hour of content:**
- Audio (MP3): 50-100MB
- Video (1080p): 500MB-2GB
- Transcripts: 1-5MB
- Summaries: <1MB

Plan accordingly based on your channel list and content volume.

### Can I store content on external drives?

Yes! Configure custom output directories:
```json
"output_directory": "/external/drive/downloads/Channel_Name"
```

### How do I clean up old content?

Use the web interface delete functions:
- **Delete Media**: Removes audio/video, keeps metadata
- **Delete Folder**: Removes everything

Or manually delete folders from the downloads directory.

## Advanced Usage

### Can I run this on a server?

Yes! The system is designed for server deployment:
- Use Docker for containerized deployment
- Configure external access with `--host 0.0.0.0`
- Consider reverse proxy (nginx) for production

### How do I backup my configuration?

Backup these files:
- `channels_config.json`
- `llm_config.json`
- `downloads/` directory (content)

### Can I integrate this with other systems?

Yes! The system provides:
- REST API for integration
- JSON configuration files
- Command-line interfaces
- Docker deployment options

### How do I contribute to the project?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See the project README for contribution guidelines.

## Getting Help

### Where can I get support?

1. Check this FAQ
2. Review the [Troubleshooting Guide](TROUBLESHOOTING.md)
3. Search existing GitHub issues
4. Open a new issue with detailed information

### How do I report bugs?

Open a GitHub issue with:
- System information (OS, Python version)
- Steps to reproduce
- Error messages
- Configuration files (remove sensitive data)

### Can I request new features?

Yes! Open a GitHub issue with:
- Feature description
- Use case explanation
- Implementation suggestions (if any)
