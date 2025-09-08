#!/usr/bin/env python3
"""
Create download control files for tracking already downloaded content.
This script scans existing downloads and creates control files that can be used
to skip already downloaded content in future runs.
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set


def get_file_hash(filepath: Path) -> str:
    """Generate a hash for a file to detect changes."""
    if not filepath.exists():
        return ""
    
    # For large files, just use size and modification time
    stat = filepath.stat()
    content = f"{stat.st_size}_{stat.st_mtime}"
    return hashlib.md5(content.encode()).hexdigest()


def extract_video_info(info_json_path: Path) -> Dict:
    """Extract key information from yt-dlp info.json file."""
    try:
        with open(info_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            'video_id': data.get('id', ''),
            'title': data.get('title', ''),
            'upload_date': data.get('upload_date', ''),
            'duration': data.get('duration', 0),
            'uploader': data.get('uploader', ''),
            'channel_id': data.get('channel_id', ''),
            'webpage_url': data.get('webpage_url', ''),
            'filesize': data.get('filesize', 0)
        }
    except Exception as e:
        print(f"Error reading {info_json_path}: {e}")
        return {}


def find_matching_files(info_file: Path, channel_dir: Path) -> Dict:
    """Find files that match the info.json file."""
    # Remove .info.json to get base name
    base_name = info_file.name.replace('.info.json', '')
    
    # Also try without .info part
    alt_base_name = base_name.replace('.info', '')
    
    files = {
        'info_json': info_file.name,
        'description': None,
        'audio': None,
        'video': None,
        'thumbnails': [],
        'subtitles': [],
        'annotations': None
    }
    
    # Look for description file
    for base in [base_name, alt_base_name]:
        desc_file = channel_dir / f"{base}.description"
        if desc_file.exists():
            files['description'] = desc_file.name
            break
    
    # Look for audio files
    for base in [base_name, alt_base_name]:
        for ext in ['.mp3', '.m4a', '.wav', '.opus']:
            audio_file = channel_dir / f"{base}{ext}"
            if audio_file.exists():
                files['audio'] = audio_file.name
                break
        if files['audio']:
            break
    
    # Look for video files
    for base in [base_name, alt_base_name]:
        for ext in ['.mp4', '.webm', '.mkv', '.avi']:
            video_file = channel_dir / f"{base}{ext}"
            if video_file.exists():
                files['video'] = video_file.name
                break
        if files['video']:
            break
    
    # Look for thumbnail files
    for base in [base_name, alt_base_name]:
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            thumb_file = channel_dir / f"{base}{ext}"
            if thumb_file.exists():
                files['thumbnails'].append(thumb_file.name)
    
    # Look for subtitle files
    for base in [base_name, alt_base_name]:
        # Check for various subtitle patterns with language codes
        for pattern in [f"{base}.*.srt", f"{base}.srt"]:
            for sub_file in channel_dir.glob(pattern):
                if sub_file.name not in files['subtitles']:
                    files['subtitles'].append(sub_file.name)
        
        # Also check for specific language patterns
        for lang in ['en', 'pl', 'auto']:
            for ext in ['srt', 'vtt', 'ass', 'ssa']:
                sub_file = channel_dir / f"{base}.{lang}.{ext}"
                if sub_file.exists() and sub_file.name not in files['subtitles']:
                    files['subtitles'].append(sub_file.name)
    
    # Look for annotations file
    for base in [base_name, alt_base_name]:
        ann_file = channel_dir / f"{base}.annotations.xml"
        if ann_file.exists():
            files['annotations'] = ann_file.name
            break
    
    return files


def scan_channel_directory(channel_dir: Path) -> Dict:
    """Scan a channel directory and create control data, handling both flat and subfolder structures."""
    control_data = {
        'channel_name': channel_dir.name,
        'last_updated': datetime.now().isoformat(),
        'downloaded_videos': {},
        'file_hashes': {},
        'statistics': {
            'total_videos': 0,
            'total_audio_files': 0,
            'total_video_files': 0,
            'total_thumbnails': 0,
            'total_subtitles': 0,
            'total_annotations': 0,
            'total_size_bytes': 0,
            'date_range': {'earliest': None, 'latest': None}
        }
    }
    
    # Find all info.json files (these indicate downloaded videos)
    # Check both flat structure and subfolder structure
    info_files = []
    
    # Flat structure: files directly in channel directory
    info_files.extend(list(channel_dir.glob('*.info.json')))
    
    # Subfolder structure: files in subdirectories
    for subdir in channel_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('.'):
            info_files.extend(list(subdir.glob('*.info.json')))
    
    for info_file in info_files:
        # Determine the working directory (either channel_dir or subdirectory)
        working_dir = info_file.parent
        
        # Extract video information
        video_info = extract_video_info(info_file)
        if not video_info.get('video_id'):
            continue
        
        video_id = video_info['video_id']
        upload_date = video_info.get('upload_date', '')
        
        # Find associated files in the same directory as the info.json file
        associated_files = find_matching_files(info_file, working_dir)
        
        # Calculate file sizes
        total_file_size = 0
        if associated_files['audio']:
            audio_path = working_dir / associated_files['audio']
            if audio_path.exists():
                control_data['statistics']['total_audio_files'] += 1
                size = audio_path.stat().st_size
                total_file_size += size
                control_data['statistics']['total_size_bytes'] += size
        
        if associated_files['video']:
            video_path = working_dir / associated_files['video']
            if video_path.exists():
                control_data['statistics']['total_video_files'] += 1
                size = video_path.stat().st_size
                total_file_size += size
                control_data['statistics']['total_size_bytes'] += size
        
        # Count thumbnails
        if associated_files['thumbnails']:
            control_data['statistics']['total_thumbnails'] += len(associated_files['thumbnails'])
            for thumb_name in associated_files['thumbnails']:
                thumb_path = working_dir / thumb_name
                if thumb_path.exists():
                    total_file_size += thumb_path.stat().st_size
                    control_data['statistics']['total_size_bytes'] += thumb_path.stat().st_size
        
        # Count subtitles
        if associated_files['subtitles']:
            control_data['statistics']['total_subtitles'] += len(associated_files['subtitles'])
            for sub_name in associated_files['subtitles']:
                sub_path = working_dir / sub_name
                if sub_path.exists():
                    total_file_size += sub_path.stat().st_size
                    control_data['statistics']['total_size_bytes'] += sub_path.stat().st_size
        
        # Count annotations
        if associated_files['annotations']:
            control_data['statistics']['total_annotations'] += 1
            ann_path = working_dir / associated_files['annotations']
            if ann_path.exists():
                total_file_size += ann_path.stat().st_size
                control_data['statistics']['total_size_bytes'] += ann_path.stat().st_size
        
        # Store video information with relative paths
        relative_files = {}
        for file_type, filename in associated_files.items():
            if filename:
                if isinstance(filename, list):
                    # Handle lists (like subtitles, thumbnails)
                    relative_files[file_type] = []
                    for individual_file in filename:
                        if working_dir != channel_dir:
                            # Store relative path from channel directory
                            relative_path = str(working_dir.relative_to(channel_dir) / individual_file)
                            relative_files[file_type].append(relative_path)
                        else:
                            relative_files[file_type].append(individual_file)
                else:
                    # Handle single files
                    if working_dir != channel_dir:
                        # Store relative path from channel directory
                        relative_path = str(working_dir.relative_to(channel_dir) / filename)
                        relative_files[file_type] = relative_path
                    else:
                        relative_files[file_type] = filename
        
        control_data['downloaded_videos'][video_id] = {
            'title': video_info.get('title', ''),
            'upload_date': upload_date,
            'duration': video_info.get('duration', 0),
            'uploader': video_info.get('uploader', ''),
            'webpage_url': video_info.get('webpage_url', ''),
            'files': relative_files,
            'file_size_bytes': total_file_size,
            'download_date': datetime.fromtimestamp(info_file.stat().st_mtime).isoformat(),
            'subfolder': str(working_dir.relative_to(channel_dir)) if working_dir != channel_dir else None
        }
        
        # Generate file hashes for integrity checking
        for file_type, filename in associated_files.items():
            if filename:
                if isinstance(filename, list):
                    # Handle lists (like subtitles, thumbnails)
                    for individual_file in filename:
                        file_path = working_dir / individual_file
                        if file_path.exists():
                            # Use relative path as key for consistency
                            if working_dir != channel_dir:
                                key = str(working_dir.relative_to(channel_dir) / individual_file)
                            else:
                                key = individual_file
                            control_data['file_hashes'][key] = get_file_hash(file_path)
                else:
                    # Handle single files (like audio, video, description)
                    file_path = working_dir / filename
                    if file_path.exists():
                        # Use relative path as key for consistency
                        if working_dir != channel_dir:
                            key = str(working_dir.relative_to(channel_dir) / filename)
                        else:
                            key = filename
                        control_data['file_hashes'][key] = get_file_hash(file_path)
        
        # Update statistics
        control_data['statistics']['total_videos'] += 1
        
        if upload_date:
            if not control_data['statistics']['date_range']['earliest'] or upload_date < control_data['statistics']['date_range']['earliest']:
                control_data['statistics']['date_range']['earliest'] = upload_date
            if not control_data['statistics']['date_range']['latest'] or upload_date > control_data['statistics']['date_range']['latest']:
                control_data['statistics']['date_range']['latest'] = upload_date
    
    return control_data


def load_existing_control_file(channel_dir: Path) -> Dict:
    """Load existing control file if it exists."""
    control_file = channel_dir / '.download_control.json'
    if control_file.exists():
        try:
            with open(control_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  ⚠️  Error loading existing control file: {e}")
    return None


def should_preserve_deleted_records(channel_dir: Path) -> bool:
    """Check if we should preserve records of deleted files based on channel configuration."""
    # Look for channel configuration files to determine redownload_deleted setting
    config_files = [
        Path("channels_config.json"),
        Path("channels_config_full.json"), 
        Path("test_channels.json")
    ]
    
    channel_name = channel_dir.name
    
    for config_file in config_files:
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    channels = json.load(f)
                    
                for channel in channels:
                    if channel.get('channel_name') == channel_name:
                        # Default to False (preserve deleted records) if not specified
                        return not channel.get('redownload_deleted', False)
            except Exception:
                continue
    
    # Default to preserving deleted records (safer option)
    return True


def create_control_file(channel_dir: Path) -> bool:
    """Create a control file for a channel directory, preserving deleted file records when appropriate."""
    if not channel_dir.exists() or not channel_dir.is_dir():
        print(f"Directory {channel_dir} does not exist or is not a directory")
        return False
    
    print(f"Scanning {channel_dir.name}...")
    
    # Load existing control file
    existing_control = load_existing_control_file(channel_dir)
    preserve_deleted = should_preserve_deleted_records(channel_dir)
    
    # Scan the directory for current files
    current_control_data = scan_channel_directory(channel_dir)
    
    # If we should preserve deleted records and have existing data, merge them
    if preserve_deleted and existing_control:
        print(f"  🔒 Preserving deleted file records (redownload_deleted: false)")
        
        # Start with existing downloaded_videos
        merged_downloaded_videos = existing_control.get('downloaded_videos', {}).copy()
        
        # Update with current files (this will update existing entries and add new ones)
        current_downloaded_videos = current_control_data.get('downloaded_videos', {})
        merged_downloaded_videos.update(current_downloaded_videos)
        
        # Merge file hashes (keep existing + add new)
        merged_file_hashes = existing_control.get('file_hashes', {}).copy()
        current_file_hashes = current_control_data.get('file_hashes', {})
        merged_file_hashes.update(current_file_hashes)
        
        # Use current statistics but update total_videos to include preserved records
        merged_statistics = current_control_data['statistics'].copy()
        merged_statistics['total_videos'] = len(merged_downloaded_videos)
        
        # Create final control data
        control_data = {
            'channel_name': channel_dir.name,
            'last_updated': datetime.now().isoformat(),
            'downloaded_videos': merged_downloaded_videos,
            'file_hashes': merged_file_hashes,
            'statistics': merged_statistics
        }
        
        preserved_count = len(merged_downloaded_videos) - len(current_downloaded_videos)
        if preserved_count > 0:
            print(f"  📋 Preserved {preserved_count} deleted file records")
    else:
        # Use current scan results only
        control_data = current_control_data
        if not preserve_deleted:
            print(f"  🔄 Rebuilding control file (redownload_deleted: true)")
    
    # Write control file
    control_file = channel_dir / '.download_control.json'
    try:
        with open(control_file, 'w', encoding='utf-8') as f:
            json.dump(control_data, f, indent=2, ensure_ascii=False)
        
        stats = control_data['statistics']
        print(f"  ✅ Created control file for {channel_dir.name}")
        print(f"     Videos: {stats['total_videos']}")
        print(f"     Audio files: {stats['total_audio_files']}")
        print(f"     Video files: {stats['total_video_files']}")
        print(f"     Thumbnails: {stats['total_thumbnails']}")
        print(f"     Subtitles: {stats['total_subtitles']}")
        print(f"     Annotations: {stats['total_annotations']}")
        print(f"     Total size: {stats['total_size_bytes'] / (1024*1024):.1f} MB")
        if stats['date_range']['earliest']:
            print(f"     Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating control file for {channel_dir.name}: {e}")
        return False


def main():
    """Main function to create control files for all channel directories."""
    downloads_dir = Path("/Users/matanyahu/Downloads/podcasts/downloads")
    
    if not downloads_dir.exists():
        print(f"Downloads directory {downloads_dir} does not exist")
        return
    
    print("Creating download control files...")
    print("=" * 50)
    
    # Find all channel directories
    channel_dirs = [d for d in downloads_dir.iterdir() if d.is_dir()]
    
    if not channel_dirs:
        print("No channel directories found")
        return
    
    successful = 0
    failed = 0
    
    for channel_dir in sorted(channel_dirs):
        if create_control_file(channel_dir):
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total channels: {len(channel_dirs)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        print(f"\nControl files created in each channel directory as '.download_control.json'")
        print("These files will be used to skip already downloaded content in future runs.")


if __name__ == "__main__":
    main()
