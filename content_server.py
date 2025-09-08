#!/usr/bin/env python3
"""
Content Server for PodcastHarvester Web Application

This server provides API endpoints for:
1. Scanning downloads directory for harvested content
2. Serving media files
3. Handling delete operations (media only or entire folder)
4. Reading summary metadata and content
"""

import json
import os
import shutil
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, List, Optional
import mimetypes

class ContentScanner:
    """Separate class for scanning content without HTTP request context."""
    
    def __init__(self, downloads_dir: Path):
        self.downloads_dir = downloads_dir
    
    def scan_downloads_directory(self) -> List[Dict]:
        """Scan the downloads directory and return content information."""
        content_list = []
        
        if not self.downloads_dir.exists():
            return content_list
        
        # Iterate through channel directories
        for channel_dir in self.downloads_dir.iterdir():
            if not channel_dir.is_dir() or channel_dir.name.startswith('.'):
                continue
            
            channel_name = channel_dir.name
            
            # Iterate through video folders in each channel
            for video_dir in channel_dir.iterdir():
                if not video_dir.is_dir() or video_dir.name.startswith('.'):
                    continue
                
                content_info = self.analyze_video_folder(video_dir, channel_name)
                if content_info:
                    content_list.append(content_info)
        
        # Sort by upload date (newest first), handling None values
        content_list.sort(key=lambda x: x.get('uploadDate') or '0000-00-00', reverse=True)
        return content_list

    def analyze_video_folder(self, video_dir: Path, channel_name: str) -> Optional[Dict]:
        """Analyze a single video folder and extract information."""
        try:
            content_info = {
                'path': f"{channel_name}/{video_dir.name}",
                'title': video_dir.name,
                'channel': channel_name,
                'hasSummary': False,
                'audioFile': None,
                'videoFile': None,
                'uploadDate': None,
                'duration': None,
                'summary': None,
                'totalChunks': 0,
                'processedChunks': 0,
                'preferredLanguage': None
            }
            
            # Check for summary files
            content_summary_dir = video_dir / "content_summary"
            if content_summary_dir.exists():
                content_info.update(self.read_summary_info(content_summary_dir))
            
            # Find media files
            media_extensions = {
                'audio': ['.mp3', '.m4a', '.aac'],
                'video': ['.mp4', '.webm', '.mkv', '.avi', '.mov']
            }
            
            for file_path in video_dir.iterdir():
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    
                    # Check for audio files
                    if ext in media_extensions['audio']:
                        content_info['audioFile'] = file_path.name
                    
                    # Check for video files
                    elif ext in media_extensions['video']:
                        content_info['videoFile'] = file_path.name
                    
                    # Check for info.json metadata
                    elif file_path.name.endswith('.info.json'):
                        metadata = self.read_metadata(file_path)
                        if metadata:
                            content_info.update(metadata)
            
            # Extract title from folder name if not found in metadata
            if content_info['title'] == video_dir.name:
                # Try to extract a cleaner title from the folder name
                title_parts = video_dir.name.split('_')
                if len(title_parts) > 3:  # Assuming format: date_channel_title...
                    content_info['title'] = ' '.join(title_parts[2:]).replace('_', ' ')
            
            return content_info
            
        except Exception as e:
            print(f"Error analyzing folder {video_dir}: {e}")
            return None

    def read_summary_info(self, content_summary_dir: Path) -> Dict:
        """Read summary information from content_summary directory."""
        summary_info = {
            'hasSummary': True,
            'summary': 'Summary available but could not be loaded.',
            'totalChunks': 0,
            'processedChunks': 0,
            'preferredLanguage': None
        }
        
        try:
            # Read final summary
            final_summary_file = content_summary_dir / "final_summary.txt"
            if final_summary_file.exists():
                with open(final_summary_file, 'r', encoding='utf-8') as f:
                    summary_info['summary'] = f.read().strip()
            
            # Read metadata
            metadata_file = content_summary_dir / "summary_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    summary_info['totalChunks'] = metadata.get('total_chunks', 0)
                    summary_info['processedChunks'] = metadata.get('processed_chunks', 0)
                    summary_info['preferredLanguage'] = metadata.get('preferred_language', 'Unknown')
            
        except Exception as e:
            print(f"Error reading summary info: {e}")
        
        return summary_info

    def read_metadata(self, info_file: Path) -> Dict:
        """Read metadata from .info.json file."""
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Ensure uploadDate is never None
            upload_date = metadata.get('upload_date', '') or ''
            
            return {
                'title': metadata.get('title', ''),
                'uploadDate': upload_date,
                'duration': metadata.get('duration', 0),
                'uploader': metadata.get('uploader', ''),
                'description': metadata.get('description', '')
            }
        except Exception as e:
            print(f"Error reading metadata from {info_file}: {e}")
            return {}

class ContentHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.downloads_dir = Path("downloads")  # Default value
        super().__init__(*args, **kwargs)

    def is_connection_alive(self):
        """Check if the client connection is still alive."""
        try:
            # Try to get the socket peer name
            self.connection.getpeername()
            return True
        except (OSError, AttributeError):
            return False

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.serve_html()
        elif self.path == '/api/content':
            self.serve_content_api()
        elif self.path == '/api/llm-config':
            self.serve_llm_config()
        elif self.path == '/api/channels-config':
            self.serve_channels_config()
        elif self.path.startswith('/media/'):
            self.serve_media_file()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/delete-media':
            self.handle_delete_media()
        elif self.path == '/api/delete-folder':
            self.handle_delete_folder()
        elif self.path == '/api/save-llm-config':
            self.handle_save_llm_config()
        elif self.path == '/api/save-channels-config':
            self.handle_save_channels_config()
        elif self.path == '/api/add-channel':
            self.handle_add_channel()
        elif self.path == '/api/process-url':
            self.handle_process_url()
        elif self.path == '/api/run-download':
            self.handle_run_download()
        elif self.path == '/api/run-summarization':
            self.handle_run_summarization()
        elif self.path == '/api/get-channels':
            self.handle_get_channels()
        else:
            self.send_error(404, "Not Found")

    def serve_html(self):
        """Serve the main HTML file."""
        try:
            html_path = Path(__file__).parent / "content_viewer.html"
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Error serving HTML: {e}")

    def serve_content_api(self):
        """Serve the content API with all discovered content."""
        try:
            scanner = ContentScanner(self.downloads_dir)
            content_data = scanner.scan_downloads_directory()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            json_data = json.dumps(content_data, ensure_ascii=False, indent=2)
            self.wfile.write(json_data.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Error scanning content: {e}")

    def serve_media_file(self):
        """Serve media files for playback."""
        try:
            # Parse the media path: /media/channel/video_folder/filename
            path_parts = urllib.parse.unquote(self.path[7:]).split('/')  # Remove '/media/'
            
            if len(path_parts) < 3:
                self.send_error(400, "Invalid media path")
                return
            
            # Reconstruct the file path
            file_path = self.downloads_dir
            for part in path_parts:
                file_path = file_path / part
            
            if not file_path.exists() or not file_path.is_file():
                self.send_error(404, "Media file not found")
                return
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if not content_type:
                if file_path.suffix.lower() in ['.mp3', '.m4a', '.aac']:
                    content_type = 'audio/mpeg'
                elif file_path.suffix.lower() in ['.mp4', '.webm', '.mkv']:
                    content_type = 'video/mp4'
                else:
                    content_type = 'application/octet-stream'
            
            # Get file size for range requests
            file_size = file_path.stat().st_size
            
            # Handle range requests for media streaming
            range_header = self.headers.get('Range')
            if range_header:
                self.handle_range_request(file_path, file_size, content_type, range_header)
            else:
                # Serve entire file
                try:
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    self.send_header('Content-length', str(file_size))
                    self.send_header('Accept-Ranges', 'bytes')
                    self.end_headers()
                    
                    with open(file_path, 'rb') as f:
                        while self.is_connection_alive():
                            chunk = f.read(8192)
                            if not chunk:
                                break
                            try:
                                self.wfile.write(chunk)
                            except (BrokenPipeError, ConnectionResetError):
                                # Client disconnected - this is normal
                                break
                except (BrokenPipeError, ConnectionResetError):
                    # Client disconnected - this is normal for media streaming
                    pass
                    
        except (BrokenPipeError, ConnectionResetError):
            # Client disconnected - this is normal, don't log as error
            pass
        except Exception as e:
            # Only log unexpected errors, not broken pipes
            if not isinstance(e, (BrokenPipeError, ConnectionResetError)):
                print(f"Error serving media: {e}")
            # Don't try to send error response if connection is broken
            try:
                self.send_error(500, f"Error serving media: {e}")
            except (BrokenPipeError, ConnectionResetError):
                pass

    def handle_range_request(self, file_path: Path, file_size: int, content_type: str, range_header: str):
        """Handle HTTP range requests for media streaming."""
        try:
            # Parse range header: "bytes=start-end"
            range_match = range_header.replace('bytes=', '').split('-')
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else file_size - 1
            
            # Ensure valid range
            start = max(0, start)
            end = min(file_size - 1, end)
            content_length = end - start + 1
            
            self.send_response(206)  # Partial Content
            self.send_header('Content-type', content_type)
            self.send_header('Content-length', str(content_length))
            self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            
            # Send the requested range
            with open(file_path, 'rb') as f:
                f.seek(start)
                remaining = content_length
                while remaining > 0 and self.is_connection_alive():
                    chunk_size = min(8192, remaining)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        # Client disconnected - this is normal, just stop sending
                        break
                    
        except (BrokenPipeError, ConnectionResetError):
            # Client disconnected - this is normal for media streaming
            # Don't log as error, just return silently
            pass
        except Exception as e:
            # Only log unexpected errors, not broken pipes
            if not isinstance(e, (BrokenPipeError, ConnectionResetError)):
                print(f"Error handling range request: {e}")
            # Don't try to send error response if connection is broken
            try:
                self.send_error(500, f"Error handling range request: {e}")
            except (BrokenPipeError, ConnectionResetError):
                pass

    def handle_delete_media(self):
        """Handle media-only deletion."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            folder_path = self.downloads_dir / data['path']
            if not folder_path.exists():
                self.send_error(404, "Folder not found")
                return
            
            # Find and delete media files
            deleted_files = []
            media_extensions = ['.mp3', '.mp4', '.m4a', '.aac', '.webm', '.mkv', '.avi', '.mov']
            
            for file_path in folder_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in media_extensions:
                    file_path.unlink()
                    deleted_files.append(file_path.name)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'deleted_files': deleted_files,
                'message': f'Deleted {len(deleted_files)} media file(s)'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error deleting media: {e}")

    def handle_delete_folder(self):
        """Handle entire folder deletion."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            folder_path = self.downloads_dir / data['path']
            if not folder_path.exists():
                self.send_error(404, "Folder not found")
                return
            
            # Delete entire folder
            shutil.rmtree(folder_path)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'message': f'Deleted folder: {data["path"]}'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error deleting folder: {e}")

    def serve_llm_config(self):
        """Serve LLM configuration."""
        try:
            config_path = Path(__file__).parent / 'llm_config.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(config, indent=2).encode())
        except Exception as e:
            self.send_error(500, f"Error loading LLM config: {e}")

    def serve_channels_config(self):
        """Serve channels configuration."""
        try:
            config_path = Path(__file__).parent / 'channels_config_full.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = []
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(config, indent=2).encode())
        except Exception as e:
            self.send_error(500, f"Error loading channels config: {e}")

    def handle_save_llm_config(self):
        """Save LLM configuration."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            config = json.loads(post_data.decode('utf-8'))
            
            config_path = Path(__file__).parent / 'llm_config.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        except Exception as e:
            self.send_error(500, f"Error saving LLM config: {e}")

    def handle_save_channels_config(self):
        """Save channels configuration."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            config = json.loads(post_data.decode('utf-8'))
            
            config_path = Path(__file__).parent / 'channels_config_full.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        except Exception as e:
            self.send_error(500, f"Error saving channels config: {e}")

    def handle_add_channel(self):
        """Add a new channel to the configuration."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            new_channel = json.loads(post_data.decode('utf-8'))
            
            config_path = Path(__file__).parent / 'channels_config_full.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = []
            
            config.append(new_channel)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        except Exception as e:
            self.send_error(500, f"Error adding channel: {e}")

    def handle_process_url(self):
        """Process a single YouTube URL."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            url = data.get('url')
            content_type = data.get('content_type', 'audio')
            download_transcript = data.get('download_transcript', 'yes') == 'yes'
            generate_summary = data.get('generate_summary', 'yes') == 'yes'
            
            if not url:
                self.send_error(400, "URL is required")
                return
            
            # Create temporary directory for this URL
            import tempfile
            import subprocess
            import threading
            from urllib.parse import parse_qs, urlparse
            
            def process_video():
                try:
                    # Extract video ID for naming
                    parsed_url = urlparse(url)
                    video_id = parse_qs(parsed_url.query).get('v', ['unknown'])[0]
                    
                    # Create output directory
                    output_dir = Path(__file__).parent / 'downloads' / 'AdHoc_URLs' / video_id
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Build yt-dlp command
                    format_selector = 'bestaudio[ext=mp3]/bestaudio/best' if content_type == 'audio' else 'best'
                    cmd = [
                        'yt-dlp',
                        '--format', format_selector,
                        '--output', str(output_dir / '%(upload_date)s_%(uploader)s_%(title)s.%(ext)s'),
                        '--write-info-json',
                        '--write-description',
                        '--write-thumbnail'
                    ]
                    
                    if download_transcript:
                        cmd.extend([
                            '--write-subs', 
                            '--sub-langs', 'en,pl',
                            '--convert-subs', 'srt'
                        ])
                    
                    cmd.append(url)
                    
                    # Run download
                    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
                    print(f"URL processing completed with return code: {result.returncode}")
                    
                    if result.returncode == 0 and generate_summary:
                        # Create a temporary config for this single video
                        temp_config = [{
                            "url": url,
                            "channel_name": "AdHoc_URLs",
                            "content_type": content_type,
                            "cutoff_date": "2020-01-01",
                            "output_format": "%(upload_date)s_%(uploader)s_%(title)s",
                            "output_directory": "downloads/AdHoc_URLs",
                            "transcript_languages": ["en"],
                            "redownload_deleted": False,
                            "summarize": "yes"
                        }]
                        
                        temp_config_path = Path(__file__).parent / 'temp_adhoc_config.json'
                        with open(temp_config_path, 'w') as f:
                            json.dump(temp_config, f, indent=2)
                        
                        # Run summarization with the temp config
                        summary_cmd = [
                            'python3', 'content_summarizer.py',
                            '--config', 'temp_adhoc_config.json',
                            '--channels', 'AdHoc_URLs'
                        ]
                        subprocess.run(summary_cmd, cwd=str(Path(__file__).parent))
                        
                        # Clean up temp config
                        temp_config_path.unlink(missing_ok=True)
                        
                except Exception as e:
                    print(f"Error processing URL: {e}")
            
            # Start processing in background
            thread = threading.Thread(target=process_video)
            thread.daemon = True
            thread.start()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'URL processing started'}).encode())
            
        except Exception as e:
            self.send_error(500, f"Error processing URL: {e}")

    def handle_get_channels(self):
        """Get available channels from configuration files."""
        try:
            channels = []
            config_files = ['channels_config_full.json', 'test_channels.json', 'channels_config.json']
            
            for config_file in config_files:
                config_path = Path(__file__).parent / config_file
                if config_path.exists():
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        
                        for channel in config_data:
                            if 'channel_name' in channel:
                                channels.append({
                                    'name': channel['channel_name'],
                                    'config_file': config_file,
                                    'summarize': channel.get('summarize', 'no')
                                })
                    except Exception as e:
                        print(f"Error reading {config_file}: {e}")
            
            # Remove duplicates
            unique_channels = []
            seen_names = set()
            for channel in channels:
                if channel['name'] not in seen_names:
                    unique_channels.append(channel)
                    seen_names.add(channel['name'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'channels': unique_channels}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error getting channels: {e}")

    def handle_run_download(self):
        """Handle download script execution."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            config_file = data.get('config_file', 'channels_config_full.json')
            channels = data.get('channels', '')
            max_channels = data.get('max_channels', '')
            
            # Build command
            script_path = Path(__file__).parent / 'podcast_harvester.py'
            cmd = ['python3', str(script_path), '--config', config_file]
            
            if channels:
                cmd.extend(['--channels', channels])
            if max_channels:
                cmd.extend(['--max-channels', str(max_channels)])
            
            # Execute script in background
            import subprocess
            import threading
            
            def run_script():
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
                    # Store result for later retrieval (in a real app, you'd use a proper job queue)
                    print(f"Download script completed with return code: {result.returncode}")
                    if result.stdout:
                        print(f"STDOUT: {result.stdout}")
                    if result.stderr:
                        print(f"STDERR: {result.stderr}")
                except Exception as e:
                    print(f"Error running download script: {e}")
            
            # Start script in background thread
            thread = threading.Thread(target=run_script)
            thread.daemon = True
            thread.start()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'message': 'Download script started successfully',
                'command': ' '.join(cmd)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error running download script: {e}")

    def handle_run_summarization(self):
        """Handle summarization script execution."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            config_file = data.get('config_file', 'channels_config_full.json')
            channels = data.get('channels', '')
            language = data.get('language', 'pl')
            
            # Build command
            script_path = Path(__file__).parent / 'content_summarizer.py'
            cmd = ['python3', str(script_path), '--config', config_file, '--language', language]
            
            if channels:
                cmd.extend(['--channels', channels])
            
            # Execute script in background
            import subprocess
            import threading
            
            def run_script():
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
                    # Store result for later retrieval (in a real app, you'd use a proper job queue)
                    print(f"Summarization script completed with return code: {result.returncode}")
                    if result.stdout:
                        print(f"STDOUT: {result.stdout}")
                    if result.stderr:
                        print(f"STDERR: {result.stderr}")
                except Exception as e:
                    print(f"Error running summarization script: {e}")
            
            # Start script in background thread
            thread = threading.Thread(target=run_script)
            thread.daemon = True
            thread.start()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'message': 'Summarization script started successfully',
                'command': ' '.join(cmd)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error running summarization script: {e}")

    def log_message(self, format, *args):
        """Override to customize logging and suppress broken pipe errors."""
        message = format % args
        
        # Don't log broken pipe errors as they're normal for media streaming
        if "Broken pipe" in message or "Connection reset" in message:
            return
            
        # Don't log successful range requests (206) as they're verbose
        if " 206 " in message:
            return
            
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def log_error(self, format, *args):
        """Override to suppress broken pipe errors."""
        message = format % args
        
        # Don't log broken pipe errors as they're normal for media streaming
        if "Broken pipe" in message or "Connection reset" in message:
            return
            
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {message}")

def create_handler_class(downloads_dir):
    """Create a handler class with the specified downloads directory."""
    class CustomHandler(ContentHandler):
        def __init__(self, *args, **kwargs):
            # Remove downloads_dir from kwargs if present to avoid conflict
            kwargs.pop('downloads_dir', None)
            super().__init__(*args, **kwargs)
            # Set the downloads_dir after initialization
            self.downloads_dir = Path(downloads_dir)
    return CustomHandler

def main():
    """Main function to start the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube Content Manager Server')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--downloads-dir', default='downloads', help='Downloads directory path')
    
    args = parser.parse_args()
    
    # Verify downloads directory exists
    downloads_path = Path(args.downloads_dir)
    if not downloads_path.exists():
        print(f"❌ Downloads directory not found: {downloads_path}")
        print(f"   Please ensure the directory exists or specify the correct path with --downloads-dir")
        return
    
    # Create server
    handler_class = create_handler_class(downloads_path)
    server = HTTPServer((args.host, args.port), handler_class)
    
    print(f"🚀 YouTube Content Manager Server Starting...")
    print(f"   📁 Downloads directory: {downloads_path.absolute()}")
    print(f"   🌐 Server URL: http://{args.host}:{args.port}")
    print(f"   📊 Scanning for content...")
    
    # Quick scan to show initial stats
    scanner = ContentScanner(downloads_path)
    content_count = len(scanner.scan_downloads_directory())
    print(f"   ✅ Found {content_count} content items")
    
    print(f"\n🎉 Server ready! Open http://{args.host}:{args.port} in your browser")
    print(f"   Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
        server.shutdown()

if __name__ == "__main__":
    main()
