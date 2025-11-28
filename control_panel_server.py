#!/usr/bin/env python3
"""
Flask Backend for Control Panel
Handles workflow execution with Server-Sent Events for real-time progress
"""

from flask import Flask, render_template, request, Response, jsonify
import json
import subprocess
import requests
import os
import sys
from typing import List, Dict, Generator
from channel_database import ChannelDatabase
import anthropic
from enhanced_channel_extractor import get_enhanced_channel_data, analyze_title_patterns
import concurrent.futures
from functools import partial

app = Flask(__name__)

# Claude API Configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
DEFAULT_MODEL = "claude-sonnet-4-20250514"

# Session State - Track what we've already processed
SESSION_STATE = {
    'used_queries': set(),  # Search terms we've already used
    'discovered_channels': set(),  # Channel IDs we've already found
    'analyzed_channels': set()  # Channel IDs we've already analyzed
}

# Import workflow functions
sys.path.insert(0, os.path.dirname(__file__))

def generate_with_claude(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Generate text using Claude API"""
    try:
        # Create client with explicit configuration
        client = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            max_retries=2,
            timeout=60.0
        )
        
        message = client.messages.create(
            model=model,
            max_tokens=2048,
            temperature=0.8,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        print(f"Claude API error: {e}")
        import traceback
        traceback.print_exc()
    
    return ""

def generate_search_queries(product_context: str, target_direction: str, num_queries: int, model: str = DEFAULT_MODEL) -> List[str]:
    """Generate search queries using Claude with custom context"""
    
    # Get list of already-used queries
    used_queries_list = list(SESSION_STATE['used_queries'])
    used_queries_text = ""
    if used_queries_list:
        used_queries_text = f"\n\nQUERIES ALREADY USED (DO NOT REPEAT THESE):\n" + "\n".join(f"- {q}" for q in used_queries_list[:20])
    
    prompt = f"""You are an expert at finding YouTube channels whose AUDIENCES would be interested in buying a product.

PRODUCT WE'RE SELLING:
{product_context}

TARGET AUDIENCE INTERESTS:
{target_direction}
{used_queries_text}

CRITICAL: Generate YouTube search queries to find CHANNELS and CONTENT that this audience watches.
DO NOT search for the product itself. Search for the TOPICS and INTERESTS of potential buyers.
DO NOT repeat any of the already-used queries above - generate NEW, DIFFERENT queries.

Example:
- BAD: "hard drive knowledge library" (searching for the product)
- GOOD: "survival skills tutorial" (searching for audience interests)
- BAD: "offline knowledge storage"
- GOOD: "prepping for beginners" or "homesteading guide"

Generate {num_queries} UNIQUE, NEW YouTube search queries focusing on:
- Content the target audience watches
- Skills and topics they're interested in
- Lifestyle and hobby channels they follow
- Educational content in their niche
- NOT the product we're selling
- NOT queries we've already used

Make queries:
- 3-6 words each
- About audience interests, NOT our product
- Focus on channel topics and content themes
- Educational, tutorial, or lifestyle content
- DIFFERENT from previously used queries

Return ONLY a JSON array:
["query 1", "query 2", "query 3"]

Generate {num_queries} NEW search queries about AUDIENCE INTERESTS now:"""

    response = generate_with_claude(prompt, model)
    
    if not response:
        return []
    
    try:
        start = response.find('[')
        end = response.rfind(']') + 1
        
        if start >= 0 and end > start:
            json_str = response[start:end]
            queries = json.loads(json_str)
            
            valid_queries = []
            for q in queries:
                if isinstance(q, str) and len(q) > 3 and len(q) < 100:
                    q = q.strip().strip('"\'')
                    if q:
                        valid_queries.append(q)
            
            return valid_queries[:num_queries]
    except:
        pass
    
    return []

def search_youtube(query: str, max_results: int = 5) -> List[str]:
    """Search YouTube and return video URLs"""
    try:
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--get-id',
            '--flat-playlist',
            f'ytsearch{max_results}:{query}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            video_ids = result.stdout.strip().split('\n')
            return [f'https://www.youtube.com/watch?v={vid_id}' for vid_id in video_ids if vid_id]
    except:
        pass
    
    return []

def get_channel_info(video_url: str) -> Dict:
    """Get channel info from video"""
    try:
        cmd = ['yt-dlp', '--skip-download', '--dump-json', video_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            # Get subscriber count, ensure it's an integer (not None)
            sub_count = data.get('channel_follower_count')
            if sub_count is None:
                sub_count = 0
            
            return {
                'channel_id': data.get('channel_id', ''),
                'channel_name': data.get('uploader', 'Unknown Channel'),
                'channel_url': data.get('channel_url', ''),
                'subscriber_count': int(sub_count),
                'description': data.get('description', '')[:1000],
                'video_title': data.get('title', ''),
                'video_url': video_url
            }
    except Exception as e:
        print(f"Error getting channel info: {e}")
    
    return None

def quick_filter_channel(channel_data: Dict, product_context: str) -> tuple[bool, str]:
    """Quick heuristic filtering before expensive Claude analysis"""
    channel_name = channel_data.get('channel_name', '').lower()
    description = channel_data.get('description', '').lower()
    subs = channel_data.get('subscriber_count', 0)
    
    # Filter out obvious mismatches (instant, no API cost)
    
    # 1. Too generic/broad entertainment channels
    generic_keywords = ['compilation', 'funny moments', 'memes', 'gaming', 'music video', 
                       'trailer', 'movie clips', 'shorts', 'tiktok', 'reaction']
    if any(keyword in channel_name for keyword in generic_keywords):
        return False, "Generic entertainment channel"
    
    # 2. Kids/family entertainment
    kids_keywords = ['kids', 'cartoons', 'nursery rhymes', 'toys', 'unboxing']
    if any(keyword in channel_name or keyword in description[:200] for keyword in kids_keywords):
        return False, "Kids/family content"
    
    # 3. Wrong language indicators (if description is very short or non-English heavy)
    if description and len(description) > 100:
        # Simple heuristic: if description has lots of non-ASCII, might be foreign
        non_ascii_ratio = sum(1 for c in description[:500] if ord(c) > 127) / min(len(description[:500]), 1)
        if non_ascii_ratio > 0.3:
            return False, "Likely non-English content"
    
    # 4. Corporate/news channels (usually low conversion)
    corporate_keywords = ['official', 'news', 'media', 'network', 'corporation']
    if any(keyword in channel_name for keyword in corporate_keywords):
        if subs > 200000:  # Large corporate channels
            return False, "Large corporate/news channel"
    
    # 5. Must have SOME description (no description = low quality/spam)
    if not description or len(description) < 50:
        return False, "No meaningful description"
    
    # 6. Check for positive indicators (makes it through filter)
    positive_keywords = ['survival', 'prepper', 'prep', 'homestead', 'off grid', 'offgrid',
                        'self reliance', 'bushcraft', 'tactical', 'shtf', 'grid down',
                        'emergency', 'preparedness', 'outdoors', 'wilderness', 'camping']
    
    has_positive = any(keyword in description or keyword in channel_name 
                      for keyword in positive_keywords)
    
    if has_positive:
        return True, "Passed pre-filter"
    
    # 7. If nothing obviously wrong but no strong signals, let it through
    # (better false positive than false negative)
    return True, "No obvious issues"

def is_ai_content_farm(channel_data: Dict) -> tuple[bool, str]:
    """
    Aggressive AI content farm detection
    Checks: volume (>500), frequency (>5/week), consistency (>0.95),
           engagement (<1%), title patterns (score>=6)
    """
    # Get the key metrics
    total_videos = channel_data.get('total_video_count', 0)
    upload_freq = channel_data.get('upload_frequency', 0)  # videos per week
    consistency = channel_data.get('consistency_score', 0)  # 0-1 scale
    engagement_rate = channel_data.get('engagement_rate', 0)
    subs = channel_data.get('subscriber_count', 0)
    
    # HARD CUTOFFS (instant rejection)
    
    # 1. Massive video count = content farm
    if total_videos and total_videos > 500:
        return True, f"Content farm ({total_videos} videos)"
    
    # 2. Multiple videos per day = bot
    if upload_freq and upload_freq > 5:  # More than 5/week (aggressive threshold)
        return True, f"Bot-like frequency ({upload_freq:.1f}/week)"
    
    # 3. Perfect consistency + high volume = automated
    if consistency and consistency > 0.95 and total_videos and total_videos > 200:
        return True, f"Bot pattern (consistency {consistency:.2f}, {total_videos} videos)"
    
    # 4. Title pattern analysis
    if 'recent_titles' in channel_data and channel_data['recent_titles']:
        is_spam, score, reason = analyze_title_patterns(channel_data['recent_titles'])
        if is_spam:
            return True, f"Spam titles ({reason}, score: {score})"
    
    # COMBINATION PATTERNS (scoring system)
    red_flags = 0
    reasons = []
    
    # High volume (300-500 videos)
    if total_videos:
        if 300 <= total_videos <= 500:
            red_flags += 2
            reasons.append(f"High volume ({total_videos})")
        elif 200 <= total_videos < 300:
            red_flags += 1
            reasons.append(f"Moderate volume ({total_videos})")
    
    # Very frequent uploads (3-5 per week)
    if upload_freq:
        if 3 <= upload_freq <= 5:
            red_flags += 2
            reasons.append(f"Frequent ({upload_freq:.1f}/week)")
        elif 2.5 <= upload_freq < 3:
            red_flags += 1
            reasons.append(f"Regular ({upload_freq:.1f}/week)")
    
    # High consistency (0.85-0.95)
    if consistency:
        if 0.90 <= consistency <= 0.95:
            red_flags += 2
            reasons.append(f"Very consistent ({consistency:.2f})")
        elif 0.85 <= consistency < 0.90:
            red_flags += 1
            reasons.append(f"Consistent ({consistency:.2f})")
    
    # Low engagement despite volume
    if engagement_rate is not None and engagement_rate < 1.0 and total_videos and total_videos > 100:
        red_flags += 2
        reasons.append(f"Low engagement ({engagement_rate}%)")
    
    # DECISION: 3+ red flags = likely content farm
    if red_flags >= 3:
        return True, f"Likely content farm ({red_flags} flags: {', '.join(reasons)})"
    
    return False, "Real creator"

def analyze_channel_with_claude(channel_data: Dict, product_context: str, model: str = DEFAULT_MODEL) -> Dict:
    """Analyze channel relevance using Claude API with enhanced metrics"""
    
    channel_name = channel_data.get('channel_name', 'Unknown')
    description = channel_data.get('description', '')[:800]
    channel_description = channel_data.get('channel_description', '')[:800]
    subs = channel_data.get('subscriber_count', 0)
    
    # Enhanced metrics
    avg_views = channel_data.get('avg_views_per_video')
    engagement_rate = channel_data.get('engagement_rate')
    view_rate = channel_data.get('view_rate')
    upload_freq = channel_data.get('upload_frequency')
    consistency = channel_data.get('consistency_score')
    growth = channel_data.get('growth_trend')
    viral_count = channel_data.get('recent_viral_count')
    has_email = bool(channel_data.get('business_email'))
    has_store = bool(channel_data.get('has_affiliate_store'))
    has_patreon = bool(channel_data.get('has_patreon'))
    
    # Build enhanced metrics section
    enhanced_metrics_text = ""
    if avg_views is not None:
        enhanced_metrics_text += f"\nAverage Views per Video: {avg_views:,}"
    if view_rate is not None:
        enhanced_metrics_text += f"\nView Rate: {view_rate:.1f}% (views/subscribers)"
    if engagement_rate is not None:
        enhanced_metrics_text += f"\nEngagement Rate: {engagement_rate}% (likes+comments/views)"
    if upload_freq is not None:
        enhanced_metrics_text += f"\nUpload Frequency: {upload_freq:.1f} videos/week"
    if consistency is not None:
        enhanced_metrics_text += f"\nConsistency Score: {consistency:.2f}/1.0"
    if growth:
        enhanced_metrics_text += f"\nGrowth Trend: {growth}"
    if viral_count:
        enhanced_metrics_text += f"\nRecent Viral Videos: {viral_count}"
    if has_email:
        enhanced_metrics_text += "\n✓ Has Business Email"
    if has_store:
        enhanced_metrics_text += "\n✓ Has Affiliate Store/Merch"
    if has_patreon:
        enhanced_metrics_text += "\n✓ Has Patreon (monetizing audience)"
    
    full_description = channel_description if channel_description else description
    
    prompt = f"""Analyze if this YouTube channel's AUDIENCE would be interested in buying this product.

OUR PRODUCT (what we're selling):
{product_context}

YOUTUBE CHANNEL TO EVALUATE:
Name: {channel_name}
Subscribers: {subs:,}
Description: {full_description if full_description else 'No description available'}
{enhanced_metrics_text}

CRITICAL EVALUATION CRITERIA:

1. AUDIENCE RESONANCE (0-10):
   - Would their specific viewers actually BUY this product?
   - Does their audience demographic match our target buyer?
   - Would their viewers see clear value in owning this?
   - Is there a direct problem-solution fit?

2. CONTENT ALIGNMENT (0-10):
   - Does their content naturally relate to our product's purpose?
   - Do they create content where this product would be mentioned?
   - Would featuring this product feel native to their content?
   - Is the lifestyle/niche an authentic match?

3. ENGAGEMENT POTENTIAL (0-10):
   Consider channel engagement indicators:
   - Content quality and production value
   - Authenticity and trust with audience
   - History of product mentions or sponsorships
   - Community interaction level
   - Likelihood of creating compelling product content
   - Estimated conversion potential (will viewers actually buy?)
   - Creator's credibility in recommending products
   - Audience's trust in creator's recommendations
   
   USE ENHANCED METRICS WHEN AVAILABLE:
   - Engagement Rate >5% = High trust community (score +2)
   - View Rate >30% = Real engaged audience (score +1)
   - Growing trend = Rising star, get in early (score +1)
   - Has business email = Professional, responds (score +1)
   - Has Patreon/Store = Audience already buys (score +2)
   - Consistent uploads (>0.8) = Reliable partner (score +1)
   - Recent virals = Bonus reach potential (score +1)

AVOID HIGH SCORES FOR:
- Competitors or similar product sellers
- Generic review/unboxing channels (low conversion)
- Misaligned demographics (wrong age/interests)
- Entertainment-only channels (viewers not buyers)
- Channels with low audience trust

PRIORITIZE HIGH SCORES FOR:
- Lifestyle match (audience lives this way)
- Educational content creators (high trust)
- Community builders (loyal audiences)
- Niche experts (authority in space)
- Authentic product users (not just reviewers)

Rate 0-10 (be highly selective):
- Most channels: 2-5 (not a good fit)
- Decent channels: 6-7 (possible fit)
- Great channels: 8-9 (strong fit)
- Perfect channels: 10 (rare, ideal match)

Respond with ONLY this JSON:
{{
  "relevance_score": X,
  "audience_match_score": X,
  "engagement_score": X,
  "overall_score": X,
  "priority": "low|medium|high",
  "relevant": true|false,
  "reason": "Specific reason why their audience would/wouldn't buy this product",
  "pitch": "Specific pitch angle: how to present this product to THIS creator's unique audience",
  "engagement_notes": "Expected engagement level and conversion potential"
}}"""

    response = generate_with_claude(prompt, model)
    
    if not response:
        return {"relevant": False, "reason": "Analysis failed"}
    
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start >= 0 and end > start:
            json_str = response[start:end]
            analysis = json.loads(json_str)
            
            if 'relevant' in analysis:
                return analysis
    except:
        pass
    
    return {"relevant": False, "reason": "Could not parse analysis"}

def workflow_generator(product_context: str, target_direction: str, num_queries: int, results_per_query: int, 
                      min_subscribers: int = 0, max_subscribers: int = 100000000) -> Generator:
    """Execute workflow and yield progress updates"""
    
    # Check Claude API
    try:
        # Just verify API key exists, don't create client yet
        if not ANTHROPIC_API_KEY or len(ANTHROPIC_API_KEY) < 20:
            raise ValueError("Invalid API key")
        yield {'type': 'log', 'message': '✓ Claude API key configured', 'logType': 'success'}
    except Exception as e:
        yield {'type': 'log', 'message': f'❌ Claude API error: {str(e)}', 'logType': 'error'}
        yield {'type': 'error', 'message': 'Claude API not available'}
        return
    
    # Step 1: Generate queries
    yield {'type': 'status', 'message': 'Generating search queries with AI...'}
    yield {'type': 'log', 'message': '🤖 Step 1: AI-generating search queries...', 'logType': 'info'}
    
    queries = generate_search_queries(product_context, target_direction, num_queries)
    
    if not queries:
        yield {'type': 'log', 'message': '❌ Failed to generate queries', 'logType': 'error'}
        yield {'type': 'error', 'message': 'Query generation failed'}
        return
    
    # Mark queries as used in session
    for q in queries:
        SESSION_STATE['used_queries'].add(q.lower())
    
    yield {'type': 'status', 'queries': len(queries)}
    yield {'type': 'log', 'message': f'✓ Generated {len(queries)} NEW queries', 'logType': 'success'}
    
    for i, q in enumerate(queries, 1):
        yield {'type': 'log', 'message': f'  {i}. {q}', 'logType': 'info'}
    
    # Show session stats
    total_queries_this_session = len(SESSION_STATE['used_queries'])
    if total_queries_this_session > len(queries):
        yield {'type': 'log', 'message': f'  ℹ️ Total unique queries this session: {total_queries_this_session}', 'logType': 'info'}
    
    # Step 2: Search YouTube (Parallel)
    yield {'type': 'status', 'message': 'Searching YouTube in parallel...'}
    yield {'type': 'log', 'message': '\n🔍 Step 2: Searching YouTube (parallel)...', 'logType': 'info'}
    
    all_channels = {}
    
    # Parallelize YouTube searches
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        search_func = partial(search_youtube, max_results=results_per_query)
        search_results = list(executor.map(search_func, queries))
    
    # Collect all video URLs with their source queries
    all_video_urls = []
    for query, video_urls in zip(queries, search_results):
        yield {'type': 'log', 'message': f'  ✓ "{query}" - found {len(video_urls)} videos', 'logType': 'info'}
        all_video_urls.extend(video_urls)
    
    yield {'type': 'log', 'message': f'  Extracting channel info (parallel)...', 'logType': 'info'}
    
    # Parallelize channel info extraction
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        channel_infos = list(executor.map(get_channel_info, all_video_urls))
    
    # Process channel infos
    for url, channel_info in zip(all_video_urls, channel_infos):
        if channel_info:
            channel_id = channel_info['channel_id']
            subs = channel_info.get('subscriber_count', 0) or 0  # Handle None
            channel_name = channel_info['channel_name']
            
            # Skip if subscriber count is unavailable
            if subs == 0:
                yield {'type': 'log', 'message': f'    ⏭️ {channel_name} (subscriber count hidden)', 'logType': 'info'}
                continue
            
            # Check if already discovered in this session
            if channel_id in SESSION_STATE['discovered_channels']:
                yield {'type': 'log', 'message': f'    ⏭️ {channel_name} (already discovered this session)', 'logType': 'info'}
                continue
            
            # Apply subscriber count filter
            if subs < min_subscribers or subs > max_subscribers:
                yield {'type': 'log', 'message': f'    ⏭️ {channel_name} ({subs:,} subs - outside range)', 'logType': 'info'}
                continue
            
            if channel_id not in all_channels:
                # Extract enhanced data (Tier 1 metrics)
                yield {'type': 'log', 'message': f'    ✓ {channel_name} ({subs:,} subs) - extracting enhanced data...', 'logType': 'success'}
                
                try:
                    enhanced_data = get_enhanced_channel_data(channel_info['channel_url'], channel_info)
                    all_channels[channel_id] = enhanced_data
                except Exception as e:
                    yield {'type': 'log', 'message': f'      ⚠️ Enhanced extraction failed, using basic data', 'logType': 'info'}
                    all_channels[channel_id] = channel_info
                
                SESSION_STATE['discovered_channels'].add(channel_id)
                yield {'type': 'status', 'channels': len(all_channels)}
    
    yield {'type': 'log', 'message': f'\n✓ Found {len(all_channels)} unique channels', 'logType': 'success'}
    
    if not all_channels:
        yield {'type': 'log', 'message': '❌ No channels found', 'logType': 'error'}
        yield {'type': 'error', 'message': 'No channels found'}
        return
    
    # Step 3: Filter AI Content Farms
    yield {'type': 'status', 'message': 'Filtering AI content farms...'}
    yield {'type': 'log', 'message': '\n🤖 Step 3: Filtering AI content farms...', 'logType': 'info'}
    
    real_creators = {}
    ai_farm_count = 0
    
    for channel_id, channel in all_channels.items():
        is_farm, reason = is_ai_content_farm(channel)
        if is_farm:
            ai_farm_count += 1
            yield {'type': 'log', 'message': f'    ⏭️ {channel["channel_name"]} - {reason}', 'logType': 'info'}
        else:
            real_creators[channel_id] = channel
    
    yield {'type': 'log', 'message': f'✓ Filtered {ai_farm_count} AI farms, kept {len(real_creators)} real creators', 'logType': 'success'}
    
    if not real_creators:
        yield {'type': 'log', 'message': '❌ No real creators found after filtering', 'logType': 'error'}
        yield {'type': 'error', 'message': 'All channels filtered as AI farms'}
        return
    
    # Update all_channels to only include real creators
    all_channels = real_creators
    
    # Step 4: Save to database
    yield {'type': 'status', 'message': 'Saving to database...'}
    yield {'type': 'log', 'message': '\n💾 Step 4: Saving to database...', 'logType': 'info'}
    
    db = ChannelDatabase()
    db.connect()
    
    for channel_id, channel_data in all_channels.items():
        channel_data['category'] = 'ai_discovered'
        db.add_channel(channel_data)
    
    db.close()
    
    yield {'type': 'log', 'message': '✓ Channels saved', 'logType': 'success'}
    
    # Filter out already-analyzed channels (deduplication)
    channels_to_analyze = {
        ch_id: ch_data for ch_id, ch_data in all_channels.items()
        if ch_id not in SESSION_STATE['analyzed_channels']
    }
    
    already_analyzed_count = len(all_channels) - len(channels_to_analyze)
    if already_analyzed_count > 0:
        yield {'type': 'log', 'message': f'  ℹ️ Skipping {already_analyzed_count} already-analyzed channels', 'logType': 'info'}
    
    if not channels_to_analyze:
        yield {'type': 'log', 'message': '  ⚠️ All channels already analyzed this session', 'logType': 'info'}
        yield {'type': 'complete', 'results': []}
        return
    
    # Step 5: Deep AI Analysis (expensive, only on filtered channels)
    yield {'type': 'status', 'message': 'Deep AI analysis with Claude...'}
    yield {'type': 'log', 'message': f'\n🤖 Step 5: Deep AI analysis ({len(channels_to_analyze)} NEW channels)...', 'logType': 'info'}
    yield {'type': 'log', 'message': f'⏳ Estimated time: ~{len(channels_to_analyze) * 3} seconds', 'logType': 'info'}
    
    results = []
    analyzed = 0
    
    for i, (channel_id, channel_data) in enumerate(channels_to_analyze.items(), 1):
        yield {'type': 'log', 'message': f'  [{i}/{len(channels_to_analyze)}] Analyzing {channel_data["channel_name"]}...', 'logType': 'info'}
        
        analysis = analyze_channel_with_claude(channel_data, product_context)
        
        # Mark as analyzed
        SESSION_STATE['analyzed_channels'].add(channel_id)
        
        result = {
            'channel_id': channel_id,
            'channel_name': channel_data['channel_name'],
            'channel_url': channel_data['channel_url'],
            'subscriber_count': channel_data['subscriber_count'],
            'analysis': analysis
        }
        
        results.append(result)
        analyzed += 1
        
        score = analysis.get('overall_score', 0)
        relevant = "✓" if analysis.get('relevant', False) else "✗"
        
        yield {'type': 'log', 'message': f'    {relevant} Score: {score}/10', 'logType': 'success' if analysis.get('relevant') else 'info'}
        yield {'type': 'status', 'analyzed': analyzed}
        
        if analysis.get('relevant', False):
            yield {'type': 'status', 'relevant': len([r for r in results if r['analysis'].get('relevant', False)])}
    
    # Complete
    relevant_count = len([r for r in results if r['analysis'].get('relevant', False)])
    
    yield {'type': 'log', 'message': f'\n🎉 Workflow complete!', 'logType': 'success'}
    yield {'type': 'log', 'message': f'  This run: {len(results)} analyzed | {relevant_count} relevant', 'logType': 'info'}
    
    # Session summary
    yield {'type': 'log', 'message': f'\n📊 Session Summary:', 'logType': 'info'}
    yield {'type': 'log', 'message': f'  • Total unique queries used: {len(SESSION_STATE["used_queries"])}', 'logType': 'info'}
    yield {'type': 'log', 'message': f'  • Total channels discovered: {len(SESSION_STATE["discovered_channels"])}', 'logType': 'info'}
    yield {'type': 'log', 'message': f'  • Total channels analyzed: {len(SESSION_STATE["analyzed_channels"])}', 'logType': 'info'}
    
    # Update viewer
    try:
        subprocess.run(['python3', 'channel_viewer.py'], capture_output=True)
        yield {'type': 'log', 'message': '✓ Channel viewer updated', 'logType': 'success'}
    except:
        pass
    
    yield {'type': 'complete', 'results': results}

@app.route('/')
def index():
    """Serve control panel"""
    html_path = os.path.join(os.path.dirname(__file__), 'control_panel.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/session_stats')
def session_stats():
    """Get current session statistics"""
    return jsonify({
        'used_queries': list(SESSION_STATE['used_queries']),
        'used_queries_count': len(SESSION_STATE['used_queries']),
        'discovered_channels_count': len(SESSION_STATE['discovered_channels']),
        'analyzed_channels_count': len(SESSION_STATE['analyzed_channels'])
    })

@app.route('/reset_session', methods=['POST'])
def reset_session():
    """Reset session state"""
    SESSION_STATE['used_queries'].clear()
    SESSION_STATE['discovered_channels'].clear()
    SESSION_STATE['analyzed_channels'].clear()
    return jsonify({'status': 'success', 'message': 'Session reset'})

@app.route('/start_workflow')
def start_workflow():
    """Start workflow with SSE progress updates"""
    product_context = request.args.get('productContext', '')
    target_direction = request.args.get('targetDirection', '')
    num_queries = int(request.args.get('numQueries', 3))
    results_per_query = int(request.args.get('resultsPerQuery', 5))
    min_subscribers = int(request.args.get('minSubscribers', 0))
    max_subscribers = int(request.args.get('maxSubscribers', 100000000))
    
    def generate():
        for event in workflow_generator(product_context, target_direction, num_queries, results_per_query,
                                       min_subscribers, max_subscribers):
            event_type = event.pop('type', 'message')
            yield f"event: {event_type}\ndata: {json.dumps(event)}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Set static folder
    app.static_folder = os.path.dirname(__file__)
    
    print("🚀 Control Panel Server Starting...")
    print("=" * 60)
    print("\n📍 Access the control panel at:")
    print("   http://localhost:5000\n")
    print("=" * 60)
    print("\n✓ Server ready. Press Ctrl+C to stop.\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

