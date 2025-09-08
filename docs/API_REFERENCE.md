# API Reference

## Overview

The PodcastHarvester web server provides a RESTful API for managing content, configurations, and processing operations.

**Base URL**: `http://localhost:8080` (default)

## Content Management APIs

### Get All Content

Retrieve metadata for all harvested content.

```http
GET /api/content
```

**Response:**
```json
[
  {
    "path": "downloads/Channel_Name/Video_Title",
    "title": "Video Title",
    "channel": "Channel Name",
    "upload_date": "2025-01-15",
    "duration": "00:45:30",
    "content_type": "audio",
    "has_summary": true,
    "summary_chunks": 9,
    "processing_language": "en",
    "summary": "Full AI-generated summary text...",
    "media_files": ["audio.mp3"],
    "transcript_files": ["transcript.en.srt"]
  }
]
```

### Stream Media Files

Stream audio/video content with HTTP range support.

```http
GET /media/{relative_path}
```

**Parameters:**
- `relative_path`: Path relative to downloads directory

**Headers:**
- `Range`: Byte range for partial content (optional)

**Response:**
- `200 OK`: Full content
- `206 Partial Content`: Range request
- `404 Not Found`: File not found

## Configuration Management APIs

### LLM Configuration

#### Get LLM Configuration

```http
GET /api/llm-config
```

**Response:**
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

#### Save LLM Configuration

```http
POST /api/save-llm-config
Content-Type: application/json
```

**Request Body:**
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

**Response:**
```json
{
  "success": true
}
```

### Channel Configuration

#### Get Channels Configuration

```http
GET /api/channels-config
```

**Response:**
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

#### Save Channels Configuration

```http
POST /api/save-channels-config
Content-Type: application/json
```

**Request Body:**
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

**Response:**
```json
{
  "success": true
}
```

#### Add New Channel

```http
POST /api/add-channel
Content-Type: application/json
```

**Request Body:**
```json
{
  "url": "https://www.youtube.com/@newchannel",
  "channel_name": "New_Channel",
  "content_type": "audio",
  "cutoff_date": "2025-01-01",
  "output_format": "%(upload_date)s_%(channel_name)s_%(title)s",
  "output_directory": "downloads/New_Channel",
  "transcript_languages": ["en"],
  "redownload_deleted": false,
  "summarize": "yes"
}
```

**Response:**
```json
{
  "success": true
}
```

## Processing APIs

### Content Download

Execute batch content download from configured channels.

```http
POST /api/run-download
Content-Type: application/json
```

**Request Body:**
```json
{
  "config_file": "channels_config.json",
  "channels": "Channel1,Channel2",
  "max_channels": 5
}
```

**Parameters:**
- `config_file`: Configuration file to use
- `channels`: Comma-separated channel names (optional)
- `max_channels`: Maximum channels to process (optional)

**Response:**
```json
{
  "success": true,
  "message": "Download script started successfully",
  "command": "python3 podcast_harvester.py --config channels_config.json"
}
```

### Content Summarization

Execute AI summarization for existing content.

```http
POST /api/run-summarization
Content-Type: application/json
```

**Request Body:**
```json
{
  "config_file": "channels_config.json",
  "channels": "Channel1,Channel2",
  "language": "en"
}
```

**Parameters:**
- `config_file`: Configuration file to use
- `channels`: Comma-separated channel names (optional)
- `language`: Preferred transcript language (optional)

**Response:**
```json
{
  "success": true,
  "message": "Summarization script started successfully"
}
```

### Ad-hoc URL Processing

Process individual YouTube URLs with download and summarization.

```http
POST /api/process-url
Content-Type: application/json
```

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "content_type": "audio",
  "download_transcript": "yes",
  "generate_summary": "yes"
}
```

**Parameters:**
- `url`: YouTube video URL
- `content_type`: "audio" or "video"
- `download_transcript`: "yes" or "no"
- `generate_summary`: "yes" or "no"

**Response:**
```json
{
  "success": true,
  "message": "URL processing started"
}
```

## Content Deletion APIs

### Delete Media Files

Remove audio/video files while preserving metadata.

```http
POST /api/delete-media
Content-Type: application/json
```

**Request Body:**
```json
{
  "path": "downloads/Channel_Name/Video_Title"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Deleted media files from: downloads/Channel_Name/Video_Title"
}
```

### Delete Entire Folder

Remove complete content folder including all files.

```http
POST /api/delete-folder
Content-Type: application/json
```

**Request Body:**
```json
{
  "path": "downloads/Channel_Name/Video_Title"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Deleted folder: downloads/Channel_Name/Video_Title"
}
```

## Error Responses

All APIs return consistent error responses:

```json
{
  "error": "Error description",
  "status": 400
}
```

**Common HTTP Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

No rate limiting is currently implemented. For production use, consider implementing rate limiting based on your requirements.

## Authentication

The current implementation does not include authentication. For production deployment:

1. Add authentication middleware
2. Implement API key validation
3. Use HTTPS for secure communication
4. Consider OAuth2 for user management

## WebSocket Support

WebSocket support is not currently implemented but could be added for:
- Real-time progress updates
- Live log streaming
- Instant configuration updates

## API Client Examples

### Python Client

```python
import requests

# Get all content
response = requests.get('http://localhost:8080/api/content')
content = response.json()

# Start download
payload = {
    "config_file": "channels_config.json",
    "max_channels": 3
}
response = requests.post('http://localhost:8080/api/run-download', json=payload)
```

### JavaScript Client

```javascript
// Get all content
const response = await fetch('/api/content');
const content = await response.json();

// Process URL
const payload = {
    url: 'https://www.youtube.com/watch?v=VIDEO_ID',
    content_type: 'audio',
    generate_summary: 'yes'
};
const response = await fetch('/api/process-url', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
});
```

### cURL Examples

```bash
# Get content
curl http://localhost:8080/api/content

# Start download
curl -X POST http://localhost:8080/api/run-download \
  -H "Content-Type: application/json" \
  -d '{"config_file": "channels_config.json"}'

# Process URL
curl -X POST http://localhost:8080/api/process-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID", "content_type": "audio"}'
```
