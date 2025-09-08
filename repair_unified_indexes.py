#!/usr/bin/env python3
"""
Repair Unified Indexes Script for PodcastHarvester

This script repairs unified channel index files that may be missing required fields
due to incomplete migration or other issues.

Usage:
    python3 repair_unified_indexes.py [--dry-run] [--downloads-dir PATH]
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict


def repair_index_file(index_path: Path, dry_run: bool = False) -> bool:
    """Repair a unified index file by adding missing fields."""
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    except Exception as e:
        print(f"    ❌ Error reading {index_path.name}: {e}")
        return False
    
    # Track what needs to be repaired
    repairs_needed = []
    
    # Check and add missing fields
    if 'cutoff_dates' not in index_data:
        repairs_needed.append('cutoff_dates')
        if not dry_run:
            # Try to infer from old cutoff_date field
            old_cutoff = index_data.get('cutoff_date')
            index_data['cutoff_dates'] = [old_cutoff] if old_cutoff else []
    
    if 'index_history' not in index_data:
        repairs_needed.append('index_history')
        if not dry_run:
            # Create basic history entry
            index_data['index_history'] = [{
                'cutoff_date': index_data.get('cutoff_date', 'unknown'),
                'created_date': index_data.get('created_date', datetime.now().isoformat()),
                'total_videos': index_data.get('total_videos', 0),
                'source_file': 'repaired_legacy'
            }]
    
    if 'current_cutoff_date' not in index_data:
        repairs_needed.append('current_cutoff_date')
        if not dry_run:
            # Use the old cutoff_date or the latest from cutoff_dates
            index_data['current_cutoff_date'] = (
                index_data.get('cutoff_date') or 
                (max(index_data['cutoff_dates']) if index_data.get('cutoff_dates') else 'unknown')
            )
    
    if 'last_updated' not in index_data:
        repairs_needed.append('last_updated')
        if not dry_run:
            index_data['last_updated'] = index_data.get('created_date', datetime.now().isoformat())
    
    # Ensure video_ids exists and matches videos
    if 'video_ids' not in index_data or not index_data.get('video_ids'):
        repairs_needed.append('video_ids')
        if not dry_run:
            videos = index_data.get('videos', {})
            index_data['video_ids'] = list(videos.keys())
    
    # Update total_videos to match actual count
    videos = index_data.get('videos', {})
    actual_count = len(videos)
    if index_data.get('total_videos', 0) != actual_count:
        repairs_needed.append('total_videos')
        if not dry_run:
            index_data['total_videos'] = actual_count
    
    if repairs_needed:
        if dry_run:
            print(f"    🔧 Would repair: {', '.join(repairs_needed)}")
        else:
            # Save the repaired index
            try:
                with open(index_path, 'w', encoding='utf-8') as f:
                    json.dump(index_data, f, indent=2, ensure_ascii=False)
                print(f"    ✅ Repaired: {', '.join(repairs_needed)}")
                return True
            except Exception as e:
                print(f"    ❌ Error saving repaired index: {e}")
                return False
    else:
        print(f"    ✅ No repairs needed")
        return True


def find_unified_indexes(downloads_dir: Path) -> list:
    """Find all unified channel index files."""
    index_files = []
    
    for channel_dir in downloads_dir.iterdir():
        if not channel_dir.is_dir():
            continue
        
        index_file = channel_dir / '.channel_index.json'
        if index_file.exists():
            index_files.append(index_file)
    
    return index_files


def main():
    parser = argparse.ArgumentParser(description='Repair unified channel indexes for PodcastHarvester')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be repaired without making changes')
    parser.add_argument('--downloads-dir', default='downloads',
                       help='Path to downloads directory (default: downloads)')
    
    args = parser.parse_args()
    
    downloads_dir = Path(args.downloads_dir)
    
    if not downloads_dir.exists():
        print(f"❌ Downloads directory not found: {downloads_dir}")
        return 1
    
    print("🔧 PodcastHarvester Unified Index Repair Tool")
    print("=" * 50)
    
    # Find all unified index files
    index_files = find_unified_indexes(downloads_dir)
    
    if not index_files:
        print("ℹ️  No unified index files found.")
        return 0
    
    print(f"📊 Found {len(index_files)} unified index files:")
    
    repaired_count = 0
    error_count = 0
    
    for index_file in index_files:
        channel_name = index_file.parent.name
        print(f"\n📁 Channel: {channel_name}")
        
        if repair_index_file(index_file, args.dry_run):
            repaired_count += 1
        else:
            error_count += 1
    
    print(f"\n✅ Repair complete!")
    print(f"   📊 Files processed: {len(index_files)}")
    print(f"   ✅ Successfully repaired: {repaired_count}")
    if error_count > 0:
        print(f"   ❌ Errors encountered: {error_count}")
    
    if args.dry_run:
        print(f"\n💡 This was a dry run. Use without --dry-run to apply repairs.")
    
    return 0


if __name__ == '__main__':
    exit(main())
