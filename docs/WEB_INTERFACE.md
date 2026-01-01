# Web Interface Guide

This guide covers using the PodcastHarvester web management interface for content browsing, ad-hoc processing, and system management.

## Quick Start

### Starting the Web Interface

```bash
# Simple startup
./start_web_app.sh
# Open http://localhost:8080

# Custom configuration
python3 content_server.py --host 0.0.0.0 --port 9000 --downloads-dir /path/to/downloads
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Server host address | `localhost` |
| `--port` | Server port | `8080` |
| `--downloads-dir` | Downloads directory path | `downloads` |

## Core Features

### 1. Content Library

**Browse Downloaded Content:**
- Grid view of all downloaded videos/audio
- Filter by channel using dropdown
- Real-time search by title
- Sort by date, channel, or title

**Content Information:**
- Thumbnail previews
- Video title and channel name
- Upload date and duration
- Available formats (audio/video)
- AI summary status

### 2. Media Playback

**Built-in Players:**
- HTML5 audio player for MP3/M4A files
- HTML5 video player for MP4/WebM files
- Full-screen video support
- Playback controls and progress tracking

### 3. Content Management

**Delete Operations:**
- **Delete Media Only**: Removes audio/video, keeps metadata
- **Delete Entire Folder**: Removes all files and folders
- Confirmation dialogs prevent accidents
- Immediate UI updates

**Download Options:**
- Direct download links for media files
- Original filenames preserved
- Batch download support

### 4. AI Summary Viewing

**Summary Display:**
- Full AI-generated content summaries
- Chunk-by-chunk breakdown view
- Processing metadata and timestamps
- Copy-to-clipboard functionality

**Summary Status Indicators:**
- ⏳ **In Progress**: Currently processing
- ✅ **Completed**: Summary available
- ❌ **Failed**: Processing errors
- ➖ **Not Processed**: No summary

## Ad-hoc URL Processing

### Process Individual URLs

**Step-by-Step:**
1. Navigate to **Settings → Process URL**
2. Enter YouTube video or channel URL
3. Configure processing options:
   - Content type (audio/video)
   - Download transcripts (required for summaries)
   - Enable AI summarization
   - Transcript languages
4. Click **"Process URL"**
5. Monitor real-time progress

**Processing Configuration:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "content_type": "audio",
  "download_transcript": true,
  "summarize": true,
  "transcript_languages": ["en"]
}
```

### Real-time Progress Monitoring

**Progress Indicators:**
- Download progress bars
- Summarization status updates
- Error notifications with details
- Completion notifications

**Status Updates:**
- Current operation details
- Progress percentage
- Estimated time remaining
- Error messages and recovery suggestions

## Configuration Management

### LLM Configuration

**Settings Panel:**
- Server URL and model configuration
- System prompts for summarization
- Request timeout and retry settings
- **Test Connectivity** button for validation

**Example Configuration:**
```json
{
  "server_url": "http://localhost:1234",
  "model_name": "llama-3.1-8b-instruct",
  "context_length": 4096,
  "temperature": 0.7
}
```

### Channel Configuration

**Management Features:**
- Add/edit/remove channels
- Batch configuration updates
- Import/export configurations
- Real-time validation and error checking

## Advanced Features

### Batch Operations

**Bulk Actions:**
- Select multiple content items
- Batch delete operations
- Mass summarization requests
- Bulk metadata updates

**Channel Operations:**
- Process entire channels from web interface
- Update channel configurations
- Regenerate RSS feeds
- Monitor channel processing status

### Search and Filtering

**Advanced Search:**
- Real-time search as you type
- Search video titles and descriptions
- Case-insensitive matching
- Filter by processing status

**Content Filtering:**
- Filter by channel
- Filter by content type (audio/video)
- Filter by summary status
- Date range filtering

## API Integration

### REST API Endpoints

**Content Management:**
- `GET /api/content` - List all downloaded content
- `POST /api/process-url` - Process individual YouTube URL
- `DELETE /api/content/{path}` - Delete content (media or folder)

**Configuration:**
- `GET /api/config` - Get system configurations
- `POST /api/config` - Update configurations

**Media Serving:**
- `GET /media/{path}` - Serve media files directly
- `GET /feeds/{channel}.xml` - RSS feeds

### WebSocket Events

**Real-time Updates:**
- `progress_update` - Processing progress notifications
- `content_added` - New content available
- `content_deleted` - Content removed
- `error_occurred` - Error notifications with details

## Interface Customization

### Themes and Layout

**Built-in Options:**
- Light theme (default)
- Dark theme support
- Responsive design for mobile/tablet
- Grid and list view modes

**Layout Options:**
- Adjustable grid size
- Sortable content display
- Collapsible sidebar
- Full-screen media playback

## Troubleshooting

### Common Issues

**Web Interface Not Loading:**
```bash
# Check server status
ps aux | grep content_server.py

# Test port availability
netstat -tlnp | grep :8080

# Start with different port
python3 content_server.py --port 8081
```

**Content Not Displaying:**
```bash
# Verify downloads directory
ls -la downloads/

# Check permissions
chmod -R 755 downloads/

# Test content scanner
python3 -c "
from content_server import ContentScanner
from pathlib import Path
scanner = ContentScanner(Path('downloads'))
print(f'Found {len(scanner.scan_downloads_directory())} items')
"
```

**Media Playback Issues:**
- Verify file formats are browser-compatible
- Check file permissions and accessibility
- Test with different browsers
- Ensure media files aren't corrupted

**Summary Display Problems:**
- Verify `content_summary/` folders exist
- Check LLM server connectivity
- Review processing logs for errors
- Ensure proper file permissions

### Performance Optimization

**Large Content Libraries:**
- Use channel filtering to reduce load
- Enable browser caching
- Optimize thumbnail loading
- Consider pagination for very large libraries

**Network Optimization:**
- Use local network access when possible
- Enable compression for large media files
- Implement proper caching headers
- Monitor bandwidth usage

## Security Considerations

### Access Control

**Network Security:**
- Default binding to `localhost` for security
- Use reverse proxy (nginx/Apache) for external access
- Implement HTTPS for secure connections
- Configure firewall rules appropriately

**File System Security:**
- Proper permissions on downloads directory
- Path sanitization to prevent directory traversal
- Input validation for all user inputs
- Regular security updates

### Data Protection

**Privacy Features:**
- All processing happens locally by default
- No external data transmission (except to configured LLM)
- User data stored locally only
- Configurable data retention

**Backup Recommendations:**
- Regular configuration backups
- Content metadata preservation
- Document recovery procedures
- Test restore processes regularly

### Media Player Controls

- **▶️ Play/Pause**: Standard playback control
- **⏪ Skip Backward**: Jump back 10 seconds
- **⏩ Skip Forward**: Jump forward 10 seconds
- **🎚️ Speed Control**: Adjust playback speed (0.5x to 2x)
- **🗑️ Delete Options**: Remove content with confirmation

## Settings Panel

Click the **Settings** button (top-right) to access configuration options.

### LLM Configuration Tab

Configure your AI summarization server:

- **Server URL**: LLM server endpoint (e.g., `http://localhost:1234`)
- **Model Name**: Model identifier (e.g., `llama3.1:8b`)
- **Context Length**: Maximum context tokens (default: 4096)
- **Temperature**: Sampling temperature (0.0-1.0, default: 0.7)

Click **Save LLM Config** to apply changes.

### Channels Tab

Manage your channel configuration:

- **View all configured channels**
- **Toggle summarization** on/off for individual channels
- **See channel details** (URL, content type, etc.)

Click **Save Changes** to apply modifications.

### Add Channel Tab

Add new channels via web form:

- **Channel URL**: YouTube channel URL
- **Channel Name**: Clean name for directories
- **Content Type**: Audio or Video
- **Cutoff Date**: Only download content after this date
- **Enable Summarization**: Yes/No

Click **Add Channel** to add to configuration.

### Process URL Tab

Process individual YouTube URLs:

- **YouTube URL**: Any YouTube video URL
- **Content Type**: Audio or Video download
- **Download Transcript**: Include subtitles
- **Generate Summary**: Create AI summary

Click **Process URL** to start processing.

## Batch Operations

### Content Download

Access via Settings or direct interface:

1. **Config File**: Choose configuration file
2. **Specific Channels**: Comma-separated channel names (optional)
3. **Max Channels**: Limit number of channels to process (optional)

Click **Start Download** to begin batch processing.

### Content Summarization

Generate AI summaries for existing content:

1. **Config File**: Choose configuration file
2. **Specific Channels**: Target specific channels (optional)
3. **Language**: Preferred transcript language

Click **Start Summarization** to begin AI processing.

## Progress Tracking

### Progress Indicator

When running downloads or summarization:

- **Progress Bar**: Visual progress from 0-100%
- **Status Text**: Current operation stage
- **Log Entries**: Timestamped progress updates
- **Manual Control**: Close button to dismiss early

### Progress Stages

**Download Process:**
1. Starting download script...
2. Fetching channel metadata...
3. Downloading video content...
4. Processing transcripts...
5. Organizing files...
6. Download completed!

**Summarization Process:**
1. Starting summarization script...
2. Loading transcripts...
3. Chunking content...
4. Generating summaries...
5. Processing with AI...
6. Summarization completed!

## Content Management

### Viewing Content

- **Expand cards** to view full summaries
- **Use media player** for audio/video playback
- **Search and filter** to find specific content
- **Maximize summaries** for full-screen reading

### Deleting Content

Two deletion options:

**Media Only:**
- Removes audio/video files
- Preserves metadata, summaries, transcripts
- Useful for freeing storage space

**Entire Folder:**
- Removes complete content folder
- Deletes all associated files
- Permanent removal

### Downloading Summaries

- **Individual summaries**: Download button on each card
- **Maximized view**: Download from full-screen summary view
- **Text format**: Summaries saved as `.txt` files

## Mobile Support

The interface is fully responsive and supports:

- **Touch navigation**
- **Mobile-optimized layouts**
- **Gesture controls** for media playback
- **Responsive design** for tablets and phones

## Keyboard Shortcuts

- **Space**: Play/pause media
- **Left Arrow**: Skip backward 10 seconds
- **Right Arrow**: Skip forward 10 seconds
- **Escape**: Close modals/expanded views
- **Enter**: Confirm actions

## Browser Compatibility

Tested and supported browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Common Issues

**Settings button not visible:**
- Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
- Clear browser cache
- Try incognito/private window

**Progress indicator disappears:**
- Progress shows for realistic timeframes
- Click X to close manually
- Page auto-refreshes after completion

**Media playback issues:**
- Ensure browser supports HTML5 audio/video
- Check file formats are compatible
- Verify media files exist on disk

**Configuration not saving:**
- Check browser console for errors
- Verify server is running
- Ensure write permissions on config files

### Performance Tips

- **Use filters** to reduce displayed content
- **Close expanded cards** when not needed
- **Clear browser cache** periodically
- **Use specific channel selection** for large configurations
