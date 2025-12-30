#!/usr/bin/env python3
"""
RSS Feed Generator for PodcastHarvester

Generates RSS feeds for downloaded content to notify external programs
like FreshRSS or Audiobookshelf about new content availability.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET


class RSSGenerator:
    def __init__(self, downloads_dir: Path, base_url: str = "http://localhost:8080"):
        self.downloads_dir = downloads_dir
        self.base_url = base_url.rstrip('/')
        
    def generate_channel_feed(self, channel_name: str, max_items: int = 50) -> str:
        """Generate RSS feed for a specific channel."""
        channel_dir = self.downloads_dir / channel_name
        if not channel_dir.exists():
            return self._empty_feed(channel_name)
        
        # Get video items
        items = self._get_channel_items(channel_dir, max_items)
        
        # Create RSS structure
        rss = Element('rss', version='2.0')
        rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        
        channel = SubElement(rss, 'channel')
        SubElement(channel, 'title').text = f"PodcastHarvester - {channel_name}"
        SubElement(channel, 'description').text = f"Downloaded content from {channel_name}"
        SubElement(channel, 'link').text = f"{self.base_url}/channel/{channel_name}"
        SubElement(channel, 'lastBuildDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
        SubElement(channel, 'generator').text = "PodcastHarvester RSS Generator"
        
        # Add items
        for item_data in items:
            self._add_item_to_channel(channel, item_data)
        
        return self._format_xml(rss)
    
    def generate_master_feed(self, max_items: int = 100) -> str:
        """Generate master RSS feed with content from all channels."""
        all_items = []
        
        # Collect items from all channels
        for channel_dir in self.downloads_dir.iterdir():
            if channel_dir.is_dir() and not channel_dir.name.startswith('.'):
                items = self._get_channel_items(channel_dir, max_items)
                all_items.extend(items)
        
        # Sort by date (newest first)
        all_items.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
        all_items = all_items[:max_items]
        
        # Create RSS structure
        rss = Element('rss', version='2.0')
        channel = SubElement(rss, 'channel')
        SubElement(channel, 'title').text = "PodcastHarvester - All Channels"
        SubElement(channel, 'description').text = "All downloaded content from PodcastHarvester"
        SubElement(channel, 'link').text = f"{self.base_url}/feeds/master"
        SubElement(channel, 'lastBuildDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Add items
        for item_data in all_items:
            self._add_item_to_channel(channel, item_data)
        
        return self._format_xml(rss)
    
    def _get_channel_items(self, channel_dir: Path, max_items: int) -> List[Dict]:
        """Extract items from a channel directory."""
        items = []
        
        for video_dir in channel_dir.iterdir():
            if not video_dir.is_dir() or video_dir.name.startswith('.'):
                continue
            
            item = self._extract_video_info(video_dir, channel_dir.name)
            if item:
                items.append(item)
        
        # Sort by upload date (newest first)
        items.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
        return items[:max_items]
    
    def _extract_video_info(self, video_dir: Path, channel_name: str) -> Optional[Dict]:
        """Extract video information from directory."""
        # Look for info.json file
        info_files = list(video_dir.glob('*.info.json'))
        if not info_files:
            return None
        
        try:
            with open(info_files[0], 'r', encoding='utf-8') as f:
                info = json.load(f)
        except:
            return None
        
        # Find media files
        audio_file = self._find_media_file(video_dir, ['.mp3', '.m4a', '.aac'])
        video_file = self._find_media_file(video_dir, ['.mp4', '.webm', '.mkv'])
        
        if not audio_file and not video_file:
            return None
        
        # Get file stats for pub date
        media_file = audio_file or video_file
        file_path = video_dir / media_file
        pub_date = datetime.fromtimestamp(file_path.stat().st_mtime, timezone.utc)
        
        return {
            'title': info.get('title', video_dir.name),
            'description': info.get('description', '')[:500] + '...' if info.get('description') else '',
            'upload_date': info.get('upload_date', ''),
            'pub_date': pub_date.strftime('%a, %d %b %Y %H:%M:%S %z'),
            'duration': info.get('duration', 0),
            'channel_name': channel_name,
            'video_path': f"{channel_name}/{video_dir.name}",
            'media_file': media_file,
            'media_url': f"{self.base_url}/media/{channel_name}/{video_dir.name}/{media_file}",
            'webpage_url': info.get('webpage_url', ''),
            'file_size': file_path.stat().st_size if file_path.exists() else 0
        }
    
    def _find_media_file(self, video_dir: Path, extensions: List[str]) -> Optional[str]:
        """Find media file with given extensions."""
        for ext in extensions:
            files = list(video_dir.glob(f'*{ext}'))
            if files:
                return files[0].name
        return None
    
    def _add_item_to_channel(self, channel: Element, item_data: Dict):
        """Add RSS item to channel."""
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = item_data['title']
        SubElement(item, 'description').text = item_data['description']
        SubElement(item, 'pubDate').text = item_data['pub_date']
        SubElement(item, 'guid').text = item_data['media_url']
        SubElement(item, 'link').text = item_data.get('webpage_url', item_data['media_url'])
        
        # Add enclosure for media file
        enclosure = SubElement(item, 'enclosure')
        enclosure.set('url', item_data['media_url'])
        enclosure.set('length', str(item_data['file_size']))
        enclosure.set('type', self._get_mime_type(item_data['media_file']))
        
        # Add iTunes tags for podcast compatibility
        if item_data['duration']:
            SubElement(item, 'itunes:duration').text = self._format_duration(item_data['duration'])
        SubElement(item, 'itunes:author').text = item_data['channel_name']
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type for file."""
        ext = Path(filename).suffix.lower()
        mime_types = {
            '.mp3': 'audio/mpeg',
            '.m4a': 'audio/mp4',
            '.aac': 'audio/aac',
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.mkv': 'video/x-matroska'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration for iTunes."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _empty_feed(self, channel_name: str) -> str:
        """Generate empty RSS feed."""
        rss = Element('rss', version='2.0')
        channel = SubElement(rss, 'channel')
        SubElement(channel, 'title').text = f"PodcastHarvester - {channel_name}"
        SubElement(channel, 'description').text = f"No content available for {channel_name}"
        SubElement(channel, 'link').text = f"{self.base_url}/channel/{channel_name}"
        return self._format_xml(rss)
    
    def _format_xml(self, element: Element) -> str:
        """Format XML with proper declaration."""
        xml_str = tostring(element, encoding='unicode')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'


def update_rss_feeds(downloads_dir: Path, feeds_dir: Path, base_url: str = "http://localhost:8080"):
    """Update all RSS feeds."""
    feeds_dir.mkdir(exist_ok=True)
    generator = RSSGenerator(downloads_dir, base_url)
    
    # Generate master feed
    master_feed = generator.generate_master_feed()
    (feeds_dir / 'master.xml').write_text(master_feed, encoding='utf-8')
    
    # Generate individual channel feeds
    for channel_dir in downloads_dir.iterdir():
        if channel_dir.is_dir() and not channel_dir.name.startswith('.'):
            channel_feed = generator.generate_channel_feed(channel_dir.name)
            (feeds_dir / f'{channel_dir.name}.xml').write_text(channel_feed, encoding='utf-8')
    
    print(f"✅ RSS feeds updated in {feeds_dir}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate RSS feeds for PodcastHarvester")
    parser.add_argument('--downloads-dir', default='downloads', help='Downloads directory')
    parser.add_argument('--feeds-dir', default='feeds', help='RSS feeds output directory')
    parser.add_argument('--base-url', default='http://localhost:8080', help='Base URL for media links')
    
    args = parser.parse_args()
    
    downloads_path = Path(args.downloads_dir)
    feeds_path = Path(args.feeds_dir)
    
    if not downloads_path.exists():
        print(f"Error: Downloads directory {downloads_path} does not exist")
        exit(1)
    
    update_rss_feeds(downloads_path, feeds_path, args.base_url)
