#!/usr/bin/env python3
"""
Configuration file for optional features
"""

import os
from pathlib import Path

# Load .env file if it exists
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# YouTube Data API v3 (Optional - disabled, using yt-dlp instead)
YOUTUBE_API_KEY = ''
USE_YOUTUBE_API = False

# Claude API (Required)
ANTHROPIC_API_KEY = 'YOUR_CLAUDE_API_KEY_HERE'  # <-- Paste your key here

# Enhanced data extraction settings
EXTRACT_ENHANCED_METRICS = True  # Enable Tier 1 metrics (avg views, engagement, etc.)
ENHANCED_VIDEO_SAMPLE_SIZE = 10  # Number of recent videos to analyze

# Pre-filter settings
ENABLE_PREFILTER = True
MIN_DESCRIPTION_LENGTH = 50  # Channels with shorter descriptions are filtered
NON_ASCII_THRESHOLD = 0.3  # For foreign language detection

# Session settings
ENABLE_SESSION_DEDUPLICATION = True

# Database settings
DATABASE_FILE = 'youtube_channels.db'

# Display settings
DISPLAY_MODE = 'enhanced'  # 'basic' or 'enhanced'

def print_config():
    """Print current configuration"""
    print("⚙️ System Configuration")
    print("=" * 60)
    print(f"YouTube API: {'✓ Enabled' if USE_YOUTUBE_API else '✗ Disabled (using yt-dlp)'}")
    print(f"Claude API: {'✓ Configured' if ANTHROPIC_API_KEY else '✗ Not configured'}")
    print(f"Enhanced Metrics: {'✓ Enabled' if EXTRACT_ENHANCED_METRICS else '✗ Disabled'}")
    print(f"Pre-filtering: {'✓ Enabled' if ENABLE_PREFILTER else '✗ Disabled'}")
    print(f"Session Dedup: {'✓ Enabled' if ENABLE_SESSION_DEDUPLICATION else '✗ Disabled'}")
    print(f"Database: {DATABASE_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    print_config()

