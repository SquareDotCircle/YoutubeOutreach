#!/usr/bin/env python3
"""
Quick Test: 3 queries → find channels → AI analysis with logging
"""

import subprocess
import json
import requests
from datetime import datetime

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"  # Using fastest model for testing

LOG_FILE = "workflow_log.txt"

def log(message):
    """Log to file and print"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

def generate_queries():
    """Generate 3 search queries with Ollama"""
    log("🤖 Step 1: Generating search queries with AI...")
    
    prompt = """Generate 3 specific YouTube search queries for finding channels about:
- Prepper survival libraries
- Off-grid knowledge resources
- Emergency preparedness documentation

Return ONLY a JSON array: ["query 1", "query 2", "query 3"]"""
    
    try:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.8}
        }
        
        log(f"   Using model: {MODEL}")
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            text = response.json().get('response', '')
            
            # Extract JSON
            start = text.find('[')
            end = text.rfind(']') + 1
            
            if start >= 0 and end > start:
                queries = json.loads(text[start:end])
                log(f"   ✓ Generated {len(queries)} queries")
                return queries[:3]
    except Exception as e:
        log(f"   ✗ Error: {e}")
    
    # Fallback
    log("   ⚠️ Using fallback queries")
    return [
        "survival knowledge library",
        "prepper offline resources",
        "grid down information"
    ]

def search_youtube(query):
    """Search YouTube"""
    log(f"\n🔍 Searching YouTube: '{query}'")
    
    try:
        cmd = ['yt-dlp', '--skip-download', '--get-id', '--flat-playlist', f'ytsearch3:{query}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            video_ids = [v for v in result.stdout.strip().split('\n') if v]
            log(f"   ✓ Found {len(video_ids)} videos")
            return [f'https://www.youtube.com/watch?v={v}' for v in video_ids]
    except Exception as e:
        log(f"   ✗ Error: {e}")
    
    return []

def get_channel_info(video_url):
    """Get channel info"""
    try:
        cmd = ['yt-dlp', '--skip-download', '--dump-json', video_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                'channel_id': data.get('channel_id', ''),
                'channel_name': data.get('uploader', ''),
                'channel_url': data.get('channel_url', ''),
                'subscriber_count': data.get('channel_follower_count', 0),
                'description': data.get('description', '')[:500]
            }
    except:
        pass
    
    return None

def analyze_channel(channel_data):
    """Analyze channel with Ollama"""
    name = channel_data['channel_name']
    log(f"\n🤖 Analyzing: {name}")
    
    prompt = f"""Analyze this YouTube channel for selling offline survival knowledge libraries.

Channel: {channel_data['channel_name']}
Subscribers: {channel_data['subscriber_count']:,}
Description: {channel_data.get('description', 'None')[:300]}

Is this relevant for our product (offline prep knowledge drive)?

Respond with ONLY this JSON:
{{"relevant": true|false, "score": X, "reason": "brief explanation", "priority": "low|medium|high"}}"""
    
    try:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            text = response.json().get('response', '')
            
            # Extract JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0:
                analysis = json.loads(text[start:end])
                score = analysis.get('score', 0)
                relevant = "✓" if analysis.get('relevant', False) else "✗"
                log(f"   {relevant} Score: {score}/10 - {analysis.get('reason', 'N/A')[:50]}...")
                return analysis
    except Exception as e:
        log(f"   ✗ Error: {e}")
    
    return {"relevant": False, "score": 0, "reason": "Analysis failed"}

def main():
    # Clear log file
    with open(LOG_FILE, 'w') as f:
        f.write(f"=== Workflow Started: {datetime.now()} ===\n\n")
    
    log("🚀 AUTOMATED AI WORKFLOW TEST")
    log("=" * 60)
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code != 200:
            log("❌ Ollama not running! Start it: ollama serve")
            return
    except:
        log("❌ Ollama not running! Start it: ollama serve")
        return
    
    log("✓ Ollama is running")
    
    # Step 1: Generate queries
    log("\n" + "=" * 60)
    log("STEP 1: AI Generate Search Queries")
    log("=" * 60)
    
    queries = generate_queries()
    
    log("\n✨ AI-Generated Queries:")
    for i, q in enumerate(queries, 1):
        log(f"   {i}. {q}")
    
    # Step 2: Search YouTube
    log("\n" + "=" * 60)
    log("STEP 2: Search YouTube")
    log("=" * 60)
    
    all_channels = {}
    
    for query in queries:
        video_urls = search_youtube(query)
        
        for url in video_urls:
            log(f"   📡 Fetching channel info...")
            channel_info = get_channel_info(url)
            
            if channel_info:
                channel_id = channel_info['channel_id']
                if channel_id not in all_channels:
                    all_channels[channel_id] = channel_info
                    log(f"   ✓ {channel_info['channel_name']} ({channel_info['subscriber_count']:,} subs)")
                else:
                    log(f"   ⏭️  Duplicate (skipped)")
    
    log(f"\n✓ Total unique channels: {len(all_channels)}")
    
    if not all_channels:
        log("❌ No channels found. Exiting.")
        return
    
    # Step 3: AI Analysis
    log("\n" + "=" * 60)
    log("STEP 3: AI Analyze Each Channel")
    log("=" * 60)
    
    results = []
    
    for i, (channel_id, channel_data) in enumerate(all_channels.items(), 1):
        log(f"\n[{i}/{len(all_channels)}] ----------------------")
        analysis = analyze_channel(channel_data)
        
        results.append({
            'channel': channel_data,
            'analysis': analysis
        })
    
    # Summary
    relevant = [r for r in results if r['analysis'].get('relevant', False)]
    
    log("\n" + "=" * 60)
    log("🎉 RESULTS")
    log("=" * 60)
    
    log(f"\nTotal Found: {len(results)}")
    log(f"✅ Relevant: {len(relevant)}")
    log(f"❌ Not Relevant: {len(results) - len(relevant)}")
    
    if relevant:
        log("\n🎯 RELEVANT CHANNELS:\n")
        
        relevant.sort(key=lambda x: x['analysis'].get('score', 0), reverse=True)
        
        for r in relevant:
            ch = r['channel']
            an = r['analysis']
            log(f"   {an.get('priority', 'N/A').upper()} | {an.get('score', 0)}/10 | {ch['channel_name']}")
            log(f"        Subs: {ch['subscriber_count']:,}")
            log(f"        URL: {ch['channel_url']}/about")
            log(f"        → {an.get('reason', 'N/A')}")
            log("")
    
    # Save JSON results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    log(f"✓ Results saved to test_results.json")
    log(f"✓ Full log saved to {LOG_FILE}")
    
    log("\n✅ Test complete!")
    log("\nView log: cat workflow_log.txt")
    log("View results: cat test_results.json")

if __name__ == "__main__":
    main()

