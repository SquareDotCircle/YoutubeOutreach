#!/usr/bin/env python3
"""
Enhanced Channel Data Extractor
Extracts detailed metrics from YouTube channels using yt-dlp
Tier 1 metrics: avg views, engagement rate, contact info
"""

import subprocess
import json
import re
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def get_recent_videos(channel_url: str, count: int = 10) -> List[Dict]:
    """Get recent videos from a channel"""
    try:
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--dump-json',
            '--playlist-end', str(count),
            '--flat-playlist',
            f"{channel_url}/videos"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video_data = json.loads(line)
                        videos.append(video_data)
                    except:
                        continue
            return videos
    except Exception as e:
        print(f"Error getting recent videos: {e}")
    
    return []

def get_video_details(video_url: str) -> Optional[Dict]:
    """Get detailed stats for a single video"""
    try:
        cmd = ['yt-dlp', '--skip-download', '--dump-json', video_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Ensure required fields exist with defaults
            return {
                'view_count': data.get('view_count', 0),
                'like_count': data.get('like_count', 0),
                'comment_count': data.get('comment_count', 0),
                'duration': data.get('duration', 0),
                'upload_date': data.get('upload_date'),
                'title': data.get('title', ''),
            }
    except Exception as e:
        print(f"      ⚠️ Error getting video details: {e}")
    
    return None

def calculate_engagement_metrics(videos: List[Dict]) -> Dict:
    """Calculate engagement metrics from video list"""
    if not videos:
        return {}
    
    view_counts = []
    like_counts = []
    comment_counts = []
    durations = []
    upload_dates = []
    
    for video in videos:
        views = video.get('view_count', 0) or 0
        likes = video.get('like_count', 0) or 0
        comments = video.get('comment_count', 0) or 0
        duration = video.get('duration', 0) or 0
        upload_date = video.get('upload_date')
        
        if views > 0:
            view_counts.append(views)
            like_counts.append(likes)
            comment_counts.append(comments)
            
        if duration > 0:
            durations.append(duration)
            
        if upload_date:
            try:
                upload_dates.append(datetime.strptime(str(upload_date), '%Y%m%d'))
            except:
                pass
    
    # Calculate metrics
    metrics = {}
    
    if view_counts:
        metrics['avg_views'] = int(statistics.mean(view_counts))
        metrics['median_views'] = int(statistics.median(view_counts))
        
        # Engagement rate
        total_views = sum(view_counts)
        total_engagement = sum(like_counts) + sum(comment_counts)
        metrics['engagement_rate'] = round((total_engagement / total_views * 100), 2) if total_views > 0 else 0
    
    if durations:
        metrics['avg_video_length'] = int(statistics.mean(durations))
    
    # Upload frequency and consistency
    if len(upload_dates) >= 3:
        upload_dates.sort(reverse=True)
        
        # Recent upload activity
        now = datetime.now()
        recent_30_days = sum(1 for d in upload_dates if (now - d).days <= 30)
        metrics['videos_last_30_days'] = recent_30_days
        metrics['last_upload_date'] = upload_dates[0].strftime('%Y-%m-%d')
        
        # Upload frequency (videos per week)
        date_range = (upload_dates[0] - upload_dates[-1]).days
        if date_range > 0:
            weeks = date_range / 7
            metrics['upload_frequency'] = round(len(upload_dates) / weeks, 2)
        
        # Consistency score (regularity of uploads)
        if len(upload_dates) >= 4:
            gaps = [(upload_dates[i] - upload_dates[i+1]).days for i in range(len(upload_dates)-1)]
            if gaps:
                avg_gap = statistics.mean(gaps)
                std_gap = statistics.stdev(gaps) if len(gaps) > 1 else 0
                consistency = 1 - (std_gap / avg_gap if avg_gap > 0 else 0)
                metrics['consistency_score'] = round(max(0, min(1, consistency)), 2)
    
    # Viral video detection
    if view_counts and len(view_counts) >= 5:
        avg_views = statistics.mean(view_counts)
        viral_threshold = avg_views * 5
        metrics['recent_viral_count'] = sum(1 for v in view_counts if v > viral_threshold)
    
    # Growth trend
    if len(view_counts) >= 6:
        recent_avg = statistics.mean(view_counts[:3])
        older_avg = statistics.mean(view_counts[3:6])
        
        if recent_avg > older_avg * 1.5:
            metrics['growth_trend'] = 'rapid'
        elif recent_avg > older_avg * 1.2:
            metrics['growth_trend'] = 'growing'
        elif recent_avg < older_avg * 0.8:
            metrics['growth_trend'] = 'declining'
        else:
            metrics['growth_trend'] = 'stable'
    
    return metrics

def extract_email_from_text(text: str) -> Optional[str]:
    """Extract email address from text"""
    if not text:
        return None
    
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Filter out common non-business emails
    for email in emails:
        email_lower = email.lower()
        if not any(skip in email_lower for skip in ['example.com', 'youremail', 'email.com']):
            return email
    
    return None

def extract_social_links(text: str) -> Dict[str, str]:
    """Extract social media handles from text"""
    links = {}
    
    if not text:
        return links
    
    # Instagram
    instagram_match = re.search(r'instagram\.com/([a-zA-Z0-9._]+)', text)
    if instagram_match:
        links['instagram'] = instagram_match.group(1)
    elif re.search(r'@([a-zA-Z0-9._]+)', text) and 'instagram' in text.lower():
        handle_match = re.search(r'@([a-zA-Z0-9._]+)', text)
        if handle_match:
            links['instagram'] = handle_match.group(1)
    
    # Twitter/X
    twitter_match = re.search(r'(?:twitter|x)\.com/([a-zA-Z0-9_]+)', text)
    if twitter_match:
        links['twitter'] = twitter_match.group(1)
    
    # Website
    website_match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', text)
    if website_match:
        full_url = website_match.group(0)
        # Exclude social media sites
        if not any(social in full_url for social in ['youtube.com', 'twitter.com', 'instagram.com', 'facebook.com']):
            links['website'] = full_url
    
    # Check for affiliate/store indicators
    if any(keyword in text.lower() for keyword in ['shop', 'store', 'merch', 'affiliate']):
        links['has_store'] = True
    
    # Check for Patreon
    if 'patreon.com' in text.lower():
        links['has_patreon'] = True
    
    return links

def get_channel_about_page(channel_url: str) -> Optional[Dict]:
    """Get channel about page information"""
    try:
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--dump-json',
            '--playlist-items', '1',
            f"{channel_url}/videos"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout.strip().split('\n')[0])
            
            channel_info = {
                'channel_description': data.get('description', '')[:2000],  # First 2000 chars
                'channel_country': data.get('channel_country'),
                'total_video_count': data.get('playlist_count') or data.get('channel_video_count'),
            }
            
            return channel_info
    except Exception as e:
        print(f"Error getting about page: {e}")
    
    return None

def analyze_title_patterns(titles: List[str]) -> tuple[bool, float, str]:
    """
    Detect AI-generated content based on title patterns
    Returns: (is_spam, spam_score, reason)
    """
    if len(titles) < 5:
        return False, 0, "Not enough titles"
    
    spam_score = 0
    
    # PATTERN 1: Repetitive Structure
    # Check if titles follow same template
    title_lengths = [len(t.split()) for t in titles]
    avg_length = sum(title_lengths) / len(title_lengths)
    std_dev = (sum((x - avg_length) ** 2 for x in title_lengths) / len(title_lengths)) ** 0.5
    
    if std_dev < 2:  # All titles roughly same length = template
        spam_score += 2
    
    # PATTERN 2: Clickbait Keywords
    clickbait = ['must know', 'you won\'t believe', 'amazing', 'shocking',
                 'unbelievable', 'insane', 'mind blowing', 'secrets']
    clickbait_count = sum(1 for title in titles 
                         for keyword in clickbait 
                         if keyword in title.lower())
    
    if clickbait_count > len(titles) * 0.4:  # >40% have clickbait
        spam_score += 3
    
    # PATTERN 3: Numbered Lists
    numbered = sum(1 for t in titles 
                  if re.search(r'top \d+|#\d+|\d+ (tips|hacks|ways)', t.lower()))
    
    if numbered > len(titles) * 0.5:  # >50% are numbered lists
        spam_score += 3
    
    # PATTERN 4: Generic Titles
    generic = ['tips', 'hacks', 'tricks', 'facts', 'compilation', 'best of']
    generic_count = sum(1 for title in titles
                       for word in generic
                       if word in title.lower())
    
    if generic_count > len(titles) * 0.6:  # >60% generic
        spam_score += 2
    
    # PATTERN 5: Year/Part Numbers (Volume Indicator)
    serialized = sum(1 for t in titles
                    if re.search(r'20\d{2}|part \d+|episode \d+|vol \d+', t.lower()))
    
    if serialized > len(titles) * 0.3:  # >30% serialized
        spam_score += 2
    
    # PATTERN 6: Personal/Authentic Markers
    personal = ['my', 'i ', 'we ', 'our', 'update', 'week', 'day', 'failed', 
                'learned', 'trying', 'testing', 'review']
    personal_count = sum(1 for title in titles
                        for marker in personal
                        if marker in title.lower())
    
    if personal_count > len(titles) * 0.3:  # >30% personal
        spam_score -= 3  # NEGATIVE score = good sign
    
    # DECISION
    if spam_score >= 6:
        return True, spam_score, "AI-generated title patterns"
    
    return False, spam_score, "Authentic titles"

def get_enhanced_channel_data(channel_url: str, basic_data: Dict) -> Dict:
    """
    Get all enhanced channel data
    
    Args:
        channel_url: YouTube channel URL
        basic_data: Basic channel info already extracted
    
    Returns:
        Dict with all enhanced metrics (or basic data if extraction fails)
    """
    print(f"    📊 Extracting enhanced metrics...")
    
    enhanced_data = {**basic_data}  # Start with basic data
    
    try:
        # Get recent videos for analysis
        print(f"    📹 Fetching recent videos...")
        recent_videos = get_recent_videos(channel_url, count=10)
        
        if recent_videos:
            print(f"    ✓ Found {len(recent_videos)} recent videos")
            
            # Get detailed stats for each video
            detailed_videos = []
            for i, video in enumerate(recent_videos[:10], 1):
                video_id = video.get('id')
                if video_id:
                    print(f"    📊 Analyzing video {i}/10...", end='\r')
                    details = get_video_details(f"https://youtube.com/watch?v={video_id}")
                    if details:
                        detailed_videos.append(details)
            
            print(f"    ✓ Analyzed {len(detailed_videos)} videos     ")
            
            # Calculate metrics
            if detailed_videos:
                metrics = calculate_engagement_metrics(detailed_videos)
                enhanced_data.update(metrics)
                
                # Store video titles for AI farm detection
                enhanced_data['recent_titles'] = [v.get('title', '') for v in detailed_videos if v.get('title')]
                
                # Calculate view rate
                if 'avg_views' in metrics and basic_data.get('subscriber_count', 0) > 0:
                    view_rate = (metrics['avg_views'] / basic_data['subscriber_count']) * 100
                    enhanced_data['view_rate'] = round(view_rate, 2)
        
        # Get channel about page
        print(f"    📄 Fetching channel description...")
        about_data = get_channel_about_page(channel_url)
        if about_data:
            enhanced_data.update(about_data)
            
            # Extract contact info and links
            description = about_data.get('channel_description', '')
            
            email = extract_email_from_text(description)
            if email:
                enhanced_data['business_email'] = email
                print(f"    ✓ Found business email: {email}")
            
            social_links = extract_social_links(description)
            if social_links:
                if 'instagram' in social_links:
                    enhanced_data['instagram_handle'] = social_links['instagram']
                    print(f"    ✓ Found Instagram: @{social_links['instagram']}")
                if 'twitter' in social_links:
                    enhanced_data['twitter_handle'] = social_links['twitter']
                    print(f"    ✓ Found Twitter: @{social_links['twitter']}")
                if 'website' in social_links:
                    enhanced_data['website_url'] = social_links['website']
                    print(f"    ✓ Found website: {social_links['website']}")
                if social_links.get('has_store'):
                    enhanced_data['has_affiliate_store'] = 1
                    print(f"    ✓ Has affiliate store/merch")
                if social_links.get('has_patreon'):
                    enhanced_data['has_patreon'] = 1
                    print(f"    ✓ Has Patreon")
        
        # Summary
        print(f"    ✓ Enhanced data extraction complete")
        if 'engagement_rate' in enhanced_data:
            print(f"    → Engagement: {enhanced_data['engagement_rate']}%")
        if 'view_rate' in enhanced_data:
            print(f"    → View rate: {enhanced_data['view_rate']}%")
    
    except Exception as e:
        print(f"    ⚠️  Enhanced extraction failed: {e}")
        print(f"    → Using basic data only")
        import traceback
        traceback.print_exc()
    
    return enhanced_data

# Test function
if __name__ == "__main__":
    print("🧪 Testing Enhanced Channel Extractor")
    print("=" * 60)
    
    # Test with a sample channel
    test_url = "https://www.youtube.com/@CityPrepping"
    
    # Basic data (would come from initial extraction)
    basic_data = {
        'channel_name': 'City Prepping',
        'channel_id': 'UCxxxx',
        'channel_url': test_url,
        'subscriber_count': 1230000
    }
    
    enhanced = get_enhanced_channel_data(test_url, basic_data)
    
    print("\n📊 Results:")
    print("=" * 60)
    for key, value in enhanced.items():
        if key not in basic_data:  # Only show new data
            print(f"{key}: {value}")

