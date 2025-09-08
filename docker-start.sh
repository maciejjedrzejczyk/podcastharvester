#!/bin/bash

# PodcastHarvester Docker Startup Script

echo "🐳 PodcastHarvester Docker Management"
echo "====================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "Modes:"
    echo "  ui          Start web UI (default)"
    echo "  download    Run content harvesting"
    echo "  summarize   Generate AI summaries"
    echo "  complete    Start UI + LLM server"
    echo "  build       Build Docker images only"
    echo "  clean       Clean up containers and images"
    echo ""
    echo "Options:"
    echo "  --selective    Process specific channels only"
    echo "  --production   Use production configuration with Nginx"
    echo "  --rebuild      Force rebuild of images"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 ui                    # Start web UI"
    echo "  $0 download --selective  # Download specific channels"
    echo "  $0 summarize             # Generate summaries"
    echo "  $0 complete              # Start UI + LLM server"
}

# Parse arguments
MODE="ui"
SELECTIVE=""
PRODUCTION=""
REBUILD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        ui|download|summarize|complete|build|clean)
            MODE="$1"
            shift
            ;;
        --selective)
            SELECTIVE="--profile selective"
            shift
            ;;
        --production)
            PRODUCTION="--profile production"
            shift
            ;;
        --rebuild)
            REBUILD="--build --force-recreate"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check for required configuration files
if [[ "$MODE" != "clean" && "$MODE" != "build" ]]; then
    if [[ ! -f "channels_config.json" ]]; then
        echo "⚠️  channels_config.json not found. Creating from example..."
        if [[ -f "channels_config.example.json" ]]; then
            cp channels_config.example.json channels_config.json
            echo "✅ Created channels_config.json from example"
            echo "   Please edit this file with your desired channels"
        else
            echo "❌ channels_config.example.json not found"
            exit 1
        fi
    fi

    if [[ ! -f "llm_config.json" && ("$MODE" == "summarize" || "$MODE" == "complete") ]]; then
        echo "⚠️  llm_config.json not found. Creating from example..."
        if [[ -f "llm_config.example.json" ]]; then
            cp llm_config.example.json llm_config.json
            echo "✅ Created llm_config.json from example"
            echo "   Please edit this file with your LLM server details"
        else
            echo "❌ llm_config.example.json not found"
            exit 1
        fi
    fi
fi

# Execute based on mode
case $MODE in
    ui)
        echo "🌐 Starting PodcastHarvester Web UI..."
        docker-compose up $REBUILD $PRODUCTION
        ;;
    download)
        echo "📥 Starting content harvesting..."
        docker-compose -f docker-compose.download.yml up $REBUILD $SELECTIVE
        ;;
    summarize)
        echo "🤖 Starting AI summarization..."
        docker-compose -f docker-compose.summary.yml up $REBUILD $SELECTIVE
        ;;
    complete)
        echo "🚀 Starting complete stack (UI + LLM)..."
        docker-compose --profile llm up $REBUILD
        ;;
    build)
        echo "🔨 Building Docker images..."
        docker-compose build
        ;;
    clean)
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down --remove-orphans
        docker-compose -f docker-compose.download.yml down --remove-orphans
        docker-compose -f docker-compose.summary.yml down --remove-orphans
        docker-compose -f docker-compose.ui.yml down --remove-orphans
        echo "   Removing unused images..."
        docker image prune -f
        echo "✅ Cleanup complete"
        ;;
    *)
        echo "❌ Unknown mode: $MODE"
        show_usage
        exit 1
        ;;
esac
