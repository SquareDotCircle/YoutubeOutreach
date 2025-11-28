# 🚀 Channel Discovery System - Startup Guide

## Quick Start (3 Steps)

### 1. Ensure Ollama is Running

```bash
ollama serve
```

Leave this terminal open. In a new terminal:

```bash
ollama pull qwen2.5:3b
```

### 2. Install Flask Dependencies

```bash
cd /Users/jordanrogan/YoutubeChannels
source venv/bin/activate
pip install -r requirements_server.txt
```

### 3. Start the Control Panel Server

```bash
python3 control_panel_server.py
```

Then open your browser to:
**http://localhost:5000**

---

## System Features

### 🎨 Flora-Inspired Modern UI
- Dark, minimal design aesthetic
- Sharp corners, subtle shadows
- Professional spacing and typography
- Clean, tool-focused interface

### 🎯 Control Panel (`http://localhost:5000`)
- Define your product and target audience
- AI generates custom search queries
- Real-time progress updates
- View results as they're analyzed

### 📊 Database Viewer (`channels_viewer.html`)
- Browse all discovered channels
- Filter by category and search
- Sort by subscribers or name
- Direct links to channels and contact info

### 📈 Flow Diagrams (`view_diagrams.html`)
- Interactive Mermaid diagrams
- Visual workflow representation
- System architecture overview

---

## How It Works

### Step 1: Define Your Product
In the control panel, describe:
- What you're selling
- Your target audience
- Channel characteristics you want

### Step 2: AI Generates Queries
The system uses Ollama to create targeted YouTube search terms based on your input.

### Step 3: Discover Channels
For each query:
- Searches YouTube
- Extracts channel information
- Removes duplicates
- Saves to SQLite database

### Step 4: AI Analysis
Each channel is analyzed for:
- Relevance to your product
- Audience match
- Engagement potential
- Overall score (0-10)

### Step 5: Review Results
- High-priority channels (8-10/10)
- Medium-priority channels (5-7/10)
- Low-priority channels (0-4/10)

---

## File Structure

```
YoutubeChannels/
├── control_panel.html          # Main UI
├── control_panel_server.py     # Flask backend
├── automated_workflow.py       # Core workflow logic
├── channel_viewer.py           # Database viewer generator
├── channels_viewer.html        # Generated database view
├── view_diagrams.html          # System diagrams
├── channel_database.py         # Database management
├── channels.db                 # SQLite database
├── venv/                       # Python environment
└── requirements_server.txt     # Flask dependencies
```

---

## Customization

### Change Product Context
Edit the default values in `automated_workflow.py`:
- `product_context` (line 49-51)
- `target_direction` (line 53-55)

### Adjust AI Model
Change `DEFAULT_MODEL` in:
- `control_panel_server.py` (line 17)
- `automated_workflow.py` (line 17)

Available models:
- `qwen2.5:3b` (fast, good quality)
- `qwen2.5:7b` (slower, better quality)
- `llama3.2` (alternative)

### Modify Search Parameters
In the control panel form:
- Number of queries: 1-10
- Channels per query: 1-10

---

## Troubleshooting

### Ollama Not Running
```
❌ Ollama server not running!
```
**Solution:** Start Ollama in a separate terminal:
```bash
ollama serve
```

### Flask Import Error
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Install dependencies:
```bash
source venv/bin/activate
pip install -r requirements_server.txt
```

### Port Already in Use
```
Address already in use
```
**Solution:** Kill the existing process or change the port in `control_panel_server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

### Database Locked
```
database is locked
```
**Solution:** Close any other scripts accessing the database, then retry.

---

## Performance Tips

### Speed Up Analysis
1. Use `qwen2.5:3b` instead of `7b` (3x faster)
2. Reduce channels per query (3 instead of 5)
3. Run multiple workflows in parallel (separate terminals)

### Improve Results Quality
1. Use `qwen2.5:7b` for better analysis
2. Be specific in product description
3. Include detailed target audience info
4. Iterate: refine queries based on initial results

---

## Next Steps After Discovery

1. **Review Results** - Open channels_viewer.html
2. **Visit About Pages** - Check high-priority channels
3. **Extract Contacts** - Find emails, social media
4. **Update Database** - Add contact info manually
5. **Begin Outreach** - Use outreach_tracker.csv

---

## Advanced Usage

### Run Workflow from Command Line
```bash
# With custom context
python3 automated_workflow.py
```

### Batch Process Multiple Products
Create separate database files:
```python
# In channel_database.py, change:
DATABASE_FILE = 'products/product1.db'
```

### Export Results to CSV
```bash
sqlite3 channels.db
.headers on
.mode csv
.output results.csv
SELECT * FROM channels WHERE category='ai_discovered';
.quit
```

---

## Support & Documentation

- **System Diagrams:** Open `view_diagrams.html` in browser
- **Database Schema:** See `channel_database.py`
- **API Reference:** See `control_panel_server.py`

---

**Built with:** Python, Flask, Ollama, SQLite, yt-dlp, Mermaid

**Design inspired by:** [Flora.fauna.ai](https://www.florafauna.ai/)

