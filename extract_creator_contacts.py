#!/usr/bin/env python3
"""
YouTube Creator Contact Extractor
Extracts social media links, emails, and contact info from YouTube channels
"""

import json
import subprocess
import re
from typing import Dict, List

# YouTube video URLs from research
VIDEO_URLS = [
    "https://www.youtube.com/watch?v=wnhCuYRYCdM",  # WIRED
    "https://www.youtube.com/watch?v=mBELXCr7wlw",  # A Small Town Prepper
    "https://www.youtube.com/watch?v=ujfTEWWgy5U",  # The Ready Life
    "https://www.youtube.com/watch?v=TLm6dC34gYk",  # Big Think
    "https://www.youtube.com/watch?v=j4GTmkcU3GM",  # The Bug Out Location
    "https://www.youtube.com/watch?v=OEBVVVTNFAY",  # City Prepping
    "https://www.youtube.com/watch?v=-K6YDvA1l5I",  # Readiness Nation
    "https://www.youtube.com/watch?v=qf7_wUm1tTM",  # ESSENTIAL PREPPER
    "https://www.youtube.com/watch?v=-V1qo_tczYA",  # Fallout Raccoon
]

def extract_channel_info(video_url: str) -> Dict:
    """Extract channel information using yt-dlp"""
    print(f"Extracting info from: {video_url}")
    
    try:
        # Run yt-dlp to get JSON metadata
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--dump-json",
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Extract relevant information
        info = {
            "video_id": data.get("id", ""),
            "video_title": data.get("title", ""),
            "channel_name": data.get("uploader", ""),
            "channel_id": data.get("channel_id", ""),
            "channel_url": data.get("channel_url", ""),
            "description": data.get("description", ""),
            "subscriber_count": data.get("channel_follower_count", "Unknown"),
            "view_count": data.get("view_count", 0),
        }
        
        return info
        
    except subprocess.CalledProcessError as e:
        print(f"Error extracting {video_url}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for {video_url}: {e}")
        return None

def extract_contacts_from_description(description: str) -> Dict[str, List[str]]:
    """Extract contact information from video description"""
    contacts = {
        "emails": [],
        "instagram": [],
        "facebook": [],
        "twitter": [],
        "tiktok": [],
        "websites": [],
        "other_links": []
    }
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    contacts["emails"] = list(set(re.findall(email_pattern, description)))
    
    # Social media patterns
    instagram_pattern = r'(?:instagram\.com/|@)([A-Za-z0-9._]+)'
    contacts["instagram"] = list(set(re.findall(instagram_pattern, description, re.IGNORECASE)))
    
    facebook_pattern = r'facebook\.com/([A-Za-z0-9._-]+)'
    contacts["facebook"] = list(set(re.findall(facebook_pattern, description, re.IGNORECASE)))
    
    twitter_pattern = r'(?:twitter\.com/|@)([A-Za-z0-9._]+)'
    contacts["twitter"] = list(set(re.findall(twitter_pattern, description, re.IGNORECASE)))
    
    tiktok_pattern = r'tiktok\.com/@([A-Za-z0-9._]+)'
    contacts["tiktok"] = list(set(re.findall(tiktok_pattern, description, re.IGNORECASE)))
    
    # Website pattern (general URLs)
    url_pattern = r'https?://(?:www\.)?([A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?)'
    all_urls = re.findall(url_pattern, description)
    
    # Separate website URLs from social media
    social_domains = ['instagram.com', 'facebook.com', 'twitter.com', 'tiktok.com', 'youtube.com']
    for url in all_urls:
        if not any(domain in url.lower() for domain in social_domains):
            contacts["websites"].append(url)
    
    # Clean up duplicates and empty lists
    for key in contacts:
        contacts[key] = list(set(contacts[key]))
    
    return contacts

def generate_markdown_report(channels_data: List[Dict]) -> str:
    """Generate a markdown report with all contact information"""
    
    report = """# YouTube Creator Contact Information

## Summary
Total channels analyzed: {}

---

""".format(len(channels_data))
    
    # Sort channels by subscriber count (preppers first, then others)
    prepper_keywords = ['prepper', 'survival', 'bug out', 'ready', 'collapse', 'shtf']
    
    prepper_channels = []
    other_channels = []
    
    for channel in channels_data:
        if channel:
            channel_name_lower = channel['channel_name'].lower()
            if any(keyword in channel_name_lower for keyword in prepper_keywords):
                prepper_channels.append(channel)
            else:
                other_channels.append(channel)
    
    # Generate sections
    report += "## 🎯 PREPPER CHANNELS (Primary Targets for Collaboration)\n\n"
    report += generate_channel_sections(prepper_channels)
    
    report += "\n---\n\n## 📚 OTHER CHANNELS (Secondary Targets)\n\n"
    report += generate_channel_sections(other_channels)
    
    # Add outreach template
    report += """
---

## 📧 OUTREACH TEMPLATE

### Subject Line Options:
1. "Collaboration Opportunity: Grid-Down Knowledge Solution for Your Audience"
2. "Product Review + Affiliate Partnership Opportunity"
3. "Your subscribers need to see this offline survival library"

### Email Template:

```
Hi [CREATOR NAME],

I'm Jordan, and I've been following your content on [SPECIFIC TOPIC]. Your video on [SPECIFIC VIDEO] really resonated with me, especially [SPECIFIC POINT].

I'm launching a product that I think your audience would find incredibly valuable: an offline hard drive containing humanity's essential knowledge for grid-down scenarios. Everything from medical procedures to water purification to off-grid power systems - all accessible without internet.

I'd love to:
1. Send you a free unit to review (no strings attached)
2. Offer your audience an exclusive discount code
3. Provide a 20% affiliate commission on all sales through your link

This isn't another bug-out bag or water filter. This is the knowledge multiplier that makes all that gear actually useful when YouTube goes dark.

Would you be interested in checking it out? Happy to answer any questions.

Best regards,
Jordan

P.S. - I specifically designed the [1TB/4TB/8TB] tier with your audience in mind based on [THEIR SPECIFIC CONCERN FROM VIDEOS].
```

### Instagram DM Template:

```
Hey [NAME]! Love your content on [TOPIC]. 

Quick question - would you be interested in reviewing an offline survival knowledge drive for your audience? It's all of humanity's essential knowledge (medical, technical, agricultural) accessible without internet.

Would send you one free + 20% affiliate commission. Thought your followers would love this.

Let me know! 👍
```

### Twitter DM Template:

```
Hi [NAME], big fan of your survival/prepper content. 

Building an offline knowledge library specifically for grid-down scenarios. Would you be interested in a free review unit + affiliate partnership?

DM me if curious!
```

---

## 📊 PRIORITY RANKING

### Tier 1 (Immediate Outreach):
- Channels with 50k-500k subscribers (good engagement, not too big to ignore you)
- Clear prepper/survival focus
- Active email/social presence
- Recent video uploads (active channels)

### Tier 2 (Follow-up):
- Smaller channels (10k-50k) - often more responsive
- Adjacent niches (homesteading, off-grid, self-reliance)
- Channels with business email listed

### Tier 3 (Long-term):
- Large channels (500k+) - harder to reach but huge impact
- Mainstream channels - pivot messaging to education/digital preservation

---

## 💡 OUTREACH TIPS

1. **Personalize every message** - Reference specific videos/topics
2. **Lead with value** - Free product, no obligations
3. **Make it easy** - Provide talking points, discount codes ready
4. **Follow up** - If no response in 7 days, gentle follow-up
5. **Start small** - Get 2-3 micro-influencers first, use their testimonials
6. **Track everything** - Spreadsheet with: contact date, response, status, notes

---
"""
    
    return report

def generate_channel_sections(channels: List[Dict]) -> str:
    """Generate markdown sections for each channel"""
    sections = ""
    
    for i, channel in enumerate(channels, 1):
        if not channel:
            continue
            
        sections += f"### {i}. {channel['channel_name']}\n\n"
        sections += f"**Channel URL:** {channel['channel_url']}\n\n"
        sections += f"**Subscribers:** {channel['subscriber_count']}\n\n"
        sections += f"**Sample Video:** [{channel['video_title']}](https://youtube.com/watch?v={channel['video_id']})\n\n"
        
        # Contact information
        if channel.get('contacts'):
            contacts = channel['contacts']
            
            sections += "**Contact Information:**\n\n"
            
            if contacts['emails']:
                sections += f"- 📧 **Email:** {', '.join(contacts['emails'])}\n"
            
            if contacts['instagram']:
                instagram_links = [f"[@{handle}](https://instagram.com/{handle})" for handle in contacts['instagram']]
                sections += f"- 📸 **Instagram:** {', '.join(instagram_links)}\n"
            
            if contacts['facebook']:
                facebook_links = [f"[{handle}](https://facebook.com/{handle})" for handle in contacts['facebook']]
                sections += f"- 📘 **Facebook:** {', '.join(facebook_links)}\n"
            
            if contacts['twitter']:
                twitter_links = [f"[@{handle}](https://twitter.com/{handle})" for handle in contacts['twitter']]
                sections += f"- 🐦 **Twitter/X:** {', '.join(twitter_links)}\n"
            
            if contacts['tiktok']:
                tiktok_links = [f"[@{handle}](https://tiktok.com/@{handle})" for handle in contacts['tiktok']]
                sections += f"- 🎵 **TikTok:** {', '.join(tiktok_links)}\n"
            
            if contacts['websites']:
                sections += f"- 🌐 **Website:** {', '.join(set(contacts['websites'][:3]))}\n"  # Limit to 3
            
            if not any([contacts['emails'], contacts['instagram'], contacts['facebook'], 
                       contacts['twitter'], contacts['tiktok'], contacts['websites']]):
                sections += "- ⚠️ No direct contact info found in video description\n"
                sections += "- 💡 **Suggestion:** Use YouTube's channel page 'About' section or comment on recent videos\n"
        
        sections += "\n---\n\n"
    
    return sections

def main():
    print("🔍 YouTube Creator Contact Extractor")
    print("=" * 50)
    print(f"Analyzing {len(VIDEO_URLS)} videos...\n")
    
    channels_data = []
    
    for url in VIDEO_URLS:
        info = extract_channel_info(url)
        if info:
            # Extract contacts from description
            contacts = extract_contacts_from_description(info['description'])
            info['contacts'] = contacts
            channels_data.append(info)
            
            print(f"✓ {info['channel_name']}")
            if contacts['emails']:
                print(f"  📧 Found {len(contacts['emails'])} email(s)")
            if any([contacts['instagram'], contacts['facebook'], contacts['twitter']]):
                print(f"  📱 Found social media links")
            print()
    
    print("\n" + "=" * 50)
    print(f"✓ Successfully extracted data from {len(channels_data)} channels")
    print("\nGenerating report...")
    
    # Generate markdown report
    report = generate_markdown_report(channels_data)
    
    # Save to file
    output_file = "creator_contacts.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Report saved to: {output_file}")
    
    # Also create a CSV for easy tracking
    csv_file = "creator_contacts.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("Channel Name,Channel URL,Subscribers,Email,Instagram,Twitter,Facebook,Website\n")
        for channel in channels_data:
            if channel:
                contacts = channel['contacts']
                f.write(f'"{channel["channel_name"]}",')
                f.write(f'"{channel["channel_url"]}",')
                f.write(f'"{channel["subscriber_count"]}",')
                f.write(f'"{"; ".join(contacts["emails"])}",')
                f.write(f'"{"; ".join(contacts["instagram"])}",')
                f.write(f'"{"; ".join(contacts["twitter"])}",')
                f.write(f'"{"; ".join(contacts["facebook"])}",')
                f.write(f'"{"; ".join(contacts["websites"][:2])}"\n')
    
    print(f"✓ CSV saved to: {csv_file}")
    print("\n🎉 Done! Check the files for contact information and outreach templates.")

if __name__ == "__main__":
    main()

