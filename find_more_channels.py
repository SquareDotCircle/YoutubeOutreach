#!/usr/bin/env python3
"""
YouTube Channel Finder - Discover more prepper/survival channels
Searches YouTube for relevant content and extracts channel information
"""

import subprocess
import json
from typing import List, Dict

# Search terms relevant to your product
SEARCH_TERMS = [
    "prepper grid down",
    "survival knowledge",
    "off grid living",
    "SHTF preparation",
    "collapse survival",
    "emergency preparedness tutorial",
    "homesteading self reliance",
    "survival library",
    "prepper checklist 2025",
    "90 day blackout survival"
]

def search_youtube(query: str, max_results: int = 10) -> List[str]:
    """Search YouTube and return video URLs"""
    print(f"Searching for: {query}")
    
    try:
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--get-id",
            "--flat-playlist",
            f"ytsearch{max_results}:{query}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        video_ids = result.stdout.strip().split('\n')
        
        urls = [f"https://www.youtube.com/watch?v={vid_id}" for vid_id in video_ids if vid_id]
        return urls
        
    except subprocess.CalledProcessError as e:
        print(f"Error searching: {e}")
        return []

def get_channel_info(video_url: str) -> Dict:
    """Extract channel info from a video URL"""
    try:
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--dump-json",
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        return {
            "channel_name": data.get("uploader", ""),
            "channel_id": data.get("channel_id", ""),
            "channel_url": data.get("channel_url", ""),
            "subscriber_count": data.get("channel_follower_count", 0),
            "video_title": data.get("title", ""),
            "video_url": video_url,
            "view_count": data.get("view_count", 0),
        }
        
    except Exception as e:
        print(f"Error getting channel info: {e}")
        return None

def main():
    print("🔍 YouTube Channel Finder - Discovering Prepper/Survival Channels")
    print("=" * 70)
    print(f"Searching {len(SEARCH_TERMS)} different queries...\n")
    
    all_channels = {}
    
    for search_term in SEARCH_TERMS:
        video_urls = search_youtube(search_term, max_results=5)
        
        for url in video_urls:
            channel_info = get_channel_info(url)
            if channel_info:
                channel_id = channel_info['channel_id']
                
                # Store unique channels only
                if channel_id not in all_channels:
                    all_channels[channel_id] = channel_info
                    print(f"  ✓ {channel_info['channel_name']} ({channel_info['subscriber_count']:,} subs)")
        
        print()
    
    print("=" * 70)
    print(f"✓ Found {len(all_channels)} unique channels\n")
    
    # Sort by subscriber count
    sorted_channels = sorted(all_channels.values(), 
                            key=lambda x: x['subscriber_count'] or 0, 
                            reverse=True)
    
    # Filter for "sweet spot" size (10k-500k subscribers)
    target_channels = [ch for ch in sorted_channels 
                      if 10000 <= (ch['subscriber_count'] or 0) <= 500000]
    
    print(f"📊 Channels in target range (10k-500k subscribers): {len(target_channels)}\n")
    
    # Save to file
    output_file = "discovered_channels.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Discovered Prepper/Survival Channels\n\n")
        f.write(f"## Summary\n")
        f.write(f"Total unique channels found: {len(all_channels)}\n")
        f.write(f"Channels in target range (10k-500k subs): {len(target_channels)}\n\n")
        f.write("---\n\n")
        
        f.write("## 🎯 Target Channels (10k-500k subscribers)\n\n")
        for i, channel in enumerate(target_channels, 1):
            f.write(f"### {i}. {channel['channel_name']}\n\n")
            f.write(f"**Subscribers:** {channel['subscriber_count']:,}\n\n")
            f.write(f"**Channel URL:** {channel['channel_url']}\n\n")
            f.write(f"**Sample Video:** [{channel['video_title']}]({channel['video_url']})\n\n")
            f.write(f"**Next Steps:**\n")
            f.write(f"1. Visit channel 'About' page for contact info\n")
            f.write(f"2. Look for email in video descriptions\n")
            f.write(f"3. Check social media links\n\n")
            f.write("---\n\n")
        
        f.write("\n## 📈 All Discovered Channels (Sorted by Size)\n\n")
        for channel in sorted_channels:
            subs = channel['subscriber_count'] or 0
            f.write(f"- **{channel['channel_name']}** ({subs:,} subs) - {channel['channel_url']}\n")
    
    print(f"✓ Report saved to: {output_file}")
    
    # Also save CSV
    csv_file = "discovered_channels.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("Channel Name,Channel URL,Subscribers,Sample Video URL,Sample Video Title\n")
        for channel in sorted_channels:
            subs = channel['subscriber_count'] or 0
            f.write(f'"{channel["channel_name"]}",')
            f.write(f'"{channel["channel_url"]}",')
            f.write(f'{subs},')
            f.write(f'"{channel["video_url"]}",')
            f.write(f'"{channel["video_title"]}"\n')
    
    print(f"✓ CSV saved to: {csv_file}")
    print("\n💡 Next step: Visit each channel's 'About' page to find business contact info")
    print("   Then add promising channels to your outreach_tracker.csv")

if __name__ == "__main__":
    main()

