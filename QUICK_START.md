# 🚀 Quick Start - 30 Seconds to Launch

## One Command Launch

```bash
cd /Users/jordanrogan/YoutubeChannels && \
source venv/bin/activate && \
python3 control_panel_server.py
```

Then open: **http://localhost:5000**

---

## What You'll See

### Control Panel (Flora-Styled Dark UI)
- Product description textarea
- Target direction textarea
- Search parameters (queries, results)
- **"Start Discovery Workflow"** button

### Real-Time Features
- Live progress log
- Status indicators
- Channel count updates
- Instant results display

---

## Example Usage

### 1. Product Description
```
A hard drive containing a comprehensive offline knowledge library 
for survival, preparedness, and self-reliance. Includes medical 
guides, technical manuals, agricultural knowledge, and essential 
information for grid-down scenarios.
```

### 2. Target Direction
```
Looking for YouTube channels focused on prepping, survival skills, 
homesteading, off-grid living, and emergency preparedness. Target 
audience: 25-55 year old preppers, survivalists, and self-reliance 
enthusiasts who value offline knowledge and disaster readiness.
```

### 3. Parameters
- Queries: 3
- Channels per query: 5
- Expected time: 2-3 minutes
- Expected results: 10-15 unique channels

---

## What Happens Next

1. AI generates 3 custom search queries
2. Searches YouTube (15 videos total)
3. Extracts channel information
4. AI analyzes each channel (relevance 0-10)
5. Shows HIGH/MEDIUM/LOW priority results
6. Updates database viewer automatically

---

## View Results

### In Control Panel
Scroll down to see relevant channels with:
- Priority badge (HIGH/MEDIUM/LOW)
- Score (X/10)
- Subscriber count
- Why relevant
- Direct channel link

### In Database Viewer
```bash
open channels_viewer.html
```
- Browse all channels
- Filter by category
- Sort by subscribers
- Search by name

---

## Important Notes

✅ Ollama must be running (`ollama serve`)  
✅ Virtual environment must be activated  
✅ Flask must be installed (`pip install -r requirements_server.txt`)

**Test everything:** `python test_system.py`

---

## Files to Know

| File | Purpose |
|------|---------|
| `control_panel_server.py` | Main server (run this) |
| `channels_viewer.html` | View all channels |
| `view_diagrams.html` | System diagrams |
| `STARTUP_GUIDE.md` | Full documentation |
| `test_system.py` | Validate installation |

---

## Keyboard Shortcuts

- `Ctrl+C` - Stop server
- `Cmd+R` - Refresh browser
- `Cmd+T` - New browser tab

---

## Pro Tips

1. **Faster Results:** Use `qwen2.5:3b` (already default)
2. **More Channels:** Increase queries to 5-10
3. **Better Quality:** Use `qwen2.5:7b` (edit control_panel_server.py)
4. **Save Results:** Results auto-save to `youtube_channels.db`

---

**Ready? Just run:**

```bash
python3 control_panel_server.py
```

**Then visit:** http://localhost:5000 🎉

