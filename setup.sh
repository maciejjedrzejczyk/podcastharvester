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

# Make the script executable
chmod +x podcast_harvester.py

# Create activation script
cat > activate_env.sh << 'EOF'
#!/bin/bash
echo "Activating PodcastHarvester environment..."
source venv/bin/activate
echo "Environment activated. You can now run:"
echo "  ./podcast_harvester.py"
echo ""
echo "To deactivate the environment, run: deactivate"
EOF

chmod +x activate_env.sh

echo ""
echo "Setup complete!"
echo ""
echo "IMPORTANT: To use PodcastHarvester, you need to activate the virtual environment first:"
echo "  source venv/bin/activate"
echo "  OR"
echo "  ./activate_env.sh"
echo ""
echo "Then you can run:"
echo "  Interactive mode:    ./podcast_harvester.py"
echo "  Non-interactive:     ./podcast_harvester.py --url <URL> --cutoff <DATE>"
echo ""
echo "Example:"
echo "  ./podcast_harvester.py --url 'https://www.youtube.com/@channelname' --format 'best' --cutoff '2023-01-01'"
echo ""
echo "To deactivate the environment when done: deactivate"
