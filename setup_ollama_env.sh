#!/bin/bash
# Setup script for Ollama environment

echo "🔧 Setting up Ollama environment..."
echo "=================================="

cd /Users/jordanrogan/YoutubeChannels

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing required packages..."
pip install --quiet requests

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To use the Ollama tools:"
echo "   source venv/bin/activate"
echo "   python ollama_search_generator.py"
echo "   python ollama_channel_analyzer.py 10"
echo ""
echo "📝 Or just run: ./run_ollama_tools.sh"
echo ""

