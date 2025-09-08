# Web Interface Guide

## Overview

The PodcastHarvester web interface provides a modern, responsive UI for managing harvested content, configuring the system, and processing individual YouTube URLs.

## Getting Started

### Starting the Web Interface

```bash
# Basic startup
./start_web_app.sh

# Custom configuration
./start_web_app.sh --host 0.0.0.0 --port 9000 --downloads-dir /path/to/downloads
```

Access the interface at `http://localhost:8080` (or your configured port).

## Main Interface

### Content Grid

The main interface displays all harvested content in an organized grid:

- **Search Bar**: Real-time search across titles, channels, and summaries
- **Filter Buttons**: 
  - **All**: Show all content
  - **Summarized**: Only content with AI summaries
  - **Audio**: Audio-only content
  - **Video**: Video content

### Content Cards

Each content item is displayed in an expandable card showing:

**Header (Always Visible):**
- Video/audio title
- Channel name
- Upload date and duration
- Content type indicator
- Summary status and chunk count
- Processing language

**Expanded View:**
- Full AI-generated summary
- Built-in media player with controls
- Delete options (media only or entire folder)

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
