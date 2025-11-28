# Script Flow Diagrams

Visual documentation of how the YouTube creator contact extraction scripts work.

---

## 📋 Script 1: `extract_creator_contacts.py`

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         START SCRIPT                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  VIDEO_URLS = [                                                  │
│    "https://youtube.com/watch?v=...",                           │
│    "https://youtube.com/watch?v=...",                           │
│    ... (9 videos total)                                         │
│  ]                                                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   FOR EACH VIDEO URL  │
                └───────────┬───────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Function: extract_channel_info(video_url)                      │
│  ─────────────────────────────────────────────────────────       │
│  1. Run yt-dlp command:                                         │
│     yt-dlp --skip-download --dump-json [URL]                    │
│                                                                  │
│  2. Get back JSON with metadata:                                │
│     - video_id, video_title                                     │
│     - channel_name, channel_id, channel_url                     │
│     - subscriber_count, view_count                              │
│     - description (full text)                                   │
│                                                                  │
│  3. Return as Python dictionary                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Function: extract_contacts_from_description(description)       │
│  ──────────────────────────────────────────────────────────      │
│  Uses REGEX patterns to find:                                   │
│                                                                  │
│  📧 Emails:                                                      │
│     Pattern: [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}   │
│     Example: "asmalltownprepper@gmail.com"                      │
│                                                                  │
│  📸 Instagram:                                                   │
│     Pattern: instagram.com/([A-Za-z0-9._]+)                     │
│     Example: "instagram.com/cityprepping" → "cityprepping"      │
│                                                                  │
│  📘 Facebook:                                                    │
│     Pattern: facebook.com/([A-Za-z0-9._-]+)                     │
│                                                                  │
│  🐦 Twitter:                                                     │
│     Pattern: twitter.com/([A-Za-z0-9._]+)                       │
│                                                                  │
│  🎵 TikTok:                                                      │
│     Pattern: tiktok.com/@([A-Za-z0-9._]+)                       │
│                                                                  │
│  🌐 Websites:                                                    │
│     Pattern: https?://(?:www\.)?([A-Za-z0-9.-]+\.[A-Za-z]{2,}) │
│     (Excludes social media domains)                             │
│                                                                  │
│  Return: Dictionary with all found contacts                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Combine channel info + contacts                                │
│  Add to channels_data[] list                                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  REPEAT FOR NEXT URL  │
                └───────────┬───────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  All videos processed? YES                                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Function: generate_markdown_report(channels_data)              │
│  ───────────────────────────────────────────────────────         │
│  1. Sort channels:                                              │
│     - Prepper keywords? → Prepper section                       │
│     - No prepper keywords? → Other section                      │
│                                                                  │
│  2. For each channel, generate markdown:                        │
│     ### Channel Name                                            │
│     **Channel URL:** ...                                        │
│     **Subscribers:** ...                                        │
│     **Contact Information:**                                    │
│     - Email: ...                                                │
│     - Instagram: ...                                            │
│     etc.                                                        │
│                                                                  │
│  3. Add outreach templates at end                               │
│                                                                  │
│  4. Return complete markdown string                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Write to file: creator_contacts.md                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Generate CSV version                                           │
│  For each channel:                                              │
│    "Channel Name","URL","Subs","Email","Instagram",...          │
│                                                                  │
│  Write to file: creator_contacts.csv                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         END SCRIPT                               │
│  Output files:                                                  │
│  - creator_contacts.md (detailed report)                        │
│  - creator_contacts.csv (spreadsheet)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

### Detailed Function Breakdown

#### 1. `extract_channel_info(video_url)` → Dict

```python
INPUT: "https://www.youtube.com/watch?v=wnhCuYRYCdM"

PROCESS:
    ├─ Run command: yt-dlp --skip-download --dump-json [URL]
    │
    ├─ yt-dlp returns JSON like:
    │  {
    │    "id": "wnhCuYRYCdM",
    │    "title": "Every Cyber Attack Facing America",
    │    "uploader": "WIRED",
    │    "channel_id": "UCftwRNsjfRo08xYE31tkiyw",
    │    "channel_url": "https://www.youtube.com/channel/...",
    │    "channel_follower_count": 12600000,
    │    "description": "Full video description text...",
    │    "view_count": 123456,
    │    ...
    │  }
    │
    └─ Extract relevant fields

OUTPUT: 
    {
        "video_id": "wnhCuYRYCdM",
        "video_title": "Every Cyber Attack Facing America",
        "channel_name": "WIRED",
        "channel_id": "UCftwRNsjfRo08xYE31tkiyw",
        "channel_url": "https://www.youtube.com/channel/...",
        "subscriber_count": 12600000,
        "description": "Full description...",
        "view_count": 123456
    }
```

#### 2. `extract_contacts_from_description(description)` → Dict

```python
INPUT: "Follow us: instagram.com/wired, twitter.com/wired, 
        Email: contact@example.com ..."

PROCESS:
    ├─ Apply regex: email_pattern
    │  └─ Finds: ["contact@example.com"]
    │
    ├─ Apply regex: instagram_pattern
    │  └─ Finds: ["wired"]
    │
    ├─ Apply regex: twitter_pattern
    │  └─ Finds: ["wired"]
    │
    ├─ Apply regex: facebook_pattern
    │  └─ Finds: []
    │
    ├─ Apply regex: tiktok_pattern
    │  └─ Finds: []
    │
    └─ Apply regex: url_pattern (for websites)
       └─ Finds: ["example.com", "wired.com"] (excludes social)

OUTPUT:
    {
        "emails": ["contact@example.com"],
        "instagram": ["wired"],
        "facebook": [],
        "twitter": ["wired"],
        "tiktok": [],
        "websites": ["example.com", "wired.com"],
        "other_links": []
    }
```

#### 3. `generate_markdown_report(channels_data)` → String

```python
INPUT: 
    [
        {channel_1_info + contacts},
        {channel_2_info + contacts},
        ...
    ]

PROCESS:
    ├─ Categorize channels:
    │  │
    │  ├─ Has "prepper", "survival", "bug out" in name?
    │  │  └─ Add to prepper_channels[]
    │  │
    │  └─ Otherwise:
    │     └─ Add to other_channels[]
    │
    ├─ Generate markdown sections:
    │  │
    │  ├─ ## PREPPER CHANNELS
    │  │  └─ For each in prepper_channels:
    │  │      Generate formatted entry
    │  │
    │  └─ ## OTHER CHANNELS
    │     └─ For each in other_channels:
    │         Generate formatted entry
    │
    └─ Add outreach templates at end

OUTPUT: Complete markdown string (write to file)
```

---

## 🔍 Script 2: `find_more_channels.py`

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         START SCRIPT                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  SEARCH_TERMS = [                                               │
│    "prepper grid down",                                         │
│    "survival knowledge",                                        │
│    "off grid living",                                           │
│    ... (10 search terms)                                        │
│  ]                                                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ FOR EACH SEARCH TERM  │
                └───────────┬───────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Function: search_youtube(query, max_results=10)                │
│  ────────────────────────────────────────────────────────        │
│  1. Run yt-dlp command:                                         │
│     yt-dlp --skip-download --get-id --flat-playlist             │
│            "ytsearch10:prepper grid down"                       │
│                                                                  │
│  2. Returns list of video IDs:                                  │
│     ["abc123", "def456", "ghi789", ...]                         │
│                                                                  │
│  3. Convert to URLs:                                            │
│     ["https://youtube.com/watch?v=abc123", ...]                 │
│                                                                  │
│  4. Return list of 10 video URLs                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  FOR EACH VIDEO URL   │
                └───────────┬───────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Function: get_channel_info(video_url)                          │
│  ───────────────────────────────────────────────────────         │
│  1. Run yt-dlp --dump-json [URL]                                │
│  2. Extract channel metadata                                    │
│  3. Return channel dict                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Check: Is this channel already in all_channels{}?              │
│  ─────────────────────────────────────────────────              │
│  YES: Skip (avoid duplicates)                                   │
│  NO:  Add to all_channels[channel_id] = channel_info            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  NEXT VIDEO           │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  NEXT SEARCH TERM     │
                └───────────┬───────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  All searches done? YES                                         │
│  Total unique channels found: X                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Sort channels by subscriber count (high to low)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Filter for target range:                                       │
│  Keep only channels with 10,000 - 500,000 subscribers           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Generate markdown report:                                      │
│  - Summary stats                                                │
│  - Target channels (10k-500k) section                           │
│  - All channels list                                            │
│                                                                  │
│  Write to: discovered_channels.md                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Generate CSV version                                           │
│  Write to: discovered_channels.csv                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         END SCRIPT                               │
│  Output files:                                                  │
│  - discovered_channels.md                                       │
│  - discovered_channels.csv                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ How to Modify the Scripts

### Common Modifications

#### 1. **Add More Video URLs** (`extract_creator_contacts.py`)

**Location:** Lines 8-18

```python
VIDEO_URLS = [
    "https://www.youtube.com/watch?v=wnhCuYRYCdM",
    "https://www.youtube.com/watch?v=mBELXCr7wlw",
    # ... existing URLs ...
    
    # ADD YOUR NEW URLS HERE:
    "https://www.youtube.com/watch?v=YOUR_NEW_VIDEO_ID",
    "https://www.youtube.com/watch?v=ANOTHER_VIDEO_ID",
]
```

Then run: `python3 extract_creator_contacts.py`

---

#### 2. **Change Search Terms** (`find_more_channels.py`)

**Location:** Lines 11-23

```python
SEARCH_TERMS = [
    "prepper grid down",
    "survival knowledge",
    
    # ADD YOUR OWN SEARCH TERMS:
    "homesteading self reliance",
    "bushcraft survival",
    "urban survival skills",
    # etc.
]
```

---

#### 3. **Add More Regex Patterns** (extract additional contact types)

**Location:** `extract_creator_contacts.py`, function `extract_contacts_from_description()`

**Example: Add LinkedIn pattern**

```python
def extract_contacts_from_description(description: str) -> Dict[str, List[str]]:
    contacts = {
        "emails": [],
        "instagram": [],
        # ... existing fields ...
        
        "linkedin": [],  # ADD THIS
    }
    
    # ... existing patterns ...
    
    # ADD THIS PATTERN:
    linkedin_pattern = r'linkedin\.com/(?:in|company)/([A-Za-z0-9._-]+)'
    contacts["linkedin"] = list(set(re.findall(linkedin_pattern, description, re.IGNORECASE)))
    
    return contacts
```

**Then update the report generation to include LinkedIn in output.**

---

#### 4. **Change Subscriber Count Filter** (`find_more_channels.py`)

**Location:** Line ~75

```python
# Current filter: 10k-500k
target_channels = [ch for ch in sorted_channels 
                  if 10000 <= (ch['subscriber_count'] or 0) <= 500000]

# Change to different range, e.g., 5k-100k:
target_channels = [ch for ch in sorted_channels 
                  if 5000 <= (ch['subscriber_count'] or 0) <= 100000]

# Or remove filter entirely (get all):
target_channels = sorted_channels
```

---

#### 5. **Change Number of Search Results** (`find_more_channels.py`)

**Location:** Line ~57

```python
# Current: 10 results per search
video_urls = search_youtube(search_term, max_results=5)

# Change to get more results:
video_urls = search_youtube(search_term, max_results=20)

# Or change in function call
def search_youtube(query: str, max_results: int = 10)
# Change the default:         max_results: int = 20
```

---

#### 6. **Add Custom Categorization** (`extract_creator_contacts.py`)

**Location:** `generate_markdown_report()` function

```python
# Current categories: prepper_keywords
prepper_keywords = ['prepper', 'survival', 'bug out', 'ready', 'collapse', 'shtf']

# Add more categories:
prepper_keywords = ['prepper', 'survival', 'bug out', 'ready', 'collapse', 'shtf']
homestead_keywords = ['homestead', 'farm', 'garden', 'permaculture']
offgrid_keywords = ['off grid', 'solar', 'cabin', 'self sufficient']

# Then create separate sections for each category in the report
```

---

#### 7. **Export to Different Formats**

**Add JSON export:**

```python
import json

# At end of main():
json_output = {
    "channels": channels_data,
    "total_count": len(channels_data),
    "extraction_date": str(datetime.now())
}

with open("creator_contacts.json", 'w') as f:
    json.dump(json_output, f, indent=2)
```

---

## 🔧 Key Variables Reference

### `extract_creator_contacts.py`

| Variable | Type | Description | Where to Change |
|----------|------|-------------|-----------------|
| `VIDEO_URLS` | List[str] | YouTube video URLs to process | Line 8-18 |
| `prepper_keywords` | List[str] | Keywords to categorize as "prepper" | Line ~95 in `generate_markdown_report()` |
| `email_pattern` | str (regex) | Pattern to find emails | Line ~68 |
| `instagram_pattern` | str (regex) | Pattern to find Instagram handles | Line ~71 |
| Output filenames | str | `creator_contacts.md`, `creator_contacts.csv` | Line ~160, ~170 |

### `find_more_channels.py`

| Variable | Type | Description | Where to Change |
|----------|------|-------------|-----------------|
| `SEARCH_TERMS` | List[str] | YouTube search queries | Line 11-23 |
| `max_results` | int | Videos per search (default 10) | Line ~28 |
| Subscriber filter | int range | 10k-500k default | Line ~75 |
| Output filenames | str | `discovered_channels.md`, `discovered_channels.csv` | Line ~90, ~115 |

---

## 🐛 Debugging Tips

### Script Not Finding Contacts?

**Problem:** No emails/social found

**Solution:** Check the description manually
```python
# Add this after line that gets description:
print("DESCRIPTION TEXT:")
print(description)
print("=" * 50)
```

This will show you exactly what text the script is searching through.

---

### Script Errors on Specific Video?

**Problem:** Script crashes on certain URLs

**Solution:** Add error handling
```python
# Wrap in try-except:
for url in VIDEO_URLS:
    try:
        info = extract_channel_info(url)
        # ... rest of processing ...
    except Exception as e:
        print(f"ERROR processing {url}: {e}")
        continue  # Skip this one and move to next
```

---

### Want to See What yt-dlp Returns?

**Solution:** Print the raw JSON
```python
# In extract_channel_info(), after result = subprocess.run(...):
print("RAW JSON:")
print(result.stdout)
print("=" * 50)
```

---

## 📝 Quick Modification Examples

### Example 1: Only Process Small Channels (Under 100k)

In `extract_creator_contacts.py`, after extracting info:

```python
info = extract_channel_info(url)
if info:
    # ADD THIS CHECK:
    if info['subscriber_count'] and info['subscriber_count'] < 100000:
        contacts = extract_contacts_from_description(info['description'])
        info['contacts'] = contacts
        channels_data.append(info)
    else:
        print(f"  Skipping {info['channel_name']} (too large)")
```

---

### Example 2: Search for Specific Niche

In `find_more_channels.py`:

```python
SEARCH_TERMS = [
    "bushcraft survival techniques",
    "wilderness survival skills",
    "primitive technology",
    "forest camping survival",
]
```

---

### Example 3: Extract Phone Numbers

In `extract_contacts_from_description()`:

```python
contacts = {
    # ... existing fields ...
    "phone_numbers": [],
}

# Add phone pattern:
phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
contacts["phone_numbers"] = list(set(re.findall(phone_pattern, description)))
```

---

## 💡 Advanced: Pipeline Diagram

Here's how you might chain these scripts together:

```
┌──────────────────────┐
│ Start with 9 videos  │
│ (manual research)    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│ extract_creator_contacts.py  │
│ Output: creator_contacts.md  │
└──────────┬───────────────────┘
           │
           ├─────> Contact these channels
           │
           ▼
┌──────────────────────────┐
│ find_more_channels.py    │
│ Discover 50+ more        │
└──────────┬───────────────┘
           │
           ▼
┌────────────────────────────────┐
│ discovered_channels.md         │
│ Visit channel 'About' pages    │
│ Find contact info manually     │
└────────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Add new video URLs to            │
│ extract_creator_contacts.py      │
│ Run again to get their contacts  │
└──────────────────────────────────┘
```

---

## 🎯 Summary

**To modify the scripts:**

1. **Add videos:** Edit `VIDEO_URLS` list in `extract_creator_contacts.py`
2. **Change searches:** Edit `SEARCH_TERMS` list in `find_more_channels.py`
3. **Add contact types:** Add regex patterns in `extract_contacts_from_description()`
4. **Change filters:** Modify subscriber count filter (10k-500k default)
5. **Debug:** Add `print()` statements to see what data looks like

**Key files to edit:**
- `extract_creator_contacts.py` - Lines 8-18 (URLs), Lines 66-95 (regex patterns)
- `find_more_channels.py` - Lines 11-23 (searches), Line 75 (subscriber filter)

All modifications should be self-contained in these two scripts!

