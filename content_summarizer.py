#!/usr/bin/env python3
"""
Content Summarization Script for PodcastHarvester

This script processes channels with summarize="yes" and creates:
1. 5-minute transcript chunks
2. Individual chunk summaries via LLM
3. Final content summary based on chunk summaries

Directory structure created:
- <video_folder>/chunks/ - 5-minute transcript segments
- <video_folder>/chunk_summaries/ - Individual chunk summaries
- <video_folder>/content_summary/ - Final video summary
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import urllib.request
import urllib.parse
import urllib.error

def parse_srt_timestamp(timestamp_str: str) -> float:
    """Convert SRT timestamp to seconds."""
    # Format: 00:00:20,000 --> 00:00:23,040
    time_part = timestamp_str.split(' --> ')[0]
    hours, minutes, seconds_ms = time_part.split(':')
    seconds, milliseconds = seconds_ms.split(',')
    
    total_seconds = (
        int(hours) * 3600 + 
        int(minutes) * 60 + 
        int(seconds) + 
        int(milliseconds) / 1000
    )
    return total_seconds

def parse_srt_file(srt_path: Path) -> List[Dict]:
    """Parse SRT file and return list of subtitle entries."""
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by double newlines to get individual subtitle blocks
        blocks = re.split(r'\n\s*\n', content.strip())
        subtitles = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Skip the sequence number (first line)
                timestamp_line = lines[1]
                text_lines = lines[2:]
                
                # Parse timestamp
                start_time = parse_srt_timestamp(timestamp_line)
                
                # Join text lines
                text = ' '.join(text_lines).strip()
                
                subtitles.append({
                    'start_time': start_time,
                    'text': text
                })
        
        return subtitles
    
    except Exception as e:
        print(f"❌ Error parsing SRT file {srt_path}: {e}")
        return []

def create_5min_chunks(subtitles: List[Dict], chunk_duration: int = 300) -> List[Dict]:
    """Create 5-minute chunks from subtitles."""
    chunks = []
    current_chunk = []
    chunk_start_time = 0
    chunk_number = 1
    
    for subtitle in subtitles:
        # If this subtitle starts a new 5-minute segment
        if subtitle['start_time'] >= chunk_start_time + chunk_duration:
            # Save current chunk if it has content
            if current_chunk:
                chunk_text = ' '.join([s['text'] for s in current_chunk])
                chunks.append({
                    'chunk_number': chunk_number,
                    'start_time': chunk_start_time,
                    'end_time': chunk_start_time + chunk_duration,
                    'text': chunk_text.strip()
                })
                chunk_number += 1
            
            # Start new chunk
            current_chunk = [subtitle]
            chunk_start_time = subtitle['start_time'] - (subtitle['start_time'] % chunk_duration)
        else:
            current_chunk.append(subtitle)
    
    # Add final chunk
    if current_chunk:
        chunk_text = ' '.join([s['text'] for s in current_chunk])
        chunks.append({
            'chunk_number': chunk_number,
            'start_time': chunk_start_time,
            'end_time': current_chunk[-1]['start_time'] + 60,  # Approximate end
            'text': chunk_text.strip()
        })
    
    return chunks

def save_chunks(chunks: List[Dict], chunks_dir: Path) -> None:
    """Save transcript chunks to individual files."""
    chunks_dir.mkdir(exist_ok=True)
    
    for chunk in chunks:
        chunk_file = chunks_dir / f"chunk_{chunk['chunk_number']:03d}.txt"
        
        # Format time for readability
        start_min = int(chunk['start_time'] // 60)
        start_sec = int(chunk['start_time'] % 60)
        end_min = int(chunk['end_time'] // 60)
        end_sec = int(chunk['end_time'] % 60)
        
        content = f"Chunk {chunk['chunk_number']}\n"
        content += f"Time: {start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}\n"
        content += f"Duration: ~{int((chunk['end_time'] - chunk['start_time']) / 60)} minutes\n\n"
        content += chunk['text']
        
        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(content)

import urllib.request
import urllib.parse
import urllib.error

# Global LLM configuration
LLM_CONFIG = None

def test_llm_connection() -> bool:
    """Test connection to LLM server."""
    if LLM_CONFIG is None:
        return False
    
    try:
        # Simple test request to check if server is available
        api_url = f"{LLM_CONFIG['server_url']}/v1/models"
        req = urllib.request.Request(api_url, headers={'Accept': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print(f"✅ LLM server connection successful")
                return True
            else:
                print(f"⚠️  LLM server responded with status {response.status}")
                return False
                
    except Exception as e:
        print(f"⚠️  LLM server connection test failed: {e}")
        print(f"   Server: {LLM_CONFIG['server_url']}")
        print(f"   This may be normal if the server doesn't support /v1/models endpoint")
        return False

def load_llm_config(config_path: Path = None) -> Dict:
    """Load LLM configuration from file."""
    global LLM_CONFIG
    
    if config_path is None:
        config_path = Path(__file__).parent / "llm_config.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            LLM_CONFIG = json.load(f)
        return LLM_CONFIG
    except Exception as e:
        print(f"❌ Error loading LLM configuration from {config_path}: {e}")
        print("   Please ensure llm_config.json exists and is properly formatted")
        sys.exit(1)

def truncate_text_to_context(text: str, max_tokens: int = 3000) -> str:
    """Truncate text to fit within context length, leaving room for system prompt and response."""
    # Rough estimation: 1 token ≈ 4 characters for most languages
    max_chars = max_tokens * 4
    
    if len(text) <= max_chars:
        return text
    
    # Truncate and add indication
    truncated = text[:max_chars - 100]  # Leave room for truncation message
    truncated += "\n\n[Note: Content truncated to fit context length]"
    return truncated

def call_llm_api(text: str, prompt_type: str = "chunk") -> Optional[str]:
    """Call LLM API for summarization using OpenAI-compatible format."""
    
    if LLM_CONFIG is None:
        print("❌ LLM configuration not loaded")
        return None
    
    # Get system prompt
    system_prompt = LLM_CONFIG["system_prompts"].get(prompt_type, "")
    if not system_prompt:
        print(f"❌ No system prompt found for type: {prompt_type}")
        return None
    
    # Truncate text to fit context length
    max_context = LLM_CONFIG.get("context_length", 4096)
    # Reserve space for system prompt, user prompt prefix, and response
    available_tokens = max_context - 1000  # Conservative estimate
    truncated_text = truncate_text_to_context(text, available_tokens)
    
    # Prepare user prompt
    if prompt_type == "chunk":
        user_prompt = f"Please summarize this transcript chunk:\n\n{truncated_text}"
    elif prompt_type == "final":
        user_prompt = f"Please create a final comprehensive summary based on these chunk summaries:\n\n{truncated_text}"
    else:
        user_prompt = truncated_text
    
    # Prepare API request
    api_url = f"{LLM_CONFIG['server_url']}/v1/chat/completions"
    
    payload = {
        "model": LLM_CONFIG["model_name"],
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": user_prompt
            }
        ],
        "temperature": LLM_CONFIG.get("temperature", 0.7),
        "max_tokens": 1000,  # Reasonable limit for summaries
        "stream": False
    }
    
    # Convert payload to JSON
    json_data = json.dumps(payload).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        api_url,
        data=json_data,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    
    # Make API call with retries
    max_retries = LLM_CONFIG.get("max_retries", 3)
    retry_delay = LLM_CONFIG.get("retry_delay", 2)
    timeout = LLM_CONFIG.get("request_timeout", 60)
    
    for attempt in range(max_retries):
        try:
            print(f"🤖 Calling LLM API for {prompt_type} summarization (attempt {attempt + 1}/{max_retries})...")
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    response_data = json.loads(response.read().decode('utf-8'))
                    
                    # Extract content from OpenAI-compatible response
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        content = response_data['choices'][0]['message']['content']
                        print(f"✅ Successfully received {prompt_type} summary ({len(content)} characters)")
                        return content.strip()
                    else:
                        print(f"❌ Invalid response format: {response_data}")
                        return None
                else:
                    print(f"❌ API request failed with status {response.status}")
                    if attempt < max_retries - 1:
                        print(f"   Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    continue
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No error details"
            print(f"❌ HTTP Error {e.code}: {e.reason}")
            print(f"   Error details: {error_body}")
            
            if attempt < max_retries - 1:
                print(f"   Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            continue
            
        except urllib.error.URLError as e:
            print(f"❌ URL Error: {e.reason}")
            if attempt < max_retries - 1:
                print(f"   Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            continue
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if attempt < max_retries - 1:
                print(f"   Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            continue
    
    print(f"❌ Failed to get {prompt_type} summary after {max_retries} attempts")
    return None

def process_video_folder(video_folder: Path, preferred_language: str = "pl") -> bool:
    """Process a single video folder for summarization."""
    print(f"📁 Processing: {video_folder.name}")
    
    # Find SRT file (prefer specified language, fallback to any available)
    srt_files = list(video_folder.glob("*.srt"))
    
    if not srt_files:
        print(f"   ⚠️  No SRT files found, skipping")
        return False
    
    # Try to find preferred language file
    preferred_srt = None
    for srt_file in srt_files:
        if f".{preferred_language}.srt" in srt_file.name:
            preferred_srt = srt_file
            break
    
    # If no preferred language, use first available
    if not preferred_srt:
        preferred_srt = srt_files[0]
        print(f"   ℹ️  Using {preferred_srt.name} (preferred language {preferred_language} not found)")
    else:
        print(f"   ✅ Using {preferred_srt.name}")
    
    # Create output directories
    chunks_dir = video_folder / "chunks"
    chunk_summaries_dir = video_folder / "chunk_summaries"
    content_summary_dir = video_folder / "content_summary"
    
    # Check if already processed
    final_summary_file = content_summary_dir / "final_summary.txt"
    if final_summary_file.exists():
        print(f"   ⏭️  Already processed, skipping")
        return True
    
    # Parse SRT file
    print(f"   📝 Parsing transcript...")
    subtitles = parse_srt_file(preferred_srt)
    
    if not subtitles:
        print(f"   ❌ Failed to parse SRT file")
        return False
    
    # Create 5-minute chunks
    print(f"   ✂️  Creating 5-minute chunks...")
    chunks = create_5min_chunks(subtitles)
    print(f"   📊 Created {len(chunks)} chunks")
    
    # Save chunks
    save_chunks(chunks, chunks_dir)
    print(f"   💾 Saved chunks to {chunks_dir}")
    
    # Process each chunk with LLM
    chunk_summaries_dir.mkdir(exist_ok=True)
    chunk_summaries = []
    
    print(f"   🤖 Processing {len(chunks)} chunks with LLM...")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"   📝 Processing chunk {i}/{len(chunks)} ({len(chunk['text'])} chars)...")
        
        summary_file = chunk_summaries_dir / f"summary_{chunk['chunk_number']:03d}.txt"
        
        # Skip if already processed
        if summary_file.exists():
            print(f"      ⏭️  Summary already exists, loading from file")
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = f.read()
        else:
            # Call LLM for chunk summary
            summary = call_llm_api(chunk['text'], "chunk")
            
            if summary:
                # Save chunk summary
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                print(f"      ✅ Summary saved ({len(summary)} chars)")
            else:
                print(f"      ❌ Failed to get summary for chunk {chunk['chunk_number']}")
                continue
        
        chunk_summaries.append({
            'chunk_number': chunk['chunk_number'],
            'summary': summary
        })
    
    print(f"   📋 Generated {len(chunk_summaries)} chunk summaries")
    
    # Create final summary
    content_summary_dir.mkdir(exist_ok=True)
    
    # Combine all chunk summaries
    combined_summaries = "\n\n".join([
        f"Chunk {cs['chunk_number']}:\n{cs['summary']}" 
        for cs in chunk_summaries
    ])
    
    print(f"   🎯 Creating final summary...")
    final_summary = call_llm_api(combined_summaries, "final")
    
    if final_summary:
        # Save final summary
        with open(final_summary_file, 'w', encoding='utf-8') as f:
            f.write(final_summary)
        
        # Also save metadata
        metadata_file = content_summary_dir / "summary_metadata.json"
        metadata = {
            'video_folder': video_folder.name,
            'srt_file_used': preferred_srt.name,
            'total_chunks': len(chunks),
            'processed_chunks': len(chunk_summaries),
            'processing_date': datetime.now().isoformat(),
            'preferred_language': preferred_language
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Final summary saved to {final_summary_file}")
        return True
    else:
        print(f"   ❌ Failed to generate final summary")
        return False

def process_channel(config: Dict) -> bool:
    """Process a single channel for summarization."""
    channel_name = config['channel_name']
    output_directory = config.get('output_directory', f"downloads/{channel_name}")
    
    print(f"\n📺 Processing channel: {channel_name}")
    print(f"   📁 Directory: {output_directory}")
    
    channel_dir = Path(output_directory)
    if not channel_dir.exists():
        print(f"   ❌ Channel directory not found: {channel_dir}")
        return False
    
    # Find all video subfolders
    video_folders = [d for d in channel_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    if not video_folders:
        print(f"   ⚠️  No video folders found")
        return False
    
    print(f"   📊 Found {len(video_folders)} video folders")
    
    # Process each video folder
    processed_count = 0
    failed_count = 0
    
    for video_folder in video_folders:
        try:
            if process_video_folder(video_folder):
                processed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"   ❌ Error processing {video_folder.name}: {e}")
            failed_count += 1
    
    print(f"\n   📊 Channel Summary:")
    print(f"      ✅ Processed: {processed_count}")
    print(f"      ❌ Failed: {failed_count}")
    print(f"      📁 Total folders: {len(video_folders)}")
    
    return processed_count > 0

def main():
    """Main function to process channels with summarize=yes."""
    parser = argparse.ArgumentParser(description='Summarize content for channels with summarize=yes')
    parser.add_argument('--config', required=True, help='Configuration file path')
    parser.add_argument('--language', default='pl', help='Preferred transcript language (default: pl)')
    parser.add_argument('--channels', help='Comma-separated list of specific channels to process')
    parser.add_argument('--llm-config', help='LLM configuration file path (default: llm_config.json)')
    
    args = parser.parse_args()
    
    # Load LLM configuration
    llm_config_path = Path(args.llm_config) if args.llm_config else None
    llm_config = load_llm_config(llm_config_path)
    
    print(f"🤖 LLM Configuration loaded:")
    print(f"   Server: {llm_config['server_url']}")
    print(f"   Model: {llm_config['model_name']}")
    print(f"   Temperature: {llm_config['temperature']}")
    print(f"   Context Length: {llm_config['context_length']}")
    
    # Test LLM connection
    print(f"\n🔗 Testing LLM server connection...")
    test_llm_connection()
    
    # Load configuration
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            channels = json.load(f)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)
    
    # Filter channels with summarize=yes
    channels_to_summarize = [
        channel for channel in channels 
        if channel.get('summarize', 'no') == 'yes'
    ]
    
    if not channels_to_summarize:
        print("ℹ️  No channels found with summarize='yes'")
        print("   To enable summarization, set 'summarize': 'yes' in your configuration file")
        return
    
    # Filter by specific channels if requested
    if args.channels:
        requested_channels = [name.strip() for name in args.channels.split(',')]
        channels_to_summarize = [
            channel for channel in channels_to_summarize
            if channel['channel_name'] in requested_channels
        ]
        
        if not channels_to_summarize:
            print(f"❌ No channels found matching: {args.channels}")
            return
    
    print(f"🚀 Content Summarization Starting...")
    print(f"📋 Found {len(channels_to_summarize)} channels to process")
    print(f"🌐 Preferred language: {args.language}")
    print("=" * 60)
    
    # Process each channel
    successful_channels = 0
    failed_channels = 0
    
    for channel in channels_to_summarize:
        try:
            if process_channel(channel):
                successful_channels += 1
            else:
                failed_channels += 1
        except Exception as e:
            print(f"❌ Error processing channel {channel['channel_name']}: {e}")
            failed_channels += 1
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 SUMMARIZATION COMPLETE")
    print("=" * 60)
    print(f"✅ Successful channels: {successful_channels}")
    print(f"❌ Failed channels: {failed_channels}")
    print(f"📁 Total channels processed: {len(channels_to_summarize)}")
    
    if successful_channels > 0:
        print("\n💡 Summary files created in:")
        print("   📁 chunks/ - 5-minute transcript segments")
        print("   📋 chunk_summaries/ - Individual chunk summaries")
        print("   🎯 content_summary/ - Final video summaries")
    
    print("\n🎉 Processing completed!")

if __name__ == "__main__":
    main()
