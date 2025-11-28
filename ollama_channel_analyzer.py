#!/usr/bin/env python3
"""
Ollama-Powered Channel Relevance Analyzer
Fetches channel About pages and uses LLM to determine if they're relevant for outreach
"""

import json
import requests
import subprocess
from typing import Dict, List, Optional
from channel_database import ChannelDatabase

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "mistral:7b-instruct"  # Using your installed model

def check_ollama_available() -> bool:
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def generate_with_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Generate text using Ollama"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temp for more consistent analysis
                "top_p": 0.9
            }
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=90)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', '')
    except Exception as e:
        print(f"Error calling Ollama: {e}")
    
    return ""

def fetch_channel_about(channel_url: str) -> Optional[Dict]:
    """Fetch channel information using yt-dlp"""
    try:
        # Get channel info
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--dump-json',
            '--playlist-items', '1',  # Just get one video for channel info
            f"{channel_url}/videos"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            return {
                'channel_id': data.get('channel_id', ''),
                'channel_name': data.get('channel', ''),
                'description': data.get('description', ''),
                'channel_url': data.get('channel_url', ''),
                'subscriber_count': data.get('channel_follower_count', 0),
                'tags': data.get('tags', []),
                'categories': data.get('categories', [])
            }
    except Exception as e:
        print(f"Error fetching channel: {e}")
    
    return None

def analyze_channel_relevance(channel_data: Dict, model: str = DEFAULT_MODEL) -> Dict:
    """Analyze if a channel is relevant for prepper/survival outreach"""
    
    channel_name = channel_data.get('channel_name', 'Unknown')
    description = channel_data.get('description', '')[:1000]  # Limit length
    tags = channel_data.get('tags', [])[:20]
    categories = channel_data.get('categories', [])
    subs = channel_data.get('subscriber_count', 0)
    
    prompt = f"""Analyze this YouTube channel to determine if it's relevant for a product about offline survival knowledge libraries.

CHANNEL INFO:
Name: {channel_name}
Subscribers: {subs:,}
Categories: {', '.join(categories) if categories else 'Unknown'}
Tags: {', '.join(tags[:10]) if tags else 'None'}

DESCRIPTION:
{description if description else 'No description available'}

PRODUCT CONTEXT:
We're selling hard drives containing humanity's essential knowledge for grid-down scenarios (medical info, survival skills, technical manuals, etc.). Target audience: preppers, survivalists, homesteaders, off-grid enthusiasts.

ANALYSIS REQUIRED:
Determine if this channel is a good fit for:
1. Product review/promotion
2. Affiliate partnership
3. Audience alignment

Rate the channel:
- Relevance (0-10): How relevant to prepping/survival/self-reliance?
- Audience Match (0-10): How well does their audience match our target?
- Engagement Potential (0-10): Likelihood they'd engage with our product?
- Priority (low/medium/high): Outreach priority

Respond with ONLY this JSON (no extra text):
{{
  "relevance_score": X,
  "audience_match_score": X,
  "engagement_score": X,
  "overall_score": X,
  "priority": "low|medium|high",
  "relevant": true|false,
  "reason": "Brief explanation why relevant or not",
  "suggested_pitch": "How to pitch the product to this channel (if relevant)",
  "red_flags": ["any concerns"],
  "positive_signals": ["why they're a good fit"]
}}"""

    print(f"  🤖 Analyzing {channel_name}...", end=' ')
    
    response = generate_with_ollama(prompt, model)
    
    if not response:
        print("❌ Failed")
        return {"relevant": False, "reason": "Analysis failed"}
    
    try:
        # Extract JSON from response
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start >= 0 and end > start:
            json_str = response[start:end]
            analysis = json.loads(json_str)
            
            # Validate required fields
            if 'relevant' in analysis and 'reason' in analysis:
                score = analysis.get('overall_score', 0)
                print(f"✓ Score: {score}/10")
                return analysis
    except Exception as e:
        print(f"⚠️ Parse error: {e}")
    
    print("⚠️ Invalid response")
    return {"relevant": False, "reason": "Could not parse analysis"}

def batch_analyze_channels(channel_ids: List[str], model: str = DEFAULT_MODEL) -> List[Dict]:
    """Analyze multiple channels"""
    results = []
    
    db = ChannelDatabase()
    db.connect()
    
    for i, channel_id in enumerate(channel_ids, 1):
        print(f"\n[{i}/{len(channel_ids)}] Processing channel...")
        
        # Get channel from database
        channel = db.get_channel(channel_id)
        if not channel:
            print(f"  ⚠️ Channel {channel_id} not in database")
            continue
        
        channel_url = channel['channel_url']
        
        # Fetch additional info
        print(f"  📡 Fetching channel data...")
        about_data = fetch_channel_about(channel_url)
        
        if about_data:
            # Merge with database data
            combined_data = {**channel, **about_data}
        else:
            combined_data = channel
            combined_data['description'] = combined_data.get('notes', '')
        
        # Analyze relevance
        analysis = analyze_channel_relevance(combined_data, model)
        
        # Store results
        result = {
            'channel_id': channel_id,
            'channel_name': channel['channel_name'],
            'channel_url': channel_url,
            'subscriber_count': channel['subscriber_count'],
            'analysis': analysis
        }
        
        results.append(result)
        
        # Update database with analysis
        if analysis.get('relevant'):
            priority = analysis.get('priority', 'medium')
            reason = analysis.get('reason', '')
            db.cursor.execute('''
                UPDATE channels 
                SET notes = ?
                WHERE channel_id = ?
            ''', (f"Priority: {priority} - {reason}", channel_id))
            db.conn.commit()
    
    db.close()
    return results

def generate_report(results: List[Dict], output_file: str = 'channel_analysis_report.md'):
    """Generate a markdown report of analysis results"""
    
    # Sort by relevance
    relevant = [r for r in results if r['analysis'].get('relevant', False)]
    not_relevant = [r for r in results if not r['analysis'].get('relevant', False)]
    
    # Sort relevant by overall score
    relevant.sort(key=lambda x: x['analysis'].get('overall_score', 0), reverse=True)
    
    report = f"""# Channel Relevance Analysis Report

## Summary
- Total Channels Analyzed: {len(results)}
- Relevant Channels: {len(relevant)}
- Not Relevant: {len(not_relevant)}

---

## 🎯 Relevant Channels (Recommended for Outreach)

"""
    
    for i, result in enumerate(relevant, 1):
        analysis = result['analysis']
        subs = result['subscriber_count']
        
        report += f"""### {i}. {result['channel_name']}

**Channel:** {result['channel_url']}
**Subscribers:** {subs:,}

**Scores:**
- Relevance: {analysis.get('relevance_score', 'N/A')}/10
- Audience Match: {analysis.get('audience_match_score', 'N/A')}/10
- Engagement Potential: {analysis.get('engagement_score', 'N/A')}/10
- **Overall: {analysis.get('overall_score', 'N/A')}/10**

**Priority:** {analysis.get('priority', 'Unknown').upper()}

**Why Relevant:**
{analysis.get('reason', 'No reason provided')}

**Positive Signals:**
{chr(10).join(f'- {signal}' for signal in analysis.get('positive_signals', ['None noted']))}

**Suggested Pitch:**
{analysis.get('suggested_pitch', 'No suggestion provided')}

**Red Flags:**
{chr(10).join(f'- {flag}' for flag in analysis.get('red_flags', ['None'])) if analysis.get('red_flags') else 'None'}

---

"""
    
    report += "\n## ❌ Not Relevant Channels\n\n"
    
    for result in not_relevant[:10]:  # Show first 10
        analysis = result['analysis']
        report += f"- **{result['channel_name']}** ({result['subscriber_count']:,} subs): {analysis.get('reason', 'Not a good fit')}\n"
    
    if len(not_relevant) > 10:
        report += f"\n...and {len(not_relevant) - 10} more\n"
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✓ Report saved to {output_file}")
    
    return report

def main():
    """Main function"""
    import sys
    
    print("🤖 Ollama-Powered Channel Relevance Analyzer")
    print("=" * 60)
    
    # Check Ollama
    if not check_ollama_available():
        print("❌ Ollama is not running!")
        print("\n💡 To start Ollama:")
        print("   1. Install: brew install ollama")
        print("   2. Start: ollama serve")
        print("   3. Pull model: ollama pull llama3.2")
        return
    
    print("✓ Ollama server is running")
    
    # Connect to database
    db = ChannelDatabase()
    db.connect()
    
    # Get channels to analyze
    print("\n📊 Fetching channels from database...")
    
    # Get target range channels (most promising)
    channels = db.get_channels_by_subscriber_range(10000, 500000)
    
    if not channels:
        print("❌ No channels in target range (10k-500k subs)")
        print("   Run find_more_channels.py first")
        db.close()
        return
    
    print(f"✓ Found {len(channels)} channels in target range")
    
    # Let user choose how many to analyze
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            channels = channels[:limit]
        except:
            pass
    else:
        limit = min(10, len(channels))
        channels = channels[:limit]
        print(f"  Analyzing first {limit} channels (pass number as argument for more)")
    
    channel_ids = [c['channel_id'] for c in channels]
    
    db.close()
    
    # Analyze channels
    print(f"\n🎯 Analyzing {len(channel_ids)} channels...")
    print("⏳ This will take a few minutes...\n")
    
    results = batch_analyze_channels(channel_ids)
    
    # Generate report
    print("\n📝 Generating report...")
    generate_report(results)
    
    # Show summary
    relevant = [r for r in results if r['analysis'].get('relevant', False)]
    high_priority = [r for r in relevant if r['analysis'].get('priority') == 'high']
    
    print("\n" + "=" * 60)
    print(f"✅ Analysis Complete!")
    print(f"\n📊 Results:")
    print(f"  Total Analyzed: {len(results)}")
    print(f"  Relevant: {len(relevant)}")
    print(f"  High Priority: {len(high_priority)}")
    
    if high_priority:
        print(f"\n🎯 Top Recommendations:")
        for result in high_priority[:5]:
            score = result['analysis'].get('overall_score', 0)
            subs = result['subscriber_count']
            print(f"  - {result['channel_name']} ({subs:,} subs, score: {score}/10)")
    
    print(f"\n📄 Full report: channel_analysis_report.md")
    print("\n💡 Next steps:")
    print("   1. Review channel_analysis_report.md")
    print("   2. Visit high-priority channels' About pages")
    print("   3. Add contact info to database")
    print("   4. Begin outreach!")

if __name__ == "__main__":
    main()

