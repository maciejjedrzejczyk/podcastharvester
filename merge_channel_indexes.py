#!/usr/bin/env python3
"""
Merge Channel Indexes Script for PodcastHarvester

This script merges multiple date-specific channel index files into a single
unified index per channel, preserving all historical data while enabling
the new single-index system.

Usage:
    python3 merge_channel_indexes.py [--dry-run] [--backup]
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import argparse


def find_channel_indexes(downloads_dir: Path) -> Dict[str, List[Path]]:
    """Find all channel index files grouped by channel directory."""
    channel_indexes = {}
    
    for channel_dir in downloads_dir.iterdir():
        if not channel_dir.is_dir():
            continue
            
        # Find all channel index files in this directory
        index_files = list(channel_dir.glob('.channel_index_*.json'))
        if index_files:
            channel_indexes[channel_dir.name] = sorted(index_files)
    
    return channel_indexes


def load_index_file(index_path: Path) -> Dict:
    """Load and parse a channel index file."""
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  ⚠️  Error loading {index_path.name}: {e}")
        return {}


def merge_channel_indexes(index_files: List[Path]) -> Dict:
    """Merge multiple channel index files into a unified structure."""
    if not index_files:
        return {}
    
    # Load all index files
    indexes = []
    for index_file in index_files:
        index_data = load_index_file(index_file)
        if index_data:
            indexes.append(index_data)
    
    if not indexes:
        return {}
    
    # Use the most recent index as the base
    base_index = max(indexes, key=lambda x: x.get('created_date', ''))
    
    # Create unified structure
    unified_index = {
        'channel_name': base_index.get('channel_name', ''),
        'channel_url': base_index.get('channel_url', ''),
        'created_date': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
        'index_history': [],
        'videos': {},
        'video_ids': [],
        'cutoff_dates': set(),
        'total_videos': 0,
        'date_range': {'earliest': None, 'latest': None}
    }
    
    # Merge all videos from all indexes
    all_videos = {}
    all_cutoff_dates = set()
    
    for index in indexes:
        # Track cutoff dates
        cutoff_date = index.get('cutoff_date')
        if cutoff_date:
            all_cutoff_dates.add(cutoff_date)
        
        # Add index to history
        unified_index['index_history'].append({
            'cutoff_date': cutoff_date,
            'created_date': index.get('created_date'),
            'total_videos': index.get('total_videos', 0),
            'source_file': None  # Will be set when saving
        })
        
        # Merge videos
        videos = index.get('videos', {})
        for video_id, video_data in videos.items():
            if video_id not in all_videos:
                all_videos[video_id] = video_data
            else:
                # Keep the video with more complete data
                existing = all_videos[video_id]
                if len(str(video_data)) > len(str(existing)):
                    all_videos[video_id] = video_data
    
    # Update unified index with merged data
    unified_index['videos'] = all_videos
    unified_index['video_ids'] = list(all_videos.keys())
    unified_index['cutoff_dates'] = sorted(list(all_cutoff_dates))
    unified_index['total_videos'] = len(all_videos)
    
    # Calculate overall date range
    video_dates = []
    for video in all_videos.values():
        upload_date = video.get('upload_date')
        if upload_date:
            video_dates.append(upload_date)
    
    if video_dates:
        unified_index['date_range'] = {
            'earliest': min(video_dates),
            'latest': max(video_dates)
        }
    
    return unified_index


def backup_index_files(index_files: List[Path], backup_dir: Path):
    """Create backups of original index files."""
    backup_dir.mkdir(exist_ok=True)
    
    for index_file in index_files:
        backup_path = backup_dir / index_file.name
        shutil.copy2(index_file, backup_path)
        print(f"    📋 Backed up {index_file.name}")


def save_unified_index(channel_dir: Path, unified_index: Dict, original_files: List[Path]):
    """Save the unified index and update history with source files."""
    # Update history with source file names
    for i, history_entry in enumerate(unified_index['index_history']):
        if i < len(original_files):
            history_entry['source_file'] = original_files[i].name
    
    # Save unified index
    unified_path = channel_dir / '.channel_index.json'
    
    try:
        with open(unified_path, 'w', encoding='utf-8') as f:
            json.dump(unified_index, f, indent=2, ensure_ascii=False)
        print(f"    ✅ Created unified index: {unified_path.name}")
        return True
    except Exception as e:
        print(f"    ❌ Error saving unified index: {e}")
        return False


def remove_old_indexes(index_files: List[Path], dry_run: bool = False):
    """Remove old date-specific index files."""
    for index_file in index_files:
        if dry_run:
            print(f"    🗑️  Would remove: {index_file.name}")
        else:
            try:
                index_file.unlink()
                print(f"    🗑️  Removed: {index_file.name}")
            except Exception as e:
                print(f"    ⚠️  Error removing {index_file.name}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Merge channel indexes for PodcastHarvester')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    parser.add_argument('--backup', action='store_true',
                       help='Create backups of original index files')
    parser.add_argument('--downloads-dir', default='downloads',
                       help='Path to downloads directory (default: downloads)')
    
    args = parser.parse_args()
    
    downloads_dir = Path(args.downloads_dir)
    
    if not downloads_dir.exists():
        print(f"❌ Downloads directory not found: {downloads_dir}")
        return 1
    
    print("🔄 PodcastHarvester Channel Index Merger")
    print("=" * 50)
    
    # Find all channel indexes
    channel_indexes = find_channel_indexes(downloads_dir)
    
    if not channel_indexes:
        print("ℹ️  No channel index files found.")
        return 0
    
    print(f"📊 Found {len(channel_indexes)} channels with index files:")
    
    total_processed = 0
    total_merged = 0
    
    for channel_name, index_files in channel_indexes.items():
        print(f"\n📁 Channel: {channel_name}")
        print(f"   Found {len(index_files)} index files:")
        
        for index_file in index_files:
            print(f"     - {index_file.name}")
        
        # Check if unified index already exists
        channel_dir = downloads_dir / channel_name
        unified_path = channel_dir / '.channel_index.json'
        
        if unified_path.exists():
            print(f"   ℹ️  Unified index already exists: {unified_path.name}")
            if not args.dry_run:
                # Still remove old indexes if they exist
                old_indexes = [f for f in index_files if f.name != '.channel_index.json']
                if old_indexes:
                    print(f"   🧹 Cleaning up {len(old_indexes)} old index files...")
                    remove_old_indexes(old_indexes, args.dry_run)
            continue
        
        if len(index_files) == 1:
            # Single index file - just rename it
            old_file = index_files[0]
            if args.dry_run:
                print(f"   🔄 Would rename {old_file.name} to .channel_index.json")
            else:
                try:
                    old_file.rename(unified_path)
                    print(f"   ✅ Renamed {old_file.name} to .channel_index.json")
                    total_processed += 1
                except Exception as e:
                    print(f"   ❌ Error renaming: {e}")
        else:
            # Multiple index files - merge them
            if args.dry_run:
                print(f"   🔄 Would merge {len(index_files)} index files")
            else:
                # Create backup if requested
                if args.backup:
                    backup_dir = channel_dir / 'index_backups'
                    backup_index_files(index_files, backup_dir)
                
                # Merge indexes
                print(f"   🔄 Merging {len(index_files)} index files...")
                unified_index = merge_channel_indexes(index_files)
                
                if unified_index:
                    if save_unified_index(channel_dir, unified_index, index_files):
                        # Remove old index files
                        remove_old_indexes(index_files, args.dry_run)
                        total_processed += 1
                        total_merged += len(index_files)
                    else:
                        print(f"   ❌ Failed to save unified index")
                else:
                    print(f"   ❌ Failed to merge index files")
        
        total_processed += 1
    
    print(f"\n✅ Processing complete!")
    print(f"   📊 Channels processed: {total_processed}")
    if total_merged > 0:
        print(f"   🔄 Index files merged: {total_merged}")
    
    if args.dry_run:
        print(f"\n💡 This was a dry run. Use without --dry-run to apply changes.")
    
    return 0


if __name__ == '__main__':
    exit(main())
