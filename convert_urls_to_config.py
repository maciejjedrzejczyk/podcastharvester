#!/usr/bin/env python3
"""
Convert YouTube channel URLs list to configuration JSON format
"""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

def extract_channel_name(url):
    """Extract a clean channel name from YouTube URL."""
    # Remove trailing slashes and /videos
    url = url.rstrip('/').replace('/videos', '')
    
    # Extract the channel identifier
    if '/@' in url:
        # Handle @username format
        channel_id = url.split('/@')[-1]
    elif '/c/' in url:
        # Handle /c/channelname format
        channel_id = url.split('/c/')[-1]
    elif '/channel/' in url:
        # Handle /channel/ID format
        channel_id = url.split('/channel/')[-1]
    else:
        # Fallback - use the last part of the URL
        channel_id = url.split('/')[-1]
    
    # Clean up the channel name
    # Remove URL encoding
    channel_id = channel_id.replace('%C5%9A', 'S').replace('%C4%99', 'e')
    
    # Replace special characters with underscores
    channel_name = re.sub(r'[^\w\-_.]', '_', channel_id)
    
    # Remove multiple underscores
    channel_name = re.sub(r'_+', '_', channel_name)
    
    # Remove leading/trailing underscores
    channel_name = channel_name.strip('_')
    
    # Capitalize first letter of each word
    channel_name = '_'.join(word.capitalize() for word in channel_name.split('_'))
    
    return channel_name

def convert_urls_to_config(input_file, output_file, default_cutoff="2025-08-01"):
    """Convert URL list to JSON configuration format."""
    
    channels_config = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        # Normalize URL format
        if url.startswith('Https://'):
            url = url.replace('Https://', 'https://')
        elif not url.startswith('http'):
            url = 'https://' + url
        
        channel_name = extract_channel_name(url)
        
        config = {
            "url": url,
            "channel_name": channel_name,
            "content_type": "audio",
            "cutoff_date": default_cutoff,
            "output_format": "%(upload_date)s_%(channel_name)s_%(title)s",
            "output_directory": f"downloads/{channel_name}",
            "download_metadata": True,
            "download_transcript": True,
            "transcript_languages": ["en", "pl"],
            "redownload_deleted": False
        }
        
        channels_config.append(config)
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(channels_config, f, indent=2, ensure_ascii=False)
    
    print(f"Converted {len(channels_config)} channels to {output_file}")
    
    # Show first few entries as preview
    print("\nFirst 5 entries preview:")
    for i, config in enumerate(channels_config[:5]):
        print(f"{i+1}. {config['channel_name']} -> {config['url']}")

def main():
    input_file = "./youtube_channel_urls.txt"
    output_file = "./channels_config.json"
    
    convert_urls_to_config(input_file, output_file)

if __name__ == "__main__":
    main()
