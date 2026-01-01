# Migration Guide

This guide covers upgrading PodcastHarvester installations, migrating data between versions, and handling breaking changes.

## Version Migration

### Pre-Migration Checklist

**1. Backup Current Installation:**
```bash
# Backup configuration files
cp channels_config.json channels_config.backup.json
cp llm_config.json llm_config.backup.json
cp notification_config.json notification_config.backup.json

# Backup control and index files
find downloads -name ".channel_index.json" -o -name ".download_control.json" | \
  tar -czf control_files_backup.tar.gz -T -

# Backup entire downloads directory (optional, large)
tar -czf downloads_backup.tar.gz downloads/
```

**2. Document Current Setup:**
```bash
# Record current version/commit
git log --oneline -1 > migration_info.txt

# Record Python environment
pip freeze > requirements_old.txt

# Record system information
python3 --version >> migration_info.txt
yt-dlp --version >> migration_info.txt
```

### Migration Procedures

#### From Legacy Index System (Pre-v2.0)

**Problem**: Old versions used date-specific index files (`.channel_index_YYYY-MM-DD.json`)
**Solution**: Migrate to unified index system

```bash
# 1. Backup old indexes
find downloads -name ".channel_index_*.json" | tar -czf old_indexes_backup.tar.gz -T -

# 2. Run migration script
python3 merge_channel_indexes.py --downloads-dir downloads

# 3. Verify migration
find downloads -name ".channel_index.json" -exec echo "=== {} ===" \; -exec jq '.channel_name, .total_videos, .cutoff_dates' {} \;

# 4. Clean up old files (after verification)
find downloads -name ".channel_index_*.json" -delete
```

#### From Basic Control System (Pre-v1.5)

**Problem**: Missing or incomplete download control files
**Solution**: Regenerate control files from filesystem

```bash
# 1. Remove old control files
find downloads -name ".download_control.json" -delete

# 2. Regenerate from current filesystem
python3 create_download_control_v2.py --downloads-dir downloads --config channels_config.json

# 3. Verify control files
find downloads -name ".download_control.json" -exec jq '.channel_name, .statistics.total_videos' {} \;
```

#### Configuration Format Changes

**Channel Configuration Updates:**

*Old Format (v1.x):*
```json
{
  "url": "https://www.youtube.com/@channel",
  "name": "Channel Name",
  "type": "audio",
  "date": "2024-01-01"
}
```

*New Format (v2.x):*
```json
{
  "url": "https://www.youtube.com/@channel",
  "channel_name": "Channel_Name",
  "content_type": "audio",
  "cutoff_date": "2024-01-01",
  "output_format": "%(upload_date)s_%(channel_name)s_%(title)s",
  "output_directory": "downloads/Channel_Name",
  "download_metadata": true,
  "download_transcript": true,
  "transcript_languages": ["en"],
  "redownload_deleted": false,
  "summarize": "yes",
  "generate_rss": true
}
```

**Migration Script:**
```python
#!/usr/bin/env python3
import json

def migrate_channel_config(old_config_path, new_config_path):
    with open(old_config_path, 'r') as f:
        old_config = json.load(f)
    
    new_config = []
    for channel in old_config:
        new_channel = {
            "url": channel["url"],
            "channel_name": channel["name"].replace(" ", "_"),
            "content_type": channel["type"],
            "cutoff_date": channel["date"],
            "output_format": "%(upload_date)s_%(channel_name)s_%(title)s",
            "output_directory": f"downloads/{channel['name'].replace(' ', '_')}",
            "download_metadata": True,
            "download_transcript": True,
            "transcript_languages": ["en"],
            "redownload_deleted": False,
            "summarize": "no",
            "generate_rss": False
        }
        new_config.append(new_channel)
    
    with open(new_config_path, 'w') as f:
        json.dump(new_config, f, indent=2)

# Usage
migrate_channel_config('channels_config.old.json', 'channels_config.json')
```

## Data Migration

### Directory Structure Changes

**Old Structure (v1.x):**
```
downloads/
├── Channel_Name/
│   ├── video1.mp3
│   ├── video1.info.json
│   ├── video2.mp3
│   └── video2.info.json
```

**New Structure (v2.x):**
```
downloads/
├── Channel_Name/
│   ├── 20250101_Channel_Name_Video1/
│   │   ├── 20250101_Channel_Name_Video1.mp3
│   │   ├── 20250101_Channel_Name_Video1.info.json
│   │   └── content_summary/
│   └── 20250102_Channel_Name_Video2/
│       ├── 20250102_Channel_Name_Video2.mp3
│       └── 20250102_Channel_Name_Video2.info.json
```

**Migration Script:**
```bash
#!/bin/bash
# migrate_directory_structure.sh

for channel_dir in downloads/*/; do
    channel_name=$(basename "$channel_dir")
    echo "Migrating $channel_name..."
    
    # Find all media files in root of channel directory
    find "$channel_dir" -maxdepth 1 -name "*.mp3" -o -name "*.mp4" | while read media_file; do
        base_name=$(basename "$media_file" | sed 's/\.[^.]*$//')
        
        # Create subfolder
        subfolder="$channel_dir/$base_name"
        mkdir -p "$subfolder"
        
        # Move related files
        mv "$media_file" "$subfolder/"
        mv "$channel_dir/$base_name.info.json" "$subfolder/" 2>/dev/null || true
        mv "$channel_dir/$base_name.description" "$subfolder/" 2>/dev/null || true
        mv "$channel_dir/$base_name"*.srt "$subfolder/" 2>/dev/null || true
        mv "$channel_dir/$base_name"*.jpg "$subfolder/" 2>/dev/null || true
        
        echo "  Moved $base_name to subfolder"
    done
done
```

### Database Migration (Future Versions)

If future versions introduce database storage:

```bash
# Export current JSON data
python3 export_to_database.py --downloads-dir downloads --output database_export.sql

# Import to new database system
python3 import_from_json.py --input database_export.sql
```

## Breaking Changes by Version

### Version 2.0 Changes

**Breaking Changes:**
1. **Index System**: Date-specific indexes → Unified indexes
2. **Directory Structure**: Flat files → Subfolder organization
3. **Configuration Format**: Simplified → Extended configuration
4. **Control Files**: Basic tracking → Comprehensive metadata

**Migration Required:**
- Run `merge_channel_indexes.py`
- Regenerate control files
- Update configuration format
- Optionally migrate directory structure

### Version 1.5 Changes

**Breaking Changes:**
1. **Control Files**: Introduction of `.download_control.json`
2. **Skip Logic**: Basic → Advanced skip functionality
3. **Metadata Tracking**: File-based → JSON-based

**Migration Required:**
- Run `create_download_control_v2.py`
- Update processing scripts

## Environment Migration

### Python Environment Updates

**Update Dependencies:**
```bash
# Backup current environment
pip freeze > requirements_old.txt

# Update yt-dlp (critical)
pip install --upgrade yt-dlp

# Update other dependencies
pip install --upgrade -r requirements.txt

# Compare versions
diff requirements_old.txt <(pip freeze)
```

**Virtual Environment Migration:**
```bash
# Create new environment
python3 -m venv venv_new

# Activate new environment
source venv_new/bin/activate

# Install requirements
pip install -r requirements.txt

# Test functionality
python3 podcast_harvester.py --help

# Switch environments
mv venv venv_old
mv venv_new venv
```

### Docker Migration

**Update Docker Images:**
```bash
# Backup current setup
docker-compose down
cp docker-compose.yml docker-compose.yml.backup

# Pull new images
docker-compose pull

# Update configuration
# Edit docker-compose.yml with new version

# Start with new images
docker-compose up --build
```

**Volume Migration:**
```bash
# Backup volumes
docker run --rm -v podcastharvester_downloads:/data -v $(pwd):/backup alpine tar czf /backup/downloads_backup.tar.gz -C /data .

# Restore to new volume
docker run --rm -v podcastharvester_downloads_new:/data -v $(pwd):/backup alpine tar xzf /backup/downloads_backup.tar.gz -C /data
```

## Post-Migration Verification

### Functionality Tests

**1. Basic Functionality:**
```bash
# Test configuration loading
python3 podcast_harvester.py --config channels_config.json --help

# Test web interface
python3 content_server.py --port 8081 &
curl http://localhost:8081/api/content
kill %1
```

**2. Index System:**
```bash
# Verify indexes exist and are valid
find downloads -name ".channel_index.json" -exec jq '.channel_name, .total_videos' {} \;

# Test index creation
python3 podcast_harvester.py --config test_channels.json --force-reindex --max-channels 1
```

**3. Control Files:**
```bash
# Verify control files
find downloads -name ".download_control.json" -exec jq '.channel_name, .statistics.total_videos' {} \;

# Test skip logic
python3 podcast_harvester.py --config test_channels.json --max-channels 1
```

**4. Summarization (if enabled):**
```bash
# Test LLM connectivity
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"test","messages":[{"role":"user","content":"test"}]}'

# Test summarization
python3 content_summarizer.py --config test_channels.json --channels "TestChannel"
```

### Data Integrity Checks

**1. File Counts:**
```bash
# Compare file counts before/after migration
echo "Before migration:" && cat migration_file_count.txt
echo "After migration:" && find downloads -type f | wc -l
```

**2. Content Verification:**
```bash
# Verify media files are playable
find downloads -name "*.mp3" -exec ffprobe -v quiet -show_entries format=duration {} \; | head -5

# Check for corrupted files
find downloads -name "*.mp3" -exec ffprobe -v error {} \; 2>&1 | grep -i error
```

**3. Metadata Consistency:**
```bash
# Check info.json files
find downloads -name "*.info.json" -exec jq '.id, .title' {} \; | head -10

# Verify control file accuracy
python3 find_redownloaded_videos.py --downloads-dir downloads
```

## Rollback Procedures

### Emergency Rollback

**1. Stop All Processes:**
```bash
pkill -f podcast_harvester.py
pkill -f content_server.py
pkill -f content_summarizer.py
```

**2. Restore Backups:**
```bash
# Restore configurations
cp channels_config.backup.json channels_config.json
cp llm_config.backup.json llm_config.json

# Restore control files
tar -xzf control_files_backup.tar.gz

# Restore downloads (if needed)
rm -rf downloads
tar -xzf downloads_backup.tar.gz
```

**3. Revert Code:**
```bash
# Return to previous version
git checkout previous_version_tag

# Restore Python environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_old.txt
```

### Partial Rollback

**Rollback Specific Components:**
```bash
# Rollback only index system
rm downloads/*/.channel_index.json
# Restore old indexes from backup
tar -xzf old_indexes_backup.tar.gz

# Rollback only control files
rm downloads/*/.download_control.json
# Use old control file generation method
```

## Migration Troubleshooting

### Common Issues

**1. Permission Errors:**
```bash
# Fix file permissions
find downloads -type f -exec chmod 644 {} \;
find downloads -type d -exec chmod 755 {} \;
```

**2. JSON Parsing Errors:**
```bash
# Find and fix invalid JSON files
find downloads -name "*.json" -exec python3 -m json.tool {} \; > /dev/null
```

**3. Missing Dependencies:**
```bash
# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt
```

**4. Configuration Conflicts:**
```bash
# Validate configuration against schema
python3 validate_config.py --config channels_config.json
```

### Recovery Strategies

**1. Incremental Migration:**
- Migrate one channel at a time
- Test each step before proceeding
- Keep backups of each stage

**2. Parallel Testing:**
- Run old and new versions side by side
- Compare outputs before switching
- Gradual transition of channels

**3. Staged Rollout:**
- Test with subset of channels
- Monitor for issues
- Full deployment after validation
