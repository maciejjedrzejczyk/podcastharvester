# Advanced Features

This guide covers the advanced features and capabilities of PodcastHarvester that go beyond basic content downloading.

## Smart Indexing System

### Channel Index Files
PodcastHarvester uses a sophisticated indexing system to optimize downloads and API usage:

- **`.channel_index.json`** - Unified index containing all video metadata for a channel
- **Pre-indexing** - Scans channels before downloading to determine what content is available
- **Cutoff date filtering** - Only indexes content after specified dates
- **API optimization** - Reduces YouTube API calls by caching video information

### Index Structure
```json
{
  "channel_name": "Channel Name",
  "channel_url": "https://www.youtube.com/@channel",
  "created_date": "2025-01-01T12:00:00",
  "last_updated": "2025-01-01T12:00:00",
  "current_cutoff_date": "2024-01-01",
  "cutoff_dates": ["2024-01-01", "2024-06-01"],
  "total_videos": 150,
  "videos": {
    "video_id": {
      "id": "video_id",
      "title": "Video Title",
      "upload_date": "20250101",
      "duration": 1800,
      "webpage_url": "https://www.youtube.com/watch?v=video_id"
    }
  },
  "video_ids": ["video_id1", "video_id2"],
  "date_range": {
    "earliest": "20240101",
    "latest": "20250101"
  }
}
```

### Index Management
```bash
# Force reindex all channels
python3 podcast_harvester.py --config channels_config.json --force-reindex

# Merge old date-specific indexes into unified format
python3 merge_channel_indexes.py

# Repair corrupted indexes
python3 repair_unified_indexes.py
```

## Smart Skip Logic

### Download Control Files
The system maintains **`.download_control.json`** files to track downloaded content:

```json
{
  "channel_name": "Channel Name",
  "downloaded_videos": {
    "video_id": {
      "title": "Video Title",
      "download_date": "2025-01-01T12:00:00",
      "files": {
        "audio": "subfolder/video.mp3",
        "video": "subfolder/video.mp4",
        "info_json": "subfolder/video.info.json",
        "description": "subfolder/video.description",
        "thumbnails": ["subfolder/video.jpg"],
        "subtitles": ["subfolder/video.en.srt"]
      },
      "deleted": false,
      "file_hashes": {
        "audio": "hash123"
      }
    }
  },
  "statistics": {
    "total_videos": 50,
    "total_size_mb": 2048
  }
}
```

### Redownload Deleted Files
Configure how the system handles previously downloaded but now deleted files:

```json
{
  "redownload_deleted": false  // Skip all videos in control file
  "redownload_deleted": true   // Only skip videos that exist on disk
}
```

**When `false`**: Maintains complete download history, never re-downloads
**When `true`**: Re-downloads files that were previously downloaded but are now missing from disk

## Notification System

### Setup Notifications
Create `notification_config.json`:

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

### Enable Per-Channel Notifications
In your channel configuration:

```json
{
  "channel_name": "Example Channel",
  "send_notification": "yes"
}
```

### Usage
```bash
python3 podcast_harvester.py --config channels_config.json --send-config notification_config.json
```

## RSS Feed Generation

### Automatic RSS Feeds
Enable RSS feed generation in channel configuration:

```json
{
  "channel_name": "Example Channel",
  "generate_rss": true
}
```

### RSS Feed Structure
The system generates:
- **Channel-specific feeds**: `feeds/channel_name.xml`
- **Master feed**: `feeds/master.xml` (all channels combined)

### Integration with External Tools

**FreshRSS Integration:**
```bash
# Add feed URL to FreshRSS
http://your-server:8080/feeds/channel_name.xml
```

**Audiobookshelf Integration:**
```bash
# Use RSS feed as podcast source
http://your-server:8080/feeds/channel_name.xml
```

### Manual RSS Generation
```bash
python3 rss_generator.py --downloads-dir downloads --output-dir feeds
```

## Content Organization

### Subfolder Structure
Each video is organized in its own subfolder:

```
downloads/
├── Channel_Name/
│   ├── 20250101_Channel_Name_Video_Title/
│   │   ├── 20250101_Channel_Name_Video_Title.mp3
│   │   ├── 20250101_Channel_Name_Video_Title.info.json
│   │   ├── 20250101_Channel_Name_Video_Title.description
│   │   ├── 20250101_Channel_Name_Video_Title.jpg
│   │   ├── 20250101_Channel_Name_Video_Title.en.srt
│   │   ├── chunks/
│   │   │   ├── chunk_001.txt
│   │   │   └── chunk_002.txt
│   │   ├── chunk_summaries/
│   │   │   ├── chunk_001_summary.txt
│   │   │   └── chunk_002_summary.txt
│   │   └── content_summary/
│   │       ├── summary.txt
│   │       └── metadata.json
│   └── .channel_index.json
│   └── .download_control.json
```

### Thumbnail Optimization
The system automatically:
- Downloads all available thumbnail resolutions
- Keeps only the highest resolution thumbnail
- Removes lower quality duplicates

## Channel Selection and Filtering

### Process Specific Channels
```bash
# Process only selected channels
python3 podcast_harvester.py --config channels_config.json --channels "Channel1,Channel2,Channel3"

# Combine with other options
python3 podcast_harvester.py --config channels_config.json --channels "Channel1" --force-reindex
```

### Limit Processing
```bash
# Process only first N channels
python3 podcast_harvester.py --config channels_config.json --max-channels 3
```

## Batch Operations

### Update All Cutoff Dates
```bash
# Update all channels to use today's date as cutoff
python3 update_cutoff_dates.py --config channels_config.json
```

### Control File Management
```bash
# Regenerate all control files
python3 create_download_control_v2.py --downloads-dir downloads --config channels_config.json

# Find videos that were re-downloaded
python3 find_redownloaded_videos.py --downloads-dir downloads
```

### Bulk Configuration Updates
```bash
# Enable summarization for all channels
python3 update_summarize_setting.py --config channels_config.json --enable

# Convert URL list to full configuration
python3 convert_urls_to_config.py --input urls.txt --output channels_config.json
```

## Performance Optimization

### API Rate Limiting
- The indexing system reduces YouTube API calls
- Built-in delays between channel processing
- Respects YouTube's rate limits automatically

### Storage Optimization
- Thumbnail cleanup removes duplicate resolutions
- Configurable content types (audio vs video)
- Optional metadata and transcript downloads

### Processing Efficiency
- Skip existing downloads by default
- Parallel processing support via Docker
- Incremental indexing for large channels

## Integration Capabilities

### Web Interface Integration
- All advanced features accessible via web UI
- Real-time progress tracking
- Configuration management interface

### Docker Integration
- Separate containers for different operations
- Volume mounting for persistent data
- Environment variable configuration

### External Tool Integration
- RSS feeds for podcast managers
- Webhook notifications for automation
- API endpoints for custom integrations
