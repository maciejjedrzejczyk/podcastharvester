#!/usr/bin/env python3
"""
PodcastHarvester - Advanced YouTube Channel Content Harvesting System

This script harvests content from YouTube channels with the following features:
- Pre-indexing of channel content within date range
- Skip already downloaded content using control files
- Batch processing from configuration file
- Optimized API usage through indexing
- Progress tracking and error handling
- AI-powered content summarization
- Smart subfolder organization
"""

import argparse
import json
import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set


def check_dependencies():
    """Check if yt-dlp is installed."""
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: yt-dlp is not installed or not found in PATH.")
        print("Please install it using: pip install yt-dlp")
        return False


def load_control_file(channel_dir: Path) -> Dict:
    """Load the download control file for a channel."""
    control_file = channel_dir / '.download_control.json'
    
    if not control_file.exists():
        return {
            'channel_name': channel_dir.name,
            'downloaded_videos': {},
            'statistics': {'total_videos': 0}
        }
    
    try:
        with open(control_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load control file for {channel_dir.name}: {e}")
        return {
            'channel_name': channel_dir.name,
            'downloaded_videos': {},
            'statistics': {'total_videos': 0}
        }


def load_index_file(channel_dir: Path, cutoff_date: str) -> Optional[Dict]:
    """Load the unified channel index file if it exists."""
    index_file = channel_dir / '.channel_index.json'
    
    if not index_file.exists():
        # Check for old date-specific index files and suggest migration
        old_indexes = list(channel_dir.glob('.channel_index_*.json'))
        if old_indexes:
            print(f"  📋 Found {len(old_indexes)} old index files. Run merge_channel_indexes.py to migrate.")
        return None
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # Initialize missing fields for backward compatibility
        if 'cutoff_dates' not in index_data:
            index_data['cutoff_dates'] = []
        if 'index_history' not in index_data:
            index_data['index_history'] = []
        if 'current_cutoff_date' not in index_data:
            index_data['current_cutoff_date'] = cutoff_date
        if 'last_updated' not in index_data:
            index_data['last_updated'] = index_data.get('created_date', datetime.now().isoformat())
        
        print(f"  📋 Using existing unified channel index")
        return index_data
            
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"  ⚠️  Error reading index file: {e}")
        return None


def save_index_file(channel_dir: Path, cutoff_date: str, index_data: Dict):
    """Save the unified channel index file."""
    index_file = channel_dir / '.channel_index.json'
    
    # Update the index with current cutoff date and timestamp
    if 'cutoff_dates' not in index_data:
        index_data['cutoff_dates'] = []
    
    if cutoff_date not in index_data['cutoff_dates']:
        index_data['cutoff_dates'].append(cutoff_date)
        index_data['cutoff_dates'] = sorted(index_data['cutoff_dates'])
    
    index_data['last_updated'] = datetime.now().isoformat()
    index_data['current_cutoff_date'] = cutoff_date
    
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        print(f"  💾 Saved unified channel index")
    except Exception as e:
        print(f"  ⚠️  Error saving index file: {e}")


def update_unified_index(existing_index: Dict, new_videos: List[Dict], cutoff_date: str) -> Dict:
    """Update an existing unified index with new videos and cutoff date."""
    
    # Merge new videos with existing ones
    existing_videos = existing_index.get('videos', {})
    
    for video in new_videos:
        video_id = video['id']
        if video_id not in existing_videos:
            existing_videos[video_id] = video
        else:
            # Keep the video with more complete data
            if len(str(video)) > len(str(existing_videos[video_id])):
                existing_videos[video_id] = video
    
    # Update index structure
    updated_index = existing_index.copy()
    updated_index['videos'] = existing_videos
    updated_index['video_ids'] = list(existing_videos.keys())
    updated_index['total_videos'] = len(existing_videos)
    updated_index['last_updated'] = datetime.now().isoformat()
    updated_index['current_cutoff_date'] = cutoff_date
    
    # Update cutoff dates list
    if 'cutoff_dates' not in updated_index:
        updated_index['cutoff_dates'] = []
    if cutoff_date not in updated_index['cutoff_dates']:
        updated_index['cutoff_dates'].append(cutoff_date)
        updated_index['cutoff_dates'] = sorted(updated_index['cutoff_dates'])
    
    # Add to history
    if 'index_history' not in updated_index:
        updated_index['index_history'] = []
    
    updated_index['index_history'].append({
        'cutoff_date': cutoff_date,
        'created_date': datetime.now().isoformat(),
        'total_videos': len(new_videos),
        'source_file': 'updated_existing'
    })
    
    # Recalculate date range
    video_dates = []
    for video in existing_videos.values():
        upload_date = video.get('upload_date')
        if upload_date:
            video_dates.append(upload_date)
    
    if video_dates:
        updated_index['date_range'] = {
            'earliest': min(video_dates),
            'latest': max(video_dates)
        }
    
    return updated_index


def create_channel_index(channel_url: str, channel_name: str, cutoff_date: str, 
                        channel_dir: Path) -> Dict:
    """Create an index of videos in the channel within the date range using a two-step process."""
    
    print(f"  🔍 Creating index for {channel_name}...")
    
    # Parse cutoff date
    try:
        cutoff_dt = datetime.strptime(cutoff_date, "%Y-%m-%d")
        cutoff_str = cutoff_dt.strftime("%Y%m%d")
    except ValueError:
        print(f"Error: Invalid date format '{cutoff_date}'")
        return {}
    
    # Step 1: Get video list with basic info (fast, reliable)
    print(f"     Step 1: Getting video list...")
    cmd_list = [
        'yt-dlp',
        '--flat-playlist',       # Get basic playlist info
        '--dump-json',           # Output JSON
        '--no-download',         # Don't download
        '--ignore-errors',       # Continue on errors
        '--no-warnings',         # Suppress warnings
        '--playlist-end', '50',  # Limit to recent videos
        channel_url
    ]
    
    try:
        # Get basic video list
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        
        video_ids = []
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        video_data = json.loads(line)
                        video_id = video_data.get('id')
                        if video_id:
                            video_ids.append(video_id)
                    except json.JSONDecodeError:
                        continue
        
        if not video_ids:
            print(f"     No videos found in channel")
            return {
                'channel_name': channel_name,
                'channel_url': channel_url,
                'cutoff_date': cutoff_date,
                'created_date': datetime.now().isoformat(),
                'total_videos': 0,
                'videos': {},
                'video_ids': [],
                'date_range': {'earliest': None, 'latest': None}
            }
        
        print(f"     Found {len(video_ids)} recent videos")
        
        # Step 2: Get detailed metadata for each video with date filtering
        print(f"     Step 2: Getting detailed metadata with date filtering...")
        videos = []
        
        for i, video_id in enumerate(video_ids[:20]):  # Limit to 20 most recent for detailed check
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd_detail = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--ignore-errors',
                '--no-warnings',
                '--dateafter', cutoff_str,
                video_url
            ]
            
            try:
                detail_result = subprocess.run(cmd_detail, capture_output=True, text=True, timeout=10)
                
                if detail_result.stdout.strip():
                    try:
                        video_data = json.loads(detail_result.stdout.strip())
                        
                        # Extract relevant information
                        video_info = {
                            'id': video_data.get('id', ''),
                            'title': video_data.get('title', ''),
                            'upload_date': video_data.get('upload_date', ''),
                            'duration': video_data.get('duration', 0),
                            'webpage_url': video_data.get('webpage_url', ''),
                            'uploader': video_data.get('uploader', ''),
                            'view_count': video_data.get('view_count', 0),
                            'description': video_data.get('description', '')[:200] + '...' if video_data.get('description') else ''
                        }
                        
                        # Only include if it has an upload date and meets cutoff
                        if video_info['upload_date'] and video_info['upload_date'] >= cutoff_str:
                            videos.append(video_info)
                            
                    except json.JSONDecodeError:
                        continue
                        
            except subprocess.TimeoutExpired:
                print(f"     Timeout checking video {i+1}/{len(video_ids[:20])}")
                continue
            except Exception:
                continue
        
        # Create unified index data structure
        index_data = {
            'channel_name': channel_name,
            'channel_url': channel_url,
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'current_cutoff_date': cutoff_date,
            'cutoff_dates': [cutoff_date],
            'total_videos': len(videos),
            'videos': {video['id']: video for video in videos},
            'video_ids': [video['id'] for video in videos],
            'date_range': {
                'earliest': None,
                'latest': None
            },
            'index_history': [{
                'cutoff_date': cutoff_date,
                'created_date': datetime.now().isoformat(),
                'total_videos': len(videos),
                'source_file': 'created_new'
            }]
        }
        
        # Calculate date range only if we have videos with dates
        video_dates = [v['upload_date'] for v in videos if v['upload_date']]
        if video_dates:
            index_data['date_range'] = {
                'earliest': min(video_dates),
                'latest': max(video_dates)
            }
        
        print(f"  ✅ Indexed {len(videos)} videos for {channel_name}")
        if index_data['date_range']['earliest']:
            print(f"     Date range: {index_data['date_range']['earliest']} to {index_data['date_range']['latest']}")
        elif len(videos) == 0:
            print(f"     No videos found in date range (after {cutoff_date})")
        else:
            print(f"     Videos found but no upload dates available")
        
        # Save index file
        save_index_file(channel_dir, cutoff_date, index_data)
        
        return index_data
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        print(f"  ❌ Error creating index for {channel_name}: {error_msg}")
        
        # Check for common error patterns
        if "Private video" in str(error_msg) or "This video is unavailable" in str(error_msg):
            print(f"     Channel may be private or have restricted access")
        elif "does not exist" in str(error_msg) or "not found" in str(error_msg):
            print(f"     Channel URL may be incorrect or channel may not exist")
        elif "rate limit" in str(error_msg).lower() or "too many requests" in str(error_msg).lower():
            print(f"     Rate limited by YouTube - try again later")
        
        return {}
    except Exception as e:
        print(f"  ❌ Unexpected error creating index for {channel_name}: {e}")
        return {}


def get_downloaded_video_ids(channel_dir: Path) -> Set[str]:
    """Get set of already downloaded video IDs from control file."""
    control_data = load_control_file(channel_dir)
    return set(control_data.get('downloaded_videos', {}).keys())


def get_existing_video_ids(channel_dir: Path, redownload_deleted: bool = False) -> Set[str]:
    """Get set of video IDs that should be skipped based on redownload_deleted setting."""
    control_data = load_control_file(channel_dir)
    downloaded_videos = control_data.get('downloaded_videos', {})
    
    if not downloaded_videos:
        return set()
    
    # Always check if files actually exist on disk
    existing_ids = set()
    for video_id, video_info in downloaded_videos.items():
        files = video_info.get('files', {})
        
        # Check if main content file (audio/video) exists
        main_file = files.get('audio') or files.get('video')
        if main_file:
            # The main_file path already includes the subfolder structure
            file_path = channel_dir / main_file
            
            if file_path.exists():
                existing_ids.add(video_id)
            elif not redownload_deleted:
                # File doesn't exist but redownload_deleted is false
                # Still skip it to honor the "don't redownload deleted" setting
                existing_ids.add(video_id)
                print(f"     🚫 Skipping deleted video (redownload_deleted: false): {video_info.get('title', video_id)[:50]}...")
            else:
                # File doesn't exist and redownload_deleted is true
                print(f"     📁 Will re-download deleted: {video_info.get('title', video_id)[:50]}...")
    
    return existing_ids


def get_actually_existing_video_ids(channel_dir: Path) -> Set[str]:
    """Get set of video IDs that actually exist on disk (regardless of redownload_deleted setting)."""
    control_data = load_control_file(channel_dir)
    downloaded_videos = control_data.get('downloaded_videos', {})
    
    if not downloaded_videos:
        return set()
    
    existing_ids = set()
    for video_id, video_info in downloaded_videos.items():
        files = video_info.get('files', {})
        
        # Check if main content file (audio/video) exists
        main_file = files.get('audio') or files.get('video')
        if main_file:
            # The main_file path already includes the subfolder structure
            file_path = channel_dir / main_file
            
            if file_path.exists():
                existing_ids.add(video_id)
    
    return existing_ids


def load_channels_config(config_file: str) -> List[Dict]:
    """Load channels configuration from JSON file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if not isinstance(config, list):
            raise ValueError("Configuration file must contain a list of channel configurations")
        
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        return []
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return []


def validate_channel_config(config: Dict) -> bool:
    """Validate a single channel configuration."""
    required_fields = ['url', 'channel_name', 'content_type', 'cutoff_date']
    
    for field in required_fields:
        if field not in config:
            print(f"Error: Missing required field '{field}' in channel configuration")
            return False
    
    # Validate content type
    if config['content_type'] not in ['audio', 'video']:
        print(f"Error: Invalid content_type '{config['content_type']}'. Must be 'audio' or 'video'")
        return False
    
    # Validate date format
    try:
        datetime.strptime(config['cutoff_date'], "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format '{config['cutoff_date']}'. Use YYYY-MM-DD")
        return False
    
    # Validate optional boolean fields
    for field in ['download_metadata', 'download_transcript', 'redownload_deleted']:
        if field in config and not isinstance(config[field], bool):
            print(f"Error: '{field}' must be true or false")
            return False
    
    # Validate summarize field
    if 'summarize' in config:
        if config['summarize'] not in ['yes', 'no']:
            print(f"Error: 'summarize' must be 'yes' or 'no'")
            return False
    
    # Validate transcript languages if specified
    if 'transcript_languages' in config:
        if not isinstance(config['transcript_languages'], list):
            print(f"Error: 'transcript_languages' must be a list of language codes")
            return False
        for lang in config['transcript_languages']:
            if not isinstance(lang, str) or len(lang) < 2:
                print(f"Error: Invalid language code '{lang}' in transcript_languages")
                return False
    
    return True


def download_channel_with_index(config: Dict, download_format: Optional[str] = None, 
                               skip_existing: bool = True, force_reindex: bool = False) -> bool:
    """Download channel content using pre-created index with skip functionality."""
    
    # Extract configuration
    channel_url = config['url']
    channel_name = config['channel_name']
    content_type = config['content_type']
    cutoff_date_str = config['cutoff_date']
    dest_dir = config.get('output_directory', f"downloads/{channel_name}")
    output_format = config.get('output_format', '%(upload_date)s_%(channel_name)s_%(title)s')
    
    # Parse cutoff date
    try:
        cutoff_date = datetime.strptime(cutoff_date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format '{cutoff_date_str}' for channel {channel_name}")
        return False
    
    # Create destination directory if it doesn't exist
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📺 Processing channel: {channel_name}")
    print(f"   URL: {channel_url}")
    print(f"   Cutoff date: {cutoff_date_str}")
    print(f"   Destination: {dest_dir}")
    
    # Step 1: Load or create channel index
    index_data = None
    if not force_reindex:
        index_data = load_index_file(dest_path, cutoff_date_str)
    
    if not index_data:
        print(f"  📋 Creating channel index...")
        index_data = create_channel_index(channel_url, channel_name, cutoff_date_str, dest_path)
        if not index_data:
            print(f"  ❌ Failed to create index for {channel_name}")
            return False
        elif not index_data.get('videos'):
            print(f"  ℹ️  No videos found in date range for {channel_name} (after {cutoff_date_str})")
            return True  # Not an error, just no content to download
    else:
        # Check if we need to update the index for a new cutoff date
        current_cutoff = index_data.get('current_cutoff_date')
        cutoff_dates = index_data.get('cutoff_dates', [])
        
        if cutoff_date_str not in cutoff_dates or current_cutoff != cutoff_date_str:
            print(f"  🔄 Updating index for new cutoff date: {cutoff_date_str}")
            
            # Get new videos for the updated cutoff date
            new_index = create_channel_index(channel_url, channel_name, cutoff_date_str, dest_path)
            if new_index and new_index.get('videos'):
                # Merge with existing index
                new_videos = list(new_index['videos'].values())
                index_data = update_unified_index(index_data, new_videos, cutoff_date_str)
                save_index_file(dest_path, cutoff_date_str, index_data)
                print(f"  ✅ Updated index: {index_data['total_videos']} total videos")
            else:
                # Just update the cutoff date tracking
                # Initialize missing fields for backward compatibility
                if 'cutoff_dates' not in index_data:
                    index_data['cutoff_dates'] = []
                if 'index_history' not in index_data:
                    index_data['index_history'] = []
                
                if cutoff_date_str not in index_data['cutoff_dates']:
                    index_data['cutoff_dates'].append(cutoff_date_str)
                    index_data['cutoff_dates'] = sorted(index_data['cutoff_dates'])
                index_data['current_cutoff_date'] = cutoff_date_str
                index_data['last_updated'] = datetime.now().isoformat()
                save_index_file(dest_path, cutoff_date_str, index_data)
                print(f"  📋 Updated cutoff date tracking")
        else:
            print(f"  📋 Using existing index ({index_data['total_videos']} videos)")
    
    
    # Step 2: Load existing downloads if skip_existing is enabled
    downloaded_ids = set()
    if skip_existing:
        redownload_deleted = config.get('redownload_deleted', False)
        
        # Use the appropriate function based on redownload_deleted setting
        if redownload_deleted:
            # Only skip videos that actually exist on disk
            downloaded_ids = get_actually_existing_video_ids(dest_path)
            print(f"  📁 Found {len(downloaded_ids)} already downloaded videos")
            print(f"     🔄 Re-download deleted: ENABLED (will re-download missing files)")
        else:
            # Skip all videos in control file (including deleted ones)
            downloaded_ids = get_existing_video_ids(dest_path, redownload_deleted)
            print(f"  📁 Found {len(downloaded_ids)} already downloaded videos")
            print(f"     🔄 Re-download deleted: DISABLED (maintains download history)")
        
        # Show count of videos that will be re-downloaded if deleted
        if redownload_deleted:
            control_data = load_control_file(dest_path)
            total_in_history = len(control_data.get('downloaded_videos', {}))
            deleted_count = total_in_history - len(downloaded_ids)
            if deleted_count > 0:
                print(f"     📥 Will re-download {deleted_count} previously downloaded but deleted videos")
    
    # Step 3: Determine what needs to be downloaded
    indexed_video_ids = set(index_data.get('video_ids', []))
    videos_to_download = indexed_video_ids - downloaded_ids if skip_existing else indexed_video_ids
    
    if not videos_to_download:
        print(f"  ✅ All indexed videos already downloaded for {channel_name}")
        return True
    
    print(f"  📥 Will download {len(videos_to_download)} new videos")
    
    # Step 4: Create video ID list for yt-dlp
    video_urls = []
    for video_id in videos_to_download:
        video_info = index_data['videos'].get(video_id)
        if video_info and video_info.get('webpage_url'):
            video_urls.append(video_info['webpage_url'])
    
    if not video_urls:
        print(f"  ⚠️  No valid video URLs found for download")
        return True
    
    # Step 5: Download the videos
    download_metadata = config.get('download_metadata', True)
    transcript_languages = config.get('transcript_languages', [])
    # Enable transcript download if transcript_languages is specified
    download_transcript = config.get('download_transcript', bool(transcript_languages))
    
    return download_videos_from_list(video_urls, dest_dir, output_format, content_type, 
                                   download_format, download_metadata, download_transcript,
                                   transcript_languages)


def download_videos_from_list(video_urls: List[str], dest_dir: str, output_format: str, 
                             content_type: str, download_format: Optional[str] = None,
                             download_metadata: bool = False, download_transcript: bool = False,
                             transcript_languages: List[str] = None) -> bool:
    """Download specific videos from a list of URLs with optional metadata and transcripts."""
    
    # Determine download format
    if not download_format:
        if content_type == "audio":
            download_format = "bestaudio/best"
        else:
            download_format = "best"
    
    # Create subfolder structure: dest_dir/video_name/files
    # Use a template that will create individual folders for each video
    output_template = os.path.join(dest_dir, f"{output_format}", f"{output_format}.%(ext)s")
    
    # Build yt-dlp command
    cmd = [
        'yt-dlp',
        '--output', output_template,
        '--restrict-filenames',  # Replace special characters in filenames
        '--no-overwrites',       # Don't overwrite existing files
        '--continue',            # Resume incomplete downloads
        '--write-info-json',     # Save metadata (always enabled)
        '--write-description',   # Save video description (always enabled)
        '--ignore-errors',       # Continue on download errors
    ]
    
    # Add metadata options
    if download_metadata:
        cmd.extend([
            '--write-thumbnail',     # Download thumbnail image
            '--write-annotations',   # Download annotations if available
        ])
        # Note: Removed --write-all-thumbnails to get only the best quality thumbnail
        print(f"  🖼️  Metadata download: ENABLED (best quality thumbnail, annotations)")
    else:
        print(f"  🖼️  Metadata download: DISABLED")
    
    # Add transcript options
    if download_transcript:
        cmd.extend([
            '--write-subs',          # Download subtitle files
            '--write-auto-subs',     # Download auto-generated subtitles
            '--convert-subs', 'srt', # Convert subtitles to SRT format
        ])
        
        # Add specific languages if provided
        if transcript_languages:
            lang_string = ','.join(transcript_languages)
            cmd.extend(['--sub-langs', lang_string])
            print(f"  📝 Transcript download: ENABLED (languages: {lang_string})")
        else:
            cmd.extend(['--sub-langs', 'all'])
            print(f"  📝 Transcript download: ENABLED (all languages)")
    else:
        print(f"  📝 Transcript download: DISABLED")
    
    # Add format specification
    if download_format:
        cmd.extend(['--format', download_format])
    
    # Add audio-specific options
    if content_type == "audio":
        cmd.extend([
            '--extract-audio',           # Extract audio from video
            '--audio-format', 'mp3',     # Convert to mp3 if not already
            '--audio-quality', '0',      # Best audio quality
            '--embed-metadata',          # Embed metadata in audio file
            '--add-metadata',            # Add metadata to file
        ])
    
    # Add video URLs
    cmd.extend(video_urls)
    
    print(f"  🚀 Starting download of {len(video_urls)} videos...")
    print(f"     Content type: {content_type}")
    print(f"     Format: {download_format}")
    print(f"     Organization: Each video in its own subfolder")
    print("-" * 50)
    
    try:
        # Execute yt-dlp command
        start_time = time.time()
        result = subprocess.run(cmd, check=True)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"\n✅ Download completed!")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Videos processed: {len(video_urls)}")
        print(f"   Organization: Content organized in individual subfolders")
        
        # Post-process thumbnails to keep only the highest resolution
        if download_metadata:
            cleanup_thumbnails(dest_dir, output_format)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during download: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  Download interrupted by user")
        return False


def cleanup_thumbnails(dest_dir: str, output_format: str):
    """Remove lower resolution thumbnails, keeping only the highest resolution one."""
    
    print(f"  🖼️  Optimizing thumbnails (keeping highest resolution only)...")
    
    dest_path = Path(dest_dir)
    if not dest_path.exists():
        return
    
    # Find all subdirectories (video folders)
    video_dirs = [d for d in dest_path.iterdir() if d.is_dir()]
    
    thumbnails_processed = 0
    thumbnails_removed = 0
    
    for video_dir in video_dirs:
        # Find all thumbnail files in this video directory
        thumbnail_files = []
        
        # Look for common thumbnail extensions
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
            thumbnail_files.extend(video_dir.glob(ext))
        
        if len(thumbnail_files) <= 1:
            continue  # No cleanup needed if 1 or fewer thumbnails
        
        # Group thumbnails by base name (same video, different resolutions)
        thumbnail_groups = {}
        for thumb_file in thumbnail_files:
            # Extract base name (everything before the resolution identifier)
            name_parts = thumb_file.stem.split('.')
            if len(name_parts) >= 2:
                # Assume format: basename.resolution.ext
                base_name = '.'.join(name_parts[:-1])
                if base_name not in thumbnail_groups:
                    thumbnail_groups[base_name] = []
                thumbnail_groups[base_name].append(thumb_file)
        
        # For each group, keep only the largest file (highest resolution)
        for base_name, thumb_list in thumbnail_groups.items():
            if len(thumb_list) <= 1:
                continue
            
            # Find the largest thumbnail (highest resolution)
            largest_thumb = max(thumb_list, key=lambda f: f.stat().st_size)
            
            # Remove all other thumbnails
            for thumb_file in thumb_list:
                if thumb_file != largest_thumb:
                    try:
                        thumb_file.unlink()
                        thumbnails_removed += 1
                    except Exception as e:
                        print(f"     Warning: Could not remove {thumb_file.name}: {e}")
            
            thumbnails_processed += 1
    
    if thumbnails_processed > 0:
        print(f"     Processed {thumbnails_processed} thumbnail groups")
        print(f"     Removed {thumbnails_removed} lower resolution thumbnails")
        print(f"     Kept highest resolution thumbnails only")


def process_channels_batch(config_file: str, download_format: Optional[str] = None, 
                          max_channels: Optional[int] = None, 
                          skip_existing: bool = True, force_reindex: bool = False,
                          selected_channels: Optional[List[str]] = None) -> Dict[str, bool]:
    """Process multiple channels from configuration file with indexing."""
    
    # Load configuration
    channels_config = load_channels_config(config_file)
    if not channels_config:
        return {}
    
    # Filter by selected channels if specified
    if selected_channels:
        # Convert selected channels to lowercase for case-insensitive matching
        selected_lower = [name.lower() for name in selected_channels]
        
        # Filter channels by name
        filtered_config = []
        found_channels = []
        
        for config in channels_config:
            channel_name = config.get('channel_name', '').lower()
            if channel_name in selected_lower:
                filtered_config.append(config)
                found_channels.append(config.get('channel_name', ''))
        
        # Report which channels were found/not found
        not_found = []
        for selected in selected_channels:
            if not any(selected.lower() == found.lower() for found in found_channels):
                not_found.append(selected)
        
        if not_found:
            print(f"⚠️  Channels not found in configuration: {', '.join(not_found)}")
        
        if not filtered_config:
            print(f"❌ No matching channels found for: {', '.join(selected_channels)}")
            return {}
        
        channels_config = filtered_config
        print(f"🎯 Selected {len(channels_config)} channels: {', '.join(found_channels)}")
    
    # Limit number of channels if specified
    if max_channels:
        channels_config = channels_config[:max_channels]
    
    print(f"Processing {len(channels_config)} channels from {config_file}")
    if selected_channels:
        print(f"🔍 Channel selection: ENABLED ({len(selected_channels)} requested)")
    print(f"🔍 Indexing: {'FORCE REINDEX' if force_reindex else 'USE CACHE'}")
    print(f"⏭️  Skip existing: {'ENABLED' if skip_existing else 'DISABLED'}")
    print("=" * 60)
    
    results = {}
    successful = 0
    failed = 0
    total_indexed = 0
    total_downloaded = 0
    
    for i, config in enumerate(channels_config, 1):
        print(f"\n[{i}/{len(channels_config)}] Processing channel: {config.get('channel_name', 'Unknown')}")
        
        # Validate configuration
        if not validate_channel_config(config):
            results[config.get('channel_name', f'Channel_{i}')] = False
            failed += 1
            continue
        
        # Process channel with indexing
        success = download_channel_with_index(config, download_format, skip_existing, force_reindex)
        results[config['channel_name']] = success
        
        if success:
            successful += 1
        else:
            failed += 1
        
        # Add a small delay between downloads to be respectful
        if i < len(channels_config):
            print("⏳ Waiting 3 seconds before next channel...")
            time.sleep(3)
    
    # Print summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total channels: {len(channels_config)}")
    if selected_channels:
        print(f"Selected channels: {len(selected_channels)} requested")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed channels:")
        for channel, success in results.items():
            if not success:
                print(f"  ❌ {channel}")
    
    if successful > 0:
        print("\nSuccessful channels:")
        for channel, success in results.items():
            if success:
                print(f"  ✅ {channel}")
    
    return results


def main():
    """Main function to handle command line arguments and execution."""
    parser = argparse.ArgumentParser(
        description="Download YouTube channel content with indexing and skip functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Batch processing with indexing:
    python youtube_channel_downloader_indexed.py --config channels_config.json

  Process specific channels only:
    python youtube_channel_downloader_indexed.py --config channels_config_full.json --channels "ColdFusion,PBoyle,Finansowaedukacja"

  Force reindex all channels:
    python youtube_channel_downloader_indexed.py --config channels_config.json --force-reindex

  Process without skipping existing downloads:
    python youtube_channel_downloader_indexed.py --config channels_config.json --no-skip

  Process only first 3 channels:
    python youtube_channel_downloader_indexed.py --config test_channels.json --max-channels 3

  Combine channel selection with other options:
    python youtube_channel_downloader_indexed.py --config channels_config_full.json --channels "Asianometry,CopernicusCenter" --force-reindex
        """
    )
    
    # Batch processing arguments
    parser.add_argument('--config', required=True, help='JSON configuration file for batch processing')
    parser.add_argument('--max-channels', type=int, help='Maximum number of channels to process')
    parser.add_argument('--no-skip', action='store_true', help='Disable skipping of already downloaded videos')
    parser.add_argument('--force-reindex', action='store_true', help='Force recreation of channel indexes')
    parser.add_argument('--channels', help='Comma-separated list of specific channel names to process (e.g., "ColdFusion,PBoyle,Finansowaedukacja")')
    
    # Common arguments
    parser.add_argument('--format', help='Download format (e.g., bestaudio/best, best)')
    
    args = parser.parse_args()
    
    # Check if yt-dlp is available
    if not check_dependencies():
        sys.exit(1)
    
    # Determine skip setting
    skip_existing = not args.no_skip
    
    # Parse selected channels if provided
    selected_channels = None
    if args.channels:
        selected_channels = [name.strip() for name in args.channels.split(',') if name.strip()]
        if not selected_channels:
            print("Error: Invalid channel list format")
            sys.exit(1)
    
    # Process channels
    print("Running in batch processing mode with indexing...")
    results = process_channels_batch(
        args.config, 
        args.format, 
        args.max_channels, 
        skip_existing, 
        args.force_reindex,
        selected_channels
    )
    
    # Exit with error code if any downloads failed
    if any(not success for success in results.values()):
        sys.exit(1)
    
    # Automatically update control files
    print("\n🔄 Updating download control files...")
    try:
        result = subprocess.run([
            sys.executable, 
            "create_download_control_v2.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Control files updated successfully!")
        else:
            print(f"⚠️  Warning: Control file update failed with return code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
    except Exception as e:
        print(f"⚠️  Warning: Could not run control file update: {e}")
    
    # Run content summarization for channels with summarize="yes"
    print("\n🤖 Running content summarization for enabled channels...")
    try:
        cmd = [sys.executable, "content_summarizer.py", "--config", args.config]
        if selected_channels:
            cmd.extend(["--channels", args.channels])
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Content summarization completed successfully!")
        else:
            print(f"⚠️  Warning: Content summarization failed with return code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
    except Exception as e:
        print(f"⚠️  Warning: Could not run content summarization: {e}")
    
    print("\n🎉 Processing completed!")


if __name__ == "__main__":
    main()
