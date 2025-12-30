#!/usr/bin/env python3
"""
Send all existing summaries via Signal API
"""

import argparse
import time
from pathlib import Path
from send_summary_notification import load_notification_config, send_signal_message

def find_all_summaries(downloads_dir: Path):
    """Find all final_summary.txt files in downloads directory."""
    summaries = []
    
    for summary_file in downloads_dir.rglob("content_summary/final_summary.txt"):
        video_folder = summary_file.parent.parent
        summaries.append({
            'video_folder': video_folder,
            'summary_file': summary_file
        })
    
    return summaries

def main():
    parser = argparse.ArgumentParser(description="Send all existing summaries via Signal")
    parser.add_argument('--downloads-dir', required=True, help='Path to downloads directory')
    parser.add_argument('--delay', type=int, default=2, help='Delay between messages in seconds (default: 2)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be sent without sending')
    args = parser.parse_args()
    
    downloads_dir = Path(args.downloads_dir)
    
    if not downloads_dir.exists():
        print(f"❌ Directory not found: {downloads_dir}")
        return
    
    # Load config
    config = load_notification_config()
    if not config:
        print("❌ notification_config.json not found")
        return
    
    if not config.get('enabled', False):
        print("⚠️  Notifications are disabled in config")
        return
    
    # Find all summaries
    print(f"🔍 Scanning for summaries in {downloads_dir}...")
    summaries = find_all_summaries(downloads_dir)
    
    if not summaries:
        print("❌ No summaries found")
        return
    
    print(f"📋 Found {len(summaries)} summaries")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - Would send:")
        for i, item in enumerate(summaries, 1):
            print(f"  {i}. {item['video_folder'].name}")
        return
    
    # Send all summaries
    print(f"\n📤 Sending {len(summaries)} notifications (delay: {args.delay}s)...\n")
    
    sent = 0
    failed = 0
    
    for i, item in enumerate(summaries, 1):
        video_folder = item['video_folder']
        summary_file = item['summary_file']
        
        print(f"[{i}/{len(summaries)}] {video_folder.name}")
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_text = f.read()
            
            message = f"📺 Summary: {video_folder.name}\n\n{summary_text}"
            
            if send_signal_message(message, config):
                print(f"  ✅ Sent")
                sent += 1
            else:
                print(f"  ❌ Failed")
                failed += 1
            
            # Delay between messages to avoid rate limiting
            if i < len(summaries):
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Sent: {sent}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(summaries)}")

if __name__ == "__main__":
    main()
