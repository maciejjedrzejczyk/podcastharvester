# Configuration Guide

## Channel Configuration

### Basic Channel Setup

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

### Configuration Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `url` | ✅ | YouTube channel URL | `"https://www.youtube.com/@mkbhd"` |
| `channel_name` | ✅ | Clean name for directories | `"MKBHD"` |
| `content_type` | ✅ | Download format | `"audio"` or `"video"` |
| `cutoff_date` | ✅ | Only download content after this date | `"2025-01-01"` |
| `output_format` | ❌ | Filename template | `"%(upload_date)s_%(title)s"` |
| `output_directory` | ❌ | Target directory | `"downloads/MKBHD"` |
| `transcript_languages` | ❌ | Subtitle languages | `["en", "es", "fr"]` |
| `redownload_deleted` | ❌ | Re-download deleted files | `true` or `false` |
| `summarize` | ❌ | Enable AI summarization | `"yes"` or `"no"` |

### Content Types

**Audio (`"audio"`):**
- Downloads best quality audio (MP3 format)
- Smaller file sizes
- Ideal for podcasts and interviews

**Video (`"video"`):**
- Downloads best quality video
- Larger file sizes
- Preserves visual content

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
