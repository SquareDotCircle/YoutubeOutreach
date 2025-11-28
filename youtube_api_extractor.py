#!/usr/bin/env python3
"""
YouTube Data API v3 Integration (Optional)
Alternative to yt-dlp for faster, more reliable data extraction

Setup:
1. Get API key from https://console.cloud.google.com/apis/credentials
2. Enable YouTube Data API v3
3. Set YOUTUBE_API_KEY environment variable or pass directly

Quota Cost:
- Search: 100 units per query
- Channel details: 1 unit per channel
- Video details: 1 unit per video
- Daily quota: 10,000 units (free tier)
- Cost after quota: ~$0.70 per 10,000 requests

When to Use:
- High volume processing (faster than yt-dlp)
- Need 100% reliability
- Rate limiting issues with yt-dlp
- Want official API support
"""

import os
import requests
from typing import Dict, List, Optional

# Get API key from environment or pass directly
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
YOUTUBE_API_BASE = 'https://www.googleapis.com/youtube/v3'

def check_api_available() -> bool:
    """Check if YouTube API key is configured and valid"""
    if not YOUTUBE_API_KEY:
        return False
    
    try:
        url = f"{YOUTUBE_API_BASE}/search"
        params = {
            'part': 'snippet',
            'maxResults': 1,
            'q': 'test',
            'type': 'channel',
            'key': YOUTUBE_API_KEY
        }
        response = requests.get(url, params=params, timeout=5)
        return response.status_code == 200
    except:
        return False

def search_channels_api(query: str, max_results: int = 10) -> List[str]:
    """
    Search for channels using YouTube API
    
    Quota Cost: 100 units per search
    """
    try:
        url = f"{YOUTUBE_API_BASE}/search"
        params = {
            'part': 'snippet',
            'maxResults': max_results,
            'q': query,
            'type': 'video',
            'key': YOUTUBE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return [f"https://youtube.com/watch?v={item['id']['videoId']}" 
                   for item in data.get('items', [])]
    except Exception as e:
        print(f"YouTube API search error: {e}")
    
    return []

def get_channel_details_api(channel_id: str) -> Optional[Dict]:
    """
    Get detailed channel information using YouTube API
    
    Quota Cost: 1 unit
    """
    try:
        url = f"{YOUTUBE_API_BASE}/channels"
        params = {
            'part': 'snippet,statistics,contentDetails,brandingSettings',
            'id': channel_id,
            'key': YOUTUBE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                item = data['items'][0]
                snippet = item.get('snippet', {})
                stats = item.get('statistics', {})
                branding = item.get('brandingSettings', {}).get('channel', {})
                
                return {
                    'channel_id': channel_id,
                    'channel_name': snippet.get('title', ''),
                    'channel_description': snippet.get('description', ''),
                    'channel_custom_url': snippet.get('customUrl', ''),
                    'channel_country': snippet.get('country', ''),
                    'channel_join_date': snippet.get('publishedAt', ''),
                    'subscriber_count': int(stats.get('subscriberCount', 0)),
                    'total_view_count': int(stats.get('viewCount', 0)),
                    'total_video_count': int(stats.get('videoCount', 0)),
                    'channel_url': f"https://youtube.com/channel/{channel_id}",
                    
                    # Additional branding data
                    'keywords': branding.get('keywords', ''),
                }
    except Exception as e:
        print(f"YouTube API channel details error: {e}")
    
    return None

def get_recent_videos_api(channel_id: str, max_results: int = 10) -> List[Dict]:
    """
    Get recent videos from a channel using YouTube API
    
    Quota Cost: 1 unit + (1 unit × max_results for video details)
    """
    try:
        # Get uploads playlist ID
        url = f"{YOUTUBE_API_BASE}/channels"
        params = {
            'part': 'contentDetails',
            'id': channel_id,
            'key': YOUTUBE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        if not data.get('items'):
            return []
        
        uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get videos from uploads playlist
        url = f"{YOUTUBE_API_BASE}/playlistItems"
        params = {
            'part': 'contentDetails',
            'playlistId': uploads_playlist_id,
            'maxResults': max_results,
            'key': YOUTUBE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        video_ids = [item['contentDetails']['videoId'] for item in data.get('items', [])]
        
        # Get video statistics
        if video_ids:
            return get_video_details_batch_api(video_ids)
    
    except Exception as e:
        print(f"YouTube API recent videos error: {e}")
    
    return []

def get_video_details_batch_api(video_ids: List[str]) -> List[Dict]:
    """
    Get detailed stats for multiple videos (batch request)
    
    Quota Cost: 1 unit per 50 videos (very efficient!)
    """
    try:
        url = f"{YOUTUBE_API_BASE}/videos"
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': ','.join(video_ids[:50]),  # API allows up to 50 IDs
            'key': YOUTUBE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                stats = item.get('statistics', {})
                content = item.get('contentDetails', {})
                
                # Parse duration (PT15M30S format)
                duration_str = content.get('duration', 'PT0S')
                duration_seconds = parse_duration(duration_str)
                
                videos.append({
                    'video_id': item['id'],
                    'title': snippet.get('title', ''),
                    'upload_date': snippet.get('publishedAt', ''),
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0)),
                    'duration': duration_seconds,
                })
            
            return videos
    except Exception as e:
        print(f"YouTube API video details error: {e}")
    
    return []

def parse_duration(duration_str: str) -> int:
    """Parse ISO 8601 duration to seconds (PT15M30S → 930)"""
    import re
    
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def get_enhanced_channel_data_api(channel_id: str) -> Optional[Dict]:
    """
    Get complete enhanced channel data using YouTube API
    
    Total Quota Cost: ~12-15 units (very efficient)
    - Channel details: 1 unit
    - Recent videos list: 1 unit
    - Video details batch: 1 unit (for up to 50 videos)
    """
    if not check_api_available():
        print("⚠️ YouTube API not configured")
        return None
    
    print(f"    🔑 Using YouTube Data API (fast mode)")
    
    # Get channel details
    channel_data = get_channel_details_api(channel_id)
    if not channel_data:
        return None
    
    # Get recent videos with stats
    recent_videos = get_recent_videos_api(channel_id, max_results=10)
    
    if recent_videos:
        # Calculate engagement metrics (same as yt-dlp version)
        from enhanced_channel_extractor import calculate_engagement_metrics
        metrics = calculate_engagement_metrics(recent_videos)
        channel_data.update(metrics)
        
        # Calculate view rate
        if 'avg_views' in metrics and channel_data.get('subscriber_count', 0) > 0:
            view_rate = (metrics['avg_views'] / channel_data['subscriber_count']) * 100
            channel_data['view_rate'] = round(view_rate, 2)
        
        # Extract contact info from description
        description = channel_data.get('channel_description', '')
        
        from enhanced_channel_extractor import extract_email_from_text, extract_social_links
        
        email = extract_email_from_text(description)
        if email:
            channel_data['business_email'] = email
        
        social_links = extract_social_links(description)
        channel_data.update({
            'instagram_handle': social_links.get('instagram'),
            'twitter_handle': social_links.get('twitter'),
            'website_url': social_links.get('website'),
            'has_affiliate_store': 1 if social_links.get('has_store') else 0,
            'has_patreon': 1 if social_links.get('has_patreon') else 0,
        })
    
    return channel_data

# Configuration helper
def setup_youtube_api():
    """Interactive setup for YouTube API key"""
    print("🔑 YouTube Data API v3 Setup")
    print("=" * 60)
    print("\nSteps to get API key:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Create new project or select existing")
    print("3. Enable 'YouTube Data API v3'")
    print("4. Create credentials → API key")
    print("5. Copy the API key")
    print("\nDaily quota: 10,000 units (free)")
    print("After quota: ~$0.70 per 10,000 requests")
    print("\n" + "=" * 60)
    
    api_key = input("\nEnter your YouTube API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Save to environment variable for current session
        os.environ['YOUTUBE_API_KEY'] = api_key
        
        # Test it
        if check_api_available():
            print("\n✓ API key is valid!")
            print("\nTo make permanent, add to your shell profile:")
            print(f'export YOUTUBE_API_KEY="{api_key}"')
            return True
        else:
            print("\n✗ API key is invalid or API not enabled")
            return False
    else:
        print("\n⏭️ Skipping YouTube API (will use yt-dlp instead)")
        return False

if __name__ == "__main__":
    # Run setup if executed directly
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup_youtube_api()

