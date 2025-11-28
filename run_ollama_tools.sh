#!/bin/bash
# Quick runner for Ollama tools

cd /Users/jordanrogan/YoutubeChannels

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "⚠️ Virtual environment not found!"
    echo "   Run: ./setup_ollama_env.sh first"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Show menu
echo "🤖 Ollama Tools"
echo "==============="
echo ""
echo "What would you like to do?"
echo ""
echo "1) Generate 30 new search terms (AI-powered)"
echo "2) Analyze 10 channels for relevance"
echo "3) Analyze 20 channels"
echo "4) Analyze all channels in target range"
echo "5) Both: Generate terms + Analyze channels"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🎯 Generating search terms..."
        python ollama_search_generator.py
        ;;
    2)
        echo ""
        echo "🔍 Analyzing 10 channels..."
        python ollama_channel_analyzer.py 10
        ;;
    3)
        echo ""
        echo "🔍 Analyzing 20 channels..."
        python ollama_channel_analyzer.py 20
        ;;
    4)
        echo ""
        echo "🔍 Analyzing all channels in target range..."
        python ollama_channel_analyzer.py 100
        ;;
    5)
        echo ""
        echo "🎯 Generating search terms..."
        python ollama_search_generator.py
        echo ""
        echo "🔍 Analyzing 10 channels..."
        python ollama_channel_analyzer.py 10
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
echo ""
echo "📄 Check the output files:"
echo "   - ollama_generated_terms.txt"
echo "   - channel_analysis_report.md"
echo ""
echo "🌐 To view channels: open channels_viewer.html"

