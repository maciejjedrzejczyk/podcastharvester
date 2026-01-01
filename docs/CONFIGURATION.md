# Configuration Guide

This guide covers basic channel configuration and system setup for PodcastHarvester.

## Channel Configuration

### Basic Setup

Create or edit `channels_config.json`:

```json
[
  {
    "url": "https://www.youtube.com/@channelname",
    "channel_name": "Channel_Name",
    "content_type": "audio",
    "cutoff_date": "2025-01-01",
    "output_format": "%(upload_date)s_%(channel_name)s_%(title)s",
    "output_directory": "downloads/Channel_Name",
    "transcript_languages": ["en", "pl"],
    "redownload_deleted": false,
    "summarize": "yes"
  }
]
```

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `url` | YouTube channel URL | `"https://www.youtube.com/@mkbhd"` |
| `channel_name` | Clean name for directories | `"MKBHD"` |
| `content_type` | Download format | `"audio"` or `"video"` |
| `cutoff_date` | Only download content after this date | `"2025-01-01"` |

### Optional Fields

| Field | Default | Description |
|-------|---------|-------------|
| `output_format` | `"%(upload_date)s_%(channel_name)s_%(title)s"` | Filename template |
| `output_directory` | `"downloads/{channel_name}"` | Target directory |
| `transcript_languages` | `[]` | Subtitle languages to download |
| `download_transcript` | `false` | Enable transcript download |
| `download_metadata` | `true` | Download thumbnails and metadata |
| `redownload_deleted` | `false` | Re-download deleted files |
| `summarize` | `"no"` | Enable AI summarization |
| `generate_rss` | `false` | Generate RSS feeds |
| `send_notification` | `"no"` | Send completion notifications |

### Content Types

**Audio (`"audio"`):**
- Downloads best quality audio (MP3 format)
- Smaller file sizes
- Ideal for podcasts and interviews

**Video (`"video"`):**
- Downloads best quality video
- Larger file sizes
- Preserves visual content

## LLM Configuration (Optional)

For AI summarization, create `llm_config.json`:

```json
{
  "server_url": "http://localhost:1234",
  "model_name": "llama-3.1-8b-instruct",
  "context_length": 4096,
  "temperature": 0.7,
  "request_timeout": 60,
  "max_retries": 3,
  "retry_delay": 2
}
```

### LLM Server Options

**Local Servers:**
- **Ollama**: `http://localhost:11434`
- **LM Studio**: `http://localhost:1234`
- **Text Generation WebUI**: `http://localhost:5000`

**Cloud Services:**
- OpenAI-compatible APIs
- Custom endpoints

## Notification Configuration (Optional)

For webhook notifications, create `notification_config.json`:

```json
{
  "enabled": true,
  "url": "https://your-webhook-url.com/notify",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-token"
  },
  "body_template": {
    "text": "{message}",
    "channel": "#downloads"
  },
  "timeout": 30
}
```

## Example Configurations

### Podcast Channel (Audio Only)
```json
{
  "url": "https://www.youtube.com/@podcastchannel",
  "channel_name": "PodcastChannel",
  "content_type": "audio",
  "cutoff_date": "2024-01-01",
  "download_transcript": true,
  "transcript_languages": ["en"],
  "summarize": "yes",
  "generate_rss": true
}
```

### Educational Channel (Video with Summaries)
```json
{
  "url": "https://www.youtube.com/@educationchannel",
  "channel_name": "EducationChannel",
  "content_type": "video",
  "cutoff_date": "2024-06-01",
  "download_metadata": true,
  "download_transcript": true,
  "transcript_languages": ["en", "es"],
  "summarize": "yes",
  "send_notification": "yes"
}
```

### News Channel (Video Only, No Processing)
```json
{
  "url": "https://www.youtube.com/@newschannel",
  "channel_name": "NewsChannel",
  "content_type": "video",
  "cutoff_date": "2024-12-01",
  "download_metadata": true,
  "summarize": "no",
  "generate_rss": false
}
```

## Configuration Validation

### Test Configuration
```bash
# Validate JSON syntax
python3 -c "import json; json.load(open('channels_config.json'))"

# Test with single channel
python3 podcast_harvester.py --config test_channels.json --max-channels 1
```

### Common Issues

**Invalid JSON:**
- Check for missing commas, quotes, or brackets
- Use a JSON validator online
- Ensure proper escaping of special characters

**Invalid Dates:**
- Use YYYY-MM-DD format only
- Ensure dates are not in the future
- Check for typos in date strings

**Invalid URLs:**
- Use full YouTube channel URLs
- Ensure channels are public and accessible
- Test URLs in browser first

## Advanced Configuration

For advanced features like indexing system configuration, RSS feed customization, and notification templates, see:

- **[Advanced Features](ADVANCED_FEATURES.md)** - Detailed configuration options
- **[AI Summarization](AI_SUMMARIZATION.md)** - LLM setup and prompts
- **[Architecture](ARCHITECTURE.md)** - System configuration details

### Filename Templates

Available variables for `output_format`:
- `%(upload_date)s` - Upload date (YYYYMMDD)
- `%(title)s` - Video title
- `%(uploader)s` - Channel name from YouTube
- `%(channel)s` - Channel name
- `%(id)s` - Video ID
- `%(duration)s` - Video duration

Example formats:
```json
"%(upload_date)s_%(title)s"
"%(channel)s_%(upload_date)s_%(title)s"
"%(upload_date)s_%(id)s_%(title)s"
```

## LLM Configuration

### Basic LLM Setup

Create or edit `llm_config.json`:

```json
{
  "server_url": "http://localhost:1234",
  "model_name": "llama3.1:8b",
  "context_length": 4096,
  "temperature": 0.7,
  "request_timeout": 60,
  "max_retries": 3,
  "retry_delay": 2
}
```

### LLM Configuration Fields

| Field | Description | Default |
|-------|-------------|---------|
| `server_url` | LLM server endpoint | `"http://localhost:1234"` |
| `model_name` | Model identifier | `"your-model-name"` |
| `context_length` | Maximum context tokens | `4096` |
| `temperature` | Sampling temperature (0.0-1.0) | `0.7` |
| `request_timeout` | API timeout in seconds | `60` |
| `max_retries` | Retry attempts for failed requests | `3` |
| `retry_delay` | Delay between retries | `2` |

### Compatible LLM Servers

**Local Servers:**
- **Ollama**: `http://localhost:11434`
- **LM Studio**: `http://localhost:1234`
- **text-generation-webui**: `http://localhost:5000`

**Cloud Services:**
- **OpenAI API**: `https://api.openai.com/v1`
- **Anthropic Claude**: Custom endpoint
- **Local vLLM**: `http://localhost:8000`

### Model Examples

```json
// Ollama
{
  "server_url": "http://localhost:11434",
  "model_name": "llama3.1:8b"
}

// LM Studio
{
  "server_url": "http://localhost:1234",
  "model_name": "microsoft/DialoGPT-medium"
}

// OpenAI API
{
  "server_url": "https://api.openai.com/v1",
  "model_name": "gpt-3.5-turbo"
}
```

## Web Interface Configuration

### Server Settings

Configure via command line:
```bash
# Basic startup
./start_web_app.sh

# Custom host and port
./start_web_app.sh --host 0.0.0.0 --port 9000

# Custom downloads directory
./start_web_app.sh --downloads-dir /path/to/downloads
```

### Web-Based Configuration

Access configuration through the web interface:
1. Open `http://localhost:8080`
2. Click **Settings** button
3. Configure:
   - **LLM Config**: Server URL, model, parameters
   - **Channels**: View/edit channel list, toggle summarization
   - **Add Channel**: Add new channels via web form
   - **Process URL**: Ad-hoc YouTube URL processing

## Advanced Configuration

### Bulk Configuration Updates

Use the utility script to enable summarization for channels with long content:

```bash
python3 update_summarize_setting.py
```

This automatically enables summarization for channels with content longer than 30 minutes.

### Environment Variables

Set via Docker or shell:
```bash
export PODCAST_HARVESTER_HOST=0.0.0.0
export PODCAST_HARVESTER_PORT=8080
export PYTHONUNBUFFERED=1
```

### Docker Configuration

Configure via `docker-compose.yml`:
```yaml
environment:
  - PODCAST_HARVESTER_HOST=0.0.0.0
  - PODCAST_HARVESTER_PORT=8080
volumes:
  - ./downloads:/app/downloads
  - ./channels_config.json:/app/channels_config.json:ro
```

## Configuration Validation

### Test Configuration

```bash
# Test channel configuration
python3 podcast_harvester.py --config channels_config.json --max-channels 1

# Test LLM configuration
python3 content_summarizer.py --config test_channels.json --channels "test"
```

### Common Configuration Errors

**Invalid JSON:**
```bash
# Validate JSON syntax
python3 -m json.tool channels_config.json
```

**Missing required fields:**
- Ensure `url`, `channel_name`, `content_type`, and `cutoff_date` are present

**Invalid dates:**
- Use YYYY-MM-DD format for `cutoff_date`

**LLM connection issues:**
- Verify server URL is accessible
- Check model name matches server configuration
