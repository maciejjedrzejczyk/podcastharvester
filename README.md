# PodcastHarvester

A comprehensive YouTube channel content harvesting system with AI-powered summarization, smart indexing, and web-based management interface.

## 🚀 Quick Setup

### 1. Install & Configure
```bash
git clone <repository-url>
cd PodcastHarvester
chmod +x setup.sh
./setup.sh

# Configure your channels
cp config/channels_config.example.json channels_config.json
# Edit channels_config.json with your YouTube channels
```

### 2. Start Web Interface
```bash
./start_web_app.sh
# Open http://localhost:8080 in your browser
```

### 3. Run Content Harvesting
```bash
# Batch processing from config file
python3 podcast_harvester.py --config channels_config.json

# Or use the web interface for individual URLs
```

## 🐳 Docker Quick Start
```bash
docker-compose up --build  # Web interface
docker-compose -f docker-compose.download.yml up --build  # Content harvesting
```

## 🎯 Key Features

- **Smart Content Harvesting** - Download audio/video with intelligent skip logic
- **AI-Powered Summarization** - Generate comprehensive summaries using local/cloud LLM
- **Web Management Interface** - Modern UI for content management and ad-hoc processing
- **RSS Feed Integration** - Automatic feeds for FreshRSS, Audiobookshelf, etc.
- **Smart Indexing System** - Efficient channel indexing with skip functionality
- **Multi-language Transcripts** - Download subtitles in multiple languages
- **Docker Support** - Complete containerized deployment

## 📖 Documentation

### Essential Guides
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup and dependencies
- **[Configuration Guide](docs/CONFIGURATION.md)** - Channel and system configuration
- **[Web Interface Guide](docs/WEB_INTERFACE.md)** - Using the management interface

### Advanced Features
- **[Advanced Features](docs/ADVANCED_FEATURES.md)** - Indexing, notifications, RSS feeds
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System components and workflows
- **[AI Summarization](docs/AI_SUMMARIZATION.md)** - LLM setup and summarization workflow

### Operations & Maintenance
- **[Maintenance Guide](docs/MAINTENANCE.md)** - Operational procedures and troubleshooting
- **[Migration Guide](docs/MIGRATION.md)** - Upgrading and migrating setups
- **[Docker Deployment](docs/DOCKER.md)** - Container deployment options

### Reference
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 📊 System Requirements

- **Python 3.6+** and **yt-dlp** (required)
- **Docker** (optional, for containerized deployment)
- **LLM Server** (optional, for AI summarization)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**💡 Pro Tip**: Start with `test_channels.json` to familiarize yourself with the system before processing large channel lists.
