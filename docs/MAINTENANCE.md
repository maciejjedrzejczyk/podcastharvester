# Maintenance Guide

This guide covers operational procedures, troubleshooting, and maintenance tasks for PodcastHarvester.

## Regular Maintenance Tasks

### 1. Index Management

**Check Index Health:**
```bash
# List all channel indexes
find downloads -name ".channel_index.json" -exec echo "=== {} ===" \; -exec jq '.channel_name, .total_videos, .last_updated' {} \;

# Verify index integrity
python3 repair_unified_indexes.py --downloads-dir downloads --dry-run
```

**Update Indexes:**
```bash
# Force reindex all channels
python3 podcast_harvester.py --config channels_config.json --force-reindex

# Reindex specific channels
python3 podcast_harvester.py --config channels_config.json --channels "Channel1,Channel2" --force-reindex
```

**Merge Legacy Indexes:**
```bash
# Convert old date-specific indexes to unified format
python3 merge_channel_indexes.py --downloads-dir downloads
```

### 2. Control File Maintenance

**Regenerate Control Files:**
```bash
# Update all control files based on current filesystem
python3 create_download_control_v2.py --downloads-dir downloads --config channels_config.json

# Verify control file accuracy
python3 find_redownloaded_videos.py --downloads-dir downloads
```

**Clean Up Control Files:**
```bash
# Remove placeholder entries
python3 remove_placeholder_ids.py --downloads-dir downloads

# Migrate deleted records format
python3 migrate_deleted_records.py --downloads-dir downloads
```

### 3. Storage Management

**Disk Space Monitoring:**
```bash
# Check total storage usage
du -sh downloads/

# Check per-channel usage
du -sh downloads/*/

# Find largest files
find downloads -type f -exec du -h {} + | sort -rh | head -20
```

**Cleanup Operations:**
```bash
# Remove duplicate thumbnails (keep highest resolution)
python3 podcast_harvester.py --config channels_config.json --cleanup-thumbnails

# Remove temporary files
find downloads -name "*.tmp" -delete
find downloads -name "*.part" -delete
```

### 4. Configuration Management

**Validate Configurations:**
```bash
# Check channel configuration syntax
python3 -c "import json; json.load(open('channels_config.json'))"

# Validate LLM configuration
python3 -c "import json; json.load(open('llm_config.json'))"

# Test LLM connectivity
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"test","messages":[{"role":"user","content":"test"}]}'
```

**Backup Configurations:**
```bash
# Create configuration backup
cp channels_config.json "channels_config.backup.$(date +%Y%m%d).json"
cp llm_config.json "llm_config.backup.$(date +%Y%m%d).json"
```

## Troubleshooting Common Issues

### Download Issues

**Problem: "yt-dlp not found"**
```bash
# Check yt-dlp installation
which yt-dlp
yt-dlp --version

# Install/update yt-dlp
pip install --upgrade yt-dlp
```

**Problem: "Private video" or "Video unavailable"**
- Check if channel/video is still public
- Verify channel URL format
- Update channel URLs if changed
- Check for geographic restrictions

**Problem: Rate limiting**
```bash
# Add delays between downloads
python3 podcast_harvester.py --config channels_config.json --delay 5

# Process fewer channels at once
python3 podcast_harvester.py --config channels_config.json --max-channels 3
```

### Indexing Issues

**Problem: Corrupted index files**
```bash
# Repair corrupted indexes
python3 repair_unified_indexes.py --downloads-dir downloads

# Force recreation of specific channel index
rm downloads/Channel_Name/.channel_index.json
python3 podcast_harvester.py --config channels_config.json --channels "Channel_Name" --force-reindex
```

**Problem: Missing videos in index**
```bash
# Check cutoff date settings
jq '.current_cutoff_date' downloads/Channel_Name/.channel_index.json

# Update cutoff date and reindex
python3 update_cutoff_dates.py --config channels_config.json --date "2024-01-01"
```

### Summarization Issues

**Problem: LLM server connection failed**
```bash
# Check LLM server status
curl http://localhost:1234/v1/models

# Restart LLM server
# For Ollama:
ollama serve

# For LM Studio: Restart application
```

**Problem: Out of memory during summarization**
```bash
# Reduce context length in llm_config.json
{
  "context_length": 2048,  # Reduced from 4096
  "temperature": 0.7
}

# Process fewer videos simultaneously
python3 content_summarizer.py --config channels_config.json --max-concurrent 1
```

**Problem: Missing transcripts**
```bash
# Check transcript download settings
jq '.download_transcript, .transcript_languages' channels_config.json

# Manually download transcripts
yt-dlp --write-subs --write-auto-subs --sub-langs "en" "VIDEO_URL"
```

### Web Interface Issues

**Problem: Web interface not accessible**
```bash
# Check if server is running
ps aux | grep content_server.py

# Check port availability
netstat -tlnp | grep :8080

# Start with different port
python3 content_server.py --port 8081
```

**Problem: Content not showing in web interface**
```bash
# Check downloads directory permissions
ls -la downloads/

# Verify content scanner
python3 -c "
from content_server import ContentScanner
from pathlib import Path
scanner = ContentScanner(Path('downloads'))
content = scanner.scan_downloads_directory()
print(f'Found {len(content)} items')
"
```

### RSS Feed Issues

**Problem: RSS feeds not generating**
```bash
# Check RSS configuration
jq '.generate_rss' channels_config.json

# Manually generate RSS feeds
python3 rss_generator.py --downloads-dir downloads --output-dir feeds

# Verify feed validity
xmllint --noout feeds/channel_name.xml
```

## Performance Monitoring

### System Resource Usage

**Monitor CPU and Memory:**
```bash
# During processing
top -p $(pgrep -f podcast_harvester.py)

# Memory usage by component
ps aux | grep -E "(podcast_harvester|content_server|content_summarizer)" | awk '{print $2, $4, $11}'
```

**Monitor Disk I/O:**
```bash
# Watch disk usage during downloads
watch -n 1 'df -h | grep downloads'

# Monitor I/O activity
iotop -p $(pgrep -f podcast_harvester.py)
```

### Processing Statistics

**Download Statistics:**
```bash
# Count total videos per channel
find downloads -name ".download_control.json" -exec jq -r '.channel_name + ": " + (.statistics.total_videos | tostring)' {} \;

# Calculate total storage usage
find downloads -name ".download_control.json" -exec jq -r '.statistics.total_size_mb // 0' {} \; | awk '{sum+=$1} END {print "Total: " sum " MB"}'
```

**Summarization Statistics:**
```bash
# Count summarized videos
find downloads -name "metadata.json" -path "*/content_summary/*" | wc -l

# Average processing time
find downloads -name "metadata.json" -path "*/content_summary/*" -exec jq '.processing_time_seconds // 0' {} \; | awk '{sum+=$1; count++} END {print "Average: " sum/count " seconds"}'
```

## Backup and Recovery

### Data Backup

**Essential Files to Backup:**
```bash
# Configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  channels_config.json \
  llm_config.json \
  notification_config.json

# Control and index files
find downloads -name ".channel_index.json" -o -name ".download_control.json" | \
  tar -czf control_files_backup_$(date +%Y%m%d).tar.gz -T -

# Complete downloads directory (large)
tar -czf downloads_backup_$(date +%Y%m%d).tar.gz downloads/
```

**Incremental Backup:**
```bash
# Backup only new content (last 7 days)
find downloads -type f -mtime -7 | tar -czf incremental_backup_$(date +%Y%m%d).tar.gz -T -
```

### Recovery Procedures

**Restore Configuration:**
```bash
# Restore from backup
tar -xzf config_backup_YYYYMMDD.tar.gz

# Validate restored configuration
python3 -c "import json; json.load(open('channels_config.json'))"
```

**Rebuild Control Files:**
```bash
# If control files are lost/corrupted
rm downloads/*/.download_control.json
python3 create_download_control_v2.py --downloads-dir downloads --config channels_config.json
```

**Rebuild Indexes:**
```bash
# If index files are lost/corrupted
rm downloads/*/.channel_index.json
python3 podcast_harvester.py --config channels_config.json --force-reindex
```

## Automation and Scheduling

### Cron Job Setup

**Daily Content Harvesting:**
```bash
# Add to crontab (crontab -e)
0 2 * * * cd /path/to/PodcastHarvester && python3 podcast_harvester.py --config channels_config.json >> logs/harvest.log 2>&1
```

**Weekly Maintenance:**
```bash
# Weekly index cleanup
0 3 * * 0 cd /path/to/PodcastHarvester && python3 repair_unified_indexes.py --downloads-dir downloads >> logs/maintenance.log 2>&1

# Weekly backup
0 4 * * 0 cd /path/to/PodcastHarvester && tar -czf backups/backup_$(date +\%Y\%m\%d).tar.gz channels_config.json llm_config.json downloads/
```

### Log Management

**Setup Logging:**
```bash
# Create log directory
mkdir -p logs

# Rotate logs
logrotate -f logrotate.conf
```

**Log Analysis:**
```bash
# Check for errors
grep -i error logs/harvest.log

# Monitor download success rate
grep -c "✅ Download completed" logs/harvest.log
grep -c "❌ Error during download" logs/harvest.log
```

## Health Checks

### System Health Script

Create `health_check.py`:
```python
#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required tools are available."""
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        print("✅ yt-dlp available")
    except:
        print("❌ yt-dlp not found")

def check_configurations():
    """Validate configuration files."""
    configs = ['channels_config.json', 'llm_config.json']
    for config in configs:
        try:
            with open(config) as f:
                json.load(f)
            print(f"✅ {config} valid")
        except:
            print(f"❌ {config} invalid or missing")

def check_downloads_directory():
    """Check downloads directory structure."""
    downloads_dir = Path('downloads')
    if downloads_dir.exists():
        channels = len([d for d in downloads_dir.iterdir() if d.is_dir()])
        print(f"✅ Downloads directory: {channels} channels")
    else:
        print("❌ Downloads directory missing")

if __name__ == "__main__":
    check_dependencies()
    check_configurations()
    check_downloads_directory()
```

### Monitoring Dashboard

**Simple Status Check:**
```bash
#!/bin/bash
echo "=== PodcastHarvester Health Check ==="
echo "Date: $(date)"
echo ""

echo "System Resources:"
df -h | grep -E "(downloads|Filesystem)"
echo ""

echo "Recent Activity:"
find downloads -name "*.mp3" -o -name "*.mp4" -mtime -1 | wc -l | xargs echo "Files downloaded today:"
echo ""

echo "Process Status:"
pgrep -f "content_server.py" > /dev/null && echo "✅ Web server running" || echo "❌ Web server stopped"
pgrep -f "podcast_harvester.py" > /dev/null && echo "✅ Harvester running" || echo "⏸️ Harvester idle"
```
