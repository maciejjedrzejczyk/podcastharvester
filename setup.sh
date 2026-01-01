#!/bin/bash

echo "Setting up PodcastHarvester..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install yt-dlp
fi

# Make scripts executable
chmod +x podcast_harvester.py content_server.py content_summarizer.py
chmod +x rss_generator.py start_web_app.sh

# Copy example configurations
echo "Setting up example configurations..."
if [ ! -f "channels_config.json" ]; then
    cp config/channels_config.example.json channels_config.json
    echo "Created channels_config.json from example"
fi

if [ ! -f "llm_config.json" ]; then
    cp config/llm_config.example.json llm_config.json
    echo "Created llm_config.json from example"
fi

if [ ! -f "notification_config.json" ]; then
    cp config/notification_config.example.json notification_config.json
    echo "Created notification_config.json from example"
fi

# Create activation script
cat > activate_env.sh << 'EOF'
#!/bin/bash
echo "Activating PodcastHarvester environment..."
source venv/bin/activate
echo "Environment activated. You can now run:"
echo "  python3 podcast_harvester.py --config channels_config.json"
echo "  ./start_web_app.sh"
echo ""
echo "To deactivate the environment, run: deactivate"
EOF

chmod +x activate_env.sh

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit channels_config.json with your YouTube channels"
echo "2. Start the web interface: ./start_web_app.sh"
echo "3. Or run batch processing: python3 podcast_harvester.py --config channels_config.json"
echo ""
echo "For AI summarization, configure llm_config.json with your LLM server details."
echo ""
echo "Documentation: See docs/ directory for detailed guides"
