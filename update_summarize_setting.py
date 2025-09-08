#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess

def get_media_duration(file_path):
    """Get duration of media file in seconds using ffprobe."""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', str(file_path)
        ], capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip()) if result.stdout.strip() else 0
    except:
        return 0

def find_channels_with_long_content():
    """Find channels with media files longer than 30 minutes."""
    downloads_dir = Path('/Users/matanyahu/Downloads/podcasts/downloads')
    long_channels = set()
    
    for channel_dir in downloads_dir.iterdir():
        if not channel_dir.is_dir() or channel_dir.name.startswith('.'):
            continue
            
        for video_dir in channel_dir.iterdir():
            if not video_dir.is_dir():
                continue
                
            for media_file in video_dir.glob('*.mp3'):
                duration = get_media_duration(media_file)
                if duration > 1800:  # 30 minutes = 1800 seconds
                    long_channels.add(channel_dir.name)
                    break
            if channel_dir.name in long_channels:
                break
    
    return long_channels

def update_config():
    """Update summarize setting for channels with long content."""
    config_path = '/Users/matanyahu/Downloads/podcasts/channels_config_full.json'
    
    with open(config_path, 'r') as f:
        channels = json.load(f)
    
    long_channels = find_channels_with_long_content()
    print(f"Found {len(long_channels)} channels with content longer than 30 minutes:")
    
    updated_count = 0
    for channel in channels:
        if channel['channel_name'] in long_channels:
            if channel.get('summarize') != 'yes':
                channel['summarize'] = 'yes'
                updated_count += 1
                print(f"  ✓ {channel['channel_name']}")
    
    with open(config_path, 'w') as f:
        json.dump(channels, f, indent=2)
    
    print(f"\nUpdated {updated_count} channels to enable summarization")

if __name__ == '__main__':
    update_config()
