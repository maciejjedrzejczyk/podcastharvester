# Architecture Overview

This document provides a comprehensive overview of PodcastHarvester's architecture, components, and workflows.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │  Content Server │    │ Content Scanner │
│ (content_viewer │◄──►│ (content_server │◄──►│   (embedded)    │
│     .html)      │    │     .py)        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Batch Processor │    │ Download Engine │    │ File System     │
│ (podcast_       │◄──►│   (yt-dlp)      │◄──►│ (downloads/)    │
│  harvester.py)  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ AI Summarizer   │    │ RSS Generator   │    │ Control Files   │
│ (content_       │    │ (rss_generator  │    │ (.json files)   │
│  summarizer.py) │    │     .py)        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Main Orchestrator (`podcast_harvester.py`)
**Purpose**: Primary entry point for batch content processing

**Key Responsibilities**:
- Channel configuration validation
- Index creation and management
- Download coordination
- Progress tracking and error handling
- Integration with summarization and RSS generation

**Workflow**:
1. Load and validate channel configurations
2. Create or update channel indexes
3. Determine content to download (skip existing)
4. Execute downloads via yt-dlp
5. Update control files
6. Trigger post-processing (summarization, RSS)

### 2. Web Management Interface
**Components**:
- `content_server.py` - HTTP server and API endpoints
- `content_viewer.html` - Modern web interface
- `ContentScanner` class - File system analysis

**Capabilities**:
- Real-time content browsing and management
- Ad-hoc URL processing
- Configuration management
- Progress monitoring
- Media file serving and playback

### 3. Indexing System
**Purpose**: Optimize downloads and reduce API calls

**Components**:
- Channel indexing (`create_channel_index()`)
- Unified index files (`.channel_index.json`)
- Index merging and repair utilities

**Benefits**:
- Pre-filters content by date range
- Caches video metadata
- Enables intelligent skip logic
- Reduces YouTube API usage

### 4. Download Control System
**Purpose**: Track downloaded content and prevent duplicates

**Components**:
- Control file generation (`create_download_control_v2.py`)
- Download tracking (`.download_control.json`)
- Deleted file detection and handling

**Features**:
- Maintains complete download history
- Supports redownload of deleted files
- File integrity checking via hashes
- Statistics and metadata tracking

### 5. AI Summarization Engine (`content_summarizer.py`)
**Purpose**: Generate intelligent content summaries

**Workflow**:
1. **Transcript Processing**: Parse SRT subtitle files
2. **Chunking**: Split transcripts into 5-minute segments
3. **Chunk Summarization**: Generate individual chunk summaries via LLM
4. **Final Summarization**: Create comprehensive video summary
5. **Metadata Generation**: Store processing information

**Directory Structure**:
```
video_folder/
├── chunks/           # 5-minute transcript segments
├── chunk_summaries/  # Individual chunk summaries
└── content_summary/  # Final video summary + metadata
```

### 6. RSS Feed System (`rss_generator.py`)
**Purpose**: Generate RSS feeds for external integration

**Features**:
- Channel-specific feeds
- Master feed (all channels)
- Automatic updates after downloads
- Integration with podcast managers

## Data Flow

### 1. Batch Processing Flow
```
Configuration → Index Creation → Content Filtering → Download → Post-Processing
      ↓              ↓               ↓                ↓            ↓
channels_config → .channel_index → skip existing → yt-dlp → summarization
      ↓              ↓               ↓                ↓            ↓
validation     → API calls      → control files → media files → RSS feeds
```

### 2. Web Interface Flow
```
User Request → Content Scanner → File System → Response Generation
     ↓              ↓               ↓              ↓
URL/Action → analyze folders → read metadata → JSON/HTML/Media
     ↓              ↓               ↓              ↓
validation → extract info    → file serving  → client update
```

### 3. Summarization Flow
```
Video Folder → Transcript → Chunking → LLM Processing → Final Summary
     ↓            ↓           ↓            ↓              ↓
.srt files → parse text → 5min chunks → individual → combined
     ↓            ↓           ↓            ↓              ↓
validation → timestamps → chunk files → summaries → metadata
```

## File System Organization

### Directory Structure
```
PodcastHarvester/
├── podcast_harvester.py      # Main orchestrator
├── content_server.py          # Web server
├── content_viewer.html        # Web interface
├── content_summarizer.py      # AI summarization
├── rss_generator.py          # RSS generation
├── create_download_control_v2.py  # Control file management
├── channels_config.json       # Channel configurations
├── llm_config.json           # LLM server configuration
├── notification_config.json  # Notification settings
├── downloads/                # Downloaded content
│   ├── Channel_Name/
│   │   ├── Video_Folder/
│   │   │   ├── media files
│   │   │   ├── chunks/
│   │   │   ├── chunk_summaries/
│   │   │   └── content_summary/
│   │   ├── .channel_index.json
│   │   └── .download_control.json
│   └── feeds/               # Generated RSS feeds
└── docs/                   # Documentation
```

### Control Files
- **`.channel_index.json`**: Video metadata cache
- **`.download_control.json`**: Download tracking and history
- **`channels_config.json`**: Channel processing configuration
- **`llm_config.json`**: AI summarization settings
- **`notification_config.json`**: Webhook notification setup

## Integration Points

### External Dependencies
- **yt-dlp**: YouTube content downloading
- **Python HTTP server**: Web interface serving
- **LLM servers**: AI summarization (Ollama, LM Studio, OpenAI-compatible)
- **Docker**: Containerized deployment

### API Endpoints (Web Interface)
- `GET /api/content` - List all downloaded content
- `POST /api/process-url` - Process individual YouTube URL
- `DELETE /api/content/{path}` - Delete content
- `GET /api/config` - Get/set configurations
- `GET /media/{path}` - Serve media files
- `GET /feeds/{channel}.xml` - RSS feeds

### Notification Integration
- **Webhook support**: HTTP POST notifications
- **Configurable payloads**: Custom message templates
- **Per-channel settings**: Selective notifications

### RSS Integration
- **Standard RSS 2.0 format**: Compatible with feed readers
- **Podcast extensions**: iTunes-compatible metadata
- **Automatic updates**: Generated after successful downloads

## Scalability Considerations

### Performance Optimizations
- **Indexing system**: Reduces API calls and processing time
- **Skip logic**: Avoids redundant downloads
- **Chunked processing**: Handles large channels efficiently
- **Parallel processing**: Docker-based concurrent operations

### Resource Management
- **Memory efficient**: Streaming processing for large files
- **Storage optimization**: Thumbnail cleanup, configurable quality
- **API rate limiting**: Respects YouTube's usage limits
- **Error handling**: Graceful degradation and recovery

### Deployment Options
- **Standalone**: Direct Python execution
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-service orchestration
- **Web-only**: Interface without batch processing

## Security Considerations

### Data Protection
- **Local processing**: No external data transmission (except LLM)
- **Configurable LLM**: Support for local AI servers
- **File permissions**: Proper access controls
- **Input validation**: Sanitized user inputs

### Network Security
- **HTTPS support**: Secure web interface access
- **Webhook validation**: Secure notification endpoints
- **CORS handling**: Controlled cross-origin requests
- **Rate limiting**: Protection against abuse

## Extensibility

### Plugin Architecture
- **Modular design**: Independent components
- **Configuration-driven**: Behavior modification via JSON
- **Script integration**: Easy addition of new utilities
- **API extensibility**: RESTful interface for custom tools

### Customization Points
- **Output formats**: Configurable file naming and organization
- **Processing workflows**: Customizable post-processing steps
- **LLM prompts**: Adjustable summarization behavior
- **Notification templates**: Custom message formats
