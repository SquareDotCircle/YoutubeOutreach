<!-- a84f9065-562d-4efc-9b87-795af4feb050 e353c56c-5790-432a-8a6b-78a8ccad7d7d -->
# AI Content Farm Filter & Parallelization Implementation

## Overview

Add aggressive AI farm detection (metrics + title patterns) and parallelize bottleneck operations to achieve 3-4x speed improvement while filtering 90-95% of spam channels.

## Changes Required

### 1. Add Title Analysis Function to `enhanced_channel_extractor.py`

Add new function to extract and store video titles:

```python
def get_video_details(video_url: str) -> Optional[Dict]:
    # Modify existing function to also capture title
    return {
        'view_count': data.get('view_count', 0),
        'like_count': data.get('like_count', 0),
        'comment_count': data.get('comment_count', 0),
        'duration': data.get('duration', 0),
        'upload_date': data.get('upload_date'),
        'title': data.get('title', '')  # ADD THIS
    }
```

Add title pattern detection function (new):

```python
def analyze_title_patterns(titles: List[str]) -> tuple[bool, float, str]:
    """
    Detect AI-generated content based on title patterns
    Returns: (is_spam, spam_score, reason)
    """
    # Check for: repetitive structure, clickbait, numbered lists,
    # generic terms, serialization, lack of personal markers
    # Threshold: spam_score >= 6 = AI farm
```

Store titles in enhanced data:

```python
def get_enhanced_channel_data():
    # After getting detailed_videos
    enhanced_data['recent_titles'] = [v.get('title', '') for v in detailed_videos]
```

### 2. Add AI Farm Detection to `control_panel_server.py`

Add comprehensive detection function (new):

```python
def is_ai_content_farm(channel_data: Dict) -> tuple[bool, str]:
    """
    Aggressive AI content farm detection
    Checks: volume (>500), frequency (>5/week), consistency (>0.95),
           engagement (<1%), title patterns (score>=6)
    """
    # Hard cutoffs
    if total_videos > 500: return True, "Content farm (>500 videos)"
    if upload_freq > 5: return True, "Bot frequency (>5/week)"
    if consistency > 0.95 and total_videos > 200: return True, "Bot pattern"
    
    # Title analysis
    if 'recent_titles' in channel_data:
        is_spam, score, reason = analyze_title_patterns(channel_data['recent_titles'])
        if is_spam: return True, f"Spam titles ({reason})"
    
    # Scoring system for edge cases
    # Return True if red_flags >= 3
```

### 3. Replace Pre-Filter in `workflow_generator()`

**Remove**: Existing `quick_filter_channel()` calls (lines ~475-490)

**Add**: New filtering stage after enhanced extraction:

```python
# After enhanced extraction completes (around line 466)
# NEW Stage: AI Content Farm Detection
yield {'type': 'log', 'message': '\n🤖 Step 3: Filtering AI content farms...'}

real_creators = []
ai_farm_count = 0

for channel_id, channel in all_channels.items():
    is_farm, reason = is_ai_content_farm(channel)
    if is_farm:
        ai_farm_count += 1
        yield {'type': 'log', 'message': f'    ⏭️ {channel["channel_name"]} - {reason}'}
    else:
        real_creators.append(channel)

yield {'type': 'log', 'message': f'✓ Filtered {ai_farm_count} AI farms, {len(real_creators)} real creators'}

# Update step numbering: Database save becomes Step 4, Analysis becomes Step 5
```

### 4. Add Parallelization

Add imports at top of `control_panel_server.py`:

```python
import concurrent.futures
from functools import partial
```

Parallelize YouTube searches (in `workflow_generator`):

```python
# Replace sequential search loop (lines 425-428)
yield {'type': 'log', 'message': 'Searching in parallel...'}

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    search_func = partial(search_youtube, max_results=results_per_query)
    search_results = executor.map(search_func, queries)
    
all_video_urls = []
for query, video_urls in zip(queries, search_results):
    yield {'type': 'log', 'message': f'  ✓ "{query}" - {len(video_urls)} videos'}
    all_video_urls.extend(video_urls)
```

Parallelize channel info extraction:

```python
# Replace sequential channel extraction loop (lines 430-466)
yield {'type': 'log', 'message': 'Extracting channel info in parallel...'}

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    channel_infos = list(executor.map(get_channel_info, all_video_urls))

# Filter and process results
for channel_info in channel_infos:
    if not channel_info: continue
    # Apply subscriber filter, deduplication
    # Then extract enhanced data (still sequential for now)
```

### 5. Update Step Numbers in UI Messages

After adding AI filter stage, renumber:

- Database save: Step 3 → Step 4
- Claude analysis: Step 4 → Step 5

## Files Modified

1. `/Users/jordanrogan/YoutubeChannels/enhanced_channel_extractor.py`

   - Modify `get_video_details()` to capture titles
   - Add `analyze_title_patterns()` function
   - Update `get_enhanced_channel_data()` to store titles

2. `/Users/jordanrogan/YoutubeChannels/control_panel_server.py`

   - Add imports: `concurrent.futures`, `partial`
   - Add `is_ai_content_farm()` function
   - Remove `quick_filter_channel()` usage
   - Parallelize YouTube searches
   - Parallelize channel extraction
   - Add AI farm filtering stage
   - Update step numbering

## Expected Results

**Performance:**

- YouTube search: 3-5 min → 1-2 min (parallel)
- Channel extraction: 4-7 min → 1-2 min (parallel)
- Total workflow: 11-15 min → 5-7 min (50% faster)

**Quality:**

- AI farm detection: 90-95% caught
- False positives: <5% (aggressive but tuned)
- Final channels: 8-10 real creators per workflow

**Cost:**

- Same ($0.12 per workflow)
- Better quality = higher ROI

### To-dos

- [ ] Modify get_video_details() to capture video titles
- [ ] Add analyze_title_patterns() function for spam detection
- [ ] Add is_ai_content_farm() with aggressive thresholds
- [ ] Parallelize YouTube searches with ThreadPoolExecutor
- [ ] Parallelize channel info extraction
- [ ] Replace quick_filter_channel with AI farm detection
- [ ] Update workflow step numbering in UI messages
- [ ] Test complete workflow with new filtering and parallelization