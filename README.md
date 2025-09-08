# PodcastHarvester

A comprehensive YouTube channel content harvesting system with AI-powered summarization, smart indexing, and web-based management interface.

## 🚀 Key Features

- **Smart Content Harvesting**: Download audio/video from YouTube channels with intelligent indexing
- **AI-Powered Summarization**: Generate comprehensive summaries using local or cloud LLM servers
- **Web Management Interface**: Modern web UI for content management, configuration, and ad-hoc processing
- **Ad-hoc URL Processing**: Process individual YouTube URLs with transcripts and summaries
- **Automatic Progress Tracking**: Real-time progress indicators and status updates
- **Docker Support**: Complete containerized deployment options
- **Configuration Management**: Web-based LLM and channel configuration
- **Transcript Support**: Multi-language subtitle download and processing

## 🎯 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd PodcastHarvester
chmod +x setup.sh
./setup.sh
```

### 2. Configure Channels
```bash
cp channels_config.example.json channels_config.json
# Edit channels_config.json with your YouTube channels
```

### 3. Setup AI Summarization (Optional)
```bash
cp llm_config.example.json llm_config.json
# Edit llm_config.json with your LLM server details
```

### 4. Start Web Interface
```bash
./start_web_app.sh
# Open http://localhost:8080 in your browser
```

### 5. Run Your First Harvest
- Use the web interface Settings → Process URL for individual videos
- Or run batch processing: `python3 podcast_harvester.py --config channels_config.json`

## 🐳 Docker Quick Start

```bash
# Start web interface
docker-compose up --build

# Run content harvesting
docker-compose -f docker-compose.download.yml up --build

# Generate AI summaries
docker-compose -f docker-compose.summary.yml up --build
```

## 📖 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Configuration Guide](docs/CONFIGURATION.md)** - Channel and LLM configuration
- **[Web Interface Guide](docs/WEB_INTERFACE.md)** - Using the web management interface
- **[Docker Deployment](docs/DOCKER.md)** - Container deployment options
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🛠️ Core Components

- **`podcast_harvester.py`** - Main content harvesting engine
- **`content_server.py`** - Web application backend
- **`content_viewer.html`** - Modern web interface
- **`content_summarizer.py`** - AI summarization engine

## 📊 System Requirements

- Python 3.6+
- yt-dlp
- Optional: Docker for containerized deployment
- Optional: Local LLM server for AI summarization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Check the [FAQ](docs/FAQ.md) for common questions
- Review [Troubleshooting](docs/TROUBLESHOOTING.md) for issues
- Open an issue for bugs or feature requests

---

**💡 Pro Tip**: Start with the test configuration (`test_channels.json`) to familiarize yourself with the system before processing large channel lists.
