#!/usr/bin/env python3
"""
Fully Automated Workflow:
1. Ollama generates search queries
2. Search YouTube with those queries
3. Ollama analyzes channels for relevance
"""

import subprocess
import json
import csv
import requests
from typing import List, Dict
from channel_database import ChannelDatabase

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"

def generate_with_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Generate text using Ollama"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9
            }
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', '')
    except Exception as e:
        print(f"Error calling Ollama: {e}")
    
    return ""

def generate_search_queries(num_queries: int = 3, model: str = DEFAULT_MODEL, 
                           product_context: str = None, target_direction: str = None) -> List[str]:
    """Generate search queries using Ollama with optional custom context"""
    
    # Use default context if not provided
    if not product_context:
        product_context = """Hard drives containing offline knowledge libraries for survival, 
preparedness, and self-reliance. Includes medical guides, technical manuals, agricultural 
knowledge, and essential information for grid-down scenarios."""
    
    if not target_direction:
        target_direction = """YouTube channels focused on prepping, survival skills, homesteading, 
off-grid living, and emergency preparedness. Target audience: 25-55 year old preppers, 
survivalists, and self-reliance enthusiasts."""
    
    prompt = f"""You are an expert at finding YouTube channels whose AUDIENCES would be interested in buying a product.

PRODUCT WE'RE SELLING:
{product_context}

TARGET AUDIENCE INTERESTS:
{target_direction}

CRITICAL: Generate YouTube search queries to find CHANNELS and CONTENT that this audience watches.
DO NOT search for the product itself. Search for the TOPICS and INTERESTS of potential buyers.

Example:
- BAD: "hard drive knowledge library" (searching for the product)
- GOOD: "survival skills tutorial" (searching for audience interests)
- BAD: "offline knowledge storage"
- GOOD: "prepping for beginners" or "homesteading guide"

Generate {num_queries} YouTube search queries focusing on:
- Content the target audience watches
- Skills and topics they're interested in
- Lifestyle and hobby channels they follow
- Educational content in their niche
- NOT the product we're selling

Make queries:
- 3-6 words each
- About audience interests, NOT our product
- Focus on channel topics and content themes
- Educational, tutorial, or lifestyle content

Return ONLY a JSON array:
["query 1", "query 2", "query 3"]

Generate {num_queries} search queries about AUDIENCE INTERESTS now:"""

    print(f"🤖 Generating {num_queries} search queries with AI...")
    print(f"   Model: {model}")
    print(f"   ⏳ This takes ~30 seconds...\n")
    
    response = generate_with_ollama(prompt, model)
    
    if not response:
        print("❌ Failed to generate queries")
        return []
    
    try:
        # Extract JSON from response
        start = response.find('[')
        end = response.rfind(']') + 1
        
        if start >= 0 and end > start:
            json_str = response[start:end]
            queries = json.loads(json_str)
            
            # Clean and validate
            valid_queries = []
            for q in queries:
                if isinstance(q, str) and len(q) > 3 and len(q) < 100:
                    q = q.strip().strip('"\'')
                    if q:
                        valid_queries.append(q)
            
            return valid_queries[:num_queries]
    except Exception as e:
        print(f"⚠️ Could not parse queries: {e}")
    
    return []

def search_youtube(query: str, max_results: int = 5) -> List[str]:
    """Search YouTube and return video URLs"""
    print(f"  🔍 Searching: '{query}'...", end=' ')
    
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
            urls = [f'https://www.youtube.com/watch?v={vid_id}' for vid_id in video_ids if vid_id]
            print(f"✓ {len(urls)} videos")
            return urls
    except Exception as e:
        print(f"✗ Error")
    
    return []

def get_channel_info(video_url: str) -> Dict:
    """Get channel info from video"""
    try:
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--dump-json',
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                'channel_id': data.get('channel_id', ''),
                'channel_name': data.get('uploader', ''),
                'channel_url': data.get('channel_url', ''),
                'subscriber_count': data.get('channel_follower_count', 0),
                'description': data.get('description', '')[:1000],
                'video_title': data.get('title', ''),
                'video_url': video_url
            }
    except:
        pass
    
    return None

def analyze_channel_with_ollama(channel_data: Dict, model: str = DEFAULT_MODEL, 
                               product_context: str = None) -> Dict:
    """Analyze channel relevance using Ollama with optional custom product context"""
    
    channel_name = channel_data.get('channel_name', 'Unknown')
    description = channel_data.get('description', '')[:800]
    subs = channel_data.get('subscriber_count', 0)
    
    # Use default context if not provided
    if not product_context:
        product_context = """Hard drives with offline knowledge for grid-down scenarios 
(medical, survival, technical info). Target audience: Preppers, survivalists, homesteaders."""
    
    prompt = f"""Analyze if this YouTube channel's AUDIENCE would be interested in buying this product.

OUR PRODUCT (what we're selling):
{product_context}

YOUTUBE CHANNEL TO EVALUATE:
Name: {channel_name}
Subscribers: {subs:,}
Description: {description if description else 'No description available'}

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

    response = generate_with_ollama(prompt, model)
    
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

def main(product_context: str = None, target_direction: str = None, 
         num_queries: int = 3, results_per_query: int = 5):
    """
    Main workflow function
    
    Args:
        product_context: Description of the product being promoted
        target_direction: Target audience and channel characteristics
        num_queries: Number of search queries to generate (default: 3)
        results_per_query: Number of videos to fetch per query (default: 5)
    """
    print("🤖 FULLY AUTOMATED AI WORKFLOW")
    print("=" * 70)
    print("\nThis workflow:")
    print("  1. Uses AI to generate search queries")
    print("  2. Searches YouTube with those queries")
    print("  3. Uses AI to analyze each channel found")
    print("  4. Generates prioritized report")
    
    if product_context:
        print(f"\n📦 Custom Product Context: {product_context[:80]}...")
    if target_direction:
        print(f"🎯 Custom Target Direction: {target_direction[:80]}...")
    
    print("\n" + "=" * 70)
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code != 200:
            print("❌ Ollama server not running!")
            print("   Start it: ollama serve")
            return
    except:
        print("❌ Ollama server not running!")
        print("   Start it: ollama serve")
        return
    
    print("✓ Ollama server is running\n")
    
    # Step 1: Generate search queries with AI
    print("STEP 1: AI-Generated Search Queries")
    print("=" * 70)
    
    queries = generate_search_queries(
        num_queries=num_queries,
        product_context=product_context,
        target_direction=target_direction
    )
    
    if not queries:
        print("❌ Failed to generate queries. Exiting.")
        return
    
    print(f"\n✨ AI Generated {len(queries)} search queries:")
    for i, q in enumerate(queries, 1):
        print(f"   {i}. {q}")
    
    # Step 2: Search YouTube
    print("\n" + "=" * 70)
    print("STEP 2: Searching YouTube")
    print("=" * 70 + "\n")
    
    all_channels = {}
    
    for query in queries:
        video_urls = search_youtube(query, max_results=results_per_query)
        
        for url in video_urls:
            print(f"    📡 Fetching channel...", end=' ')
            channel_info = get_channel_info(url)
            
            if channel_info:
                channel_id = channel_info['channel_id']
                
                if channel_id not in all_channels:
                    all_channels[channel_id] = channel_info
                    print(f"✓ {channel_info['channel_name']}")
                else:
                    print("(duplicate)")
    
    print(f"\n✓ Found {len(all_channels)} unique channels")
    
    if not all_channels:
        print("❌ No channels found. Try different queries.")
        return
    
    # Step 3: Save to database
    print("\n" + "=" * 70)
    print("STEP 3: Saving to Database")
    print("=" * 70 + "\n")
    
    db = ChannelDatabase()
    db.connect()
    
    channel_ids = []
    for channel_id, channel_data in all_channels.items():
        channel_data['category'] = 'ai_discovered'
        if db.add_channel(channel_data):
            subs = channel_data['subscriber_count']
            print(f"  ✓ {channel_data['channel_name']} ({subs:,} subs)")
            channel_ids.append(channel_id)
    
    db.close()
    
    # Step 4: AI Analysis
    print("\n" + "=" * 70)
    print("STEP 4: AI Analysis of Channels")
    print("=" * 70)
    print(f"\n⏳ Analyzing {len(channel_ids)} channels...")
    print(f"   (~30 seconds per channel = ~{len(channel_ids) * 30} seconds total)\n")
    
    results = []
    
    for i, (channel_id, channel_data) in enumerate(all_channels.items(), 1):
        print(f"[{i}/{len(all_channels)}] {channel_data['channel_name']}...", end=' ')
        
        analysis = analyze_channel_with_ollama(channel_data, product_context=product_context)
        
        result = {
            'channel_id': channel_id,
            'channel_name': channel_data['channel_name'],
            'channel_url': channel_data['channel_url'],
            'subscriber_count': channel_data['subscriber_count'],
            'analysis': analysis
        }
        
        results.append(result)
        
        score = analysis.get('overall_score', 0)
        relevant = "✓" if analysis.get('relevant', False) else "✗"
        print(f"{relevant} Score: {score}/10")
    
    # Step 5: Generate Report
    print("\n" + "=" * 70)
    print("STEP 5: Generating Report")
    print("=" * 70 + "\n")
    
    relevant = [r for r in results if r['analysis'].get('relevant', False)]
    not_relevant = [r for r in results if not r['analysis'].get('relevant', False)]
    
    # Save detailed report
    report_file = 'ai_automated_report.md'
    with open(report_file, 'w') as f:
        f.write("# AI-Automated Channel Discovery & Analysis Report\n\n")
        f.write(f"## Search Queries Used\n\n")
        for i, q in enumerate(queries, 1):
            f.write(f"{i}. {q}\n")
        
        f.write(f"\n## Summary\n\n")
        f.write(f"- Total Channels Found: {len(results)}\n")
        f.write(f"- Relevant: {len(relevant)}\n")
        f.write(f"- Not Relevant: {len(not_relevant)}\n\n")
        
        f.write("---\n\n")
        f.write("## ✅ RELEVANT CHANNELS\n\n")
        
        relevant.sort(key=lambda x: x['analysis'].get('overall_score', 0), reverse=True)
        
        for r in relevant:
            a = r['analysis']
            f.write(f"### {r['channel_name']}\n\n")
            f.write(f"**URL:** {r['channel_url']}\n")
            f.write(f"**Subscribers:** {r['subscriber_count']:,}\n\n")
            f.write(f"**Scores:**\n")
            f.write(f"- Relevance: {a.get('relevance_score', 'N/A')}/10\n")
            f.write(f"- Audience Match: {a.get('audience_match_score', 'N/A')}/10\n")
            f.write(f"- Engagement: {a.get('engagement_score', 'N/A')}/10\n")
            f.write(f"- **Overall: {a.get('overall_score', 'N/A')}/10**\n\n")
            f.write(f"**Priority:** {a.get('priority', 'N/A').upper()}\n\n")
            f.write(f"**Why Relevant:** {a.get('reason', 'N/A')}\n\n")
            f.write(f"**Suggested Approach:** {a.get('pitch', 'N/A')}\n\n")
            f.write("---\n\n")
        
        if not_relevant:
            f.write("## ❌ NOT RELEVANT\n\n")
            for r in not_relevant:
                f.write(f"- **{r['channel_name']}**: {r['analysis'].get('reason', 'Not a good fit')}\n")
    
    print(f"✓ Report saved to: {report_file}")
    
    # Show summary
    print("\n" + "=" * 70)
    print("🎉 WORKFLOW COMPLETE!")
    print("=" * 70)
    
    print(f"\n📊 Results:")
    print(f"   Channels Found: {len(results)}")
    print(f"   ✅ Relevant: {len(relevant)}")
    print(f"   ❌ Not Relevant: {len(not_relevant)}")
    
    if relevant:
        print(f"\n🎯 RELEVANT CHANNELS (Recommended for Outreach):\n")
        
        for r in relevant:
            a = r['analysis']
            score = a.get('overall_score', 0)
            priority = a.get('priority', 'unknown').upper()
            subs = r['subscriber_count']
            
            print(f"   {priority:6s} | {score:4}/10 | {r['channel_name']}")
            print(f"           {subs:,} subs")
            print(f"           {r['channel_url']}/about")
            print(f"           → {a.get('reason', 'N/A')[:70]}...")
            print()
    
    if not_relevant:
        print(f"\n❌ NOT RELEVANT:")
        for r in not_relevant:
            print(f"   • {r['channel_name']}: {r['analysis'].get('reason', 'N/A')}")
    
    # Update viewer
    print(f"\n🔄 Updating channel viewer...")
    subprocess.run(['python', 'channel_viewer.py'], capture_output=True)
    print(f"✓ Viewer updated")
    
    print(f"\n📄 Files created:")
    print(f"   - {report_file}")
    print(f"   - channels_viewer.html (updated)")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Review: {report_file}")
    print(f"   2. View all: open channels_viewer.html")
    print(f"   3. Visit About pages of HIGH priority channels")
    print(f"   4. Add contact info to database")
    print(f"   5. Begin outreach!")
    
    print(f"\n✅ Fully automated workflow complete!")

if __name__ == "__main__":
    main()

