#!/bin/bash

# PodcastHarvester Web Application Startup Script

echo "🚀 Starting PodcastHarvester Web Application..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3 and try again."
    exit 1
fi

# Check if downloads directory exists
if [ ! -d "downloads" ]; then
    echo "❌ Downloads directory not found."
    echo "   Please ensure you're running this script from the correct directory."
    echo "   Expected directory structure:"
    echo "   - downloads/"
    echo "   - content_server.py"
    echo "   - content_viewer.html"
    exit 1
fi

# Default settings
HOST="localhost"
PORT="8080"
DOWNLOADS_DIR="downloads"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --downloads-dir)
            DOWNLOADS_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --host HOST           Server host (default: localhost)"
            echo "  --port PORT           Server port (default: 8080)"
            echo "  --downloads-dir DIR   Downloads directory path (default: downloads)"
            echo "  --help                Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Start with default settings"
            echo "  $0 --port 9000                       # Start on port 9000"
            echo "  $0 --host 0.0.0.0 --port 8080       # Allow external connections"
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "   Use --help for usage information."
            exit 1
            ;;
    esac
done

echo "📋 Configuration:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Downloads Directory: $DOWNLOADS_DIR"
echo ""

# Start the server
echo "🌐 Starting server..."
echo "   Open http://$HOST:$PORT in your browser"
echo "   Press Ctrl+C to stop the server"
echo ""

python3 content_server.py --host "$HOST" --port "$PORT" --downloads-dir "$DOWNLOADS_DIR"
