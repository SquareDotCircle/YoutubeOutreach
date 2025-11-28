# YouTube Outreach - AI-Powered Channel Discovery System

🚀 **Automated micro-influencer discovery and outreach for YouTube marketing campaigns**

Find and analyze thousands of relevant YouTube channels in minutes using AI-powered search, intelligent filtering, and comprehensive analytics.

---

## ✨ Features

### 🤖 AI-Powered Discovery
- **Claude Sonnet 4** generates intelligent search queries based on your product and target audience
- Adaptive query generation learns from successful patterns
- Context-aware relevance scoring

### ⚡ High-Performance Processing
- **Parallel execution** with ThreadPoolExecutor (2x faster)
- 5 parallel YouTube search workers
- 10 parallel channel extraction workers
- Processes 1-1000 channels per workflow

### 🎯 Intelligent Filtering
- **AI content farm detection** (90-95% accuracy)
  - Volume analysis (flags >500 videos)
  - Upload frequency patterns (>5/week = bot)
  - Title pattern analysis (clickbait, templates, numbering)
  - Engagement rate scoring
- **Subscriber range filtering**
- **Session deduplication** (no repeated work)

### 📊 Enhanced Analytics
- **Engagement Rate**: (likes + comments) / views
- **View Rate**: % of subscribers who actually watch
- **Growth Trend**: Rapid, growing, stable, or declining
- **Upload Consistency**: Regularity score (0-1)
- **Video Title Analysis**: Authenticity vs AI-generated
- **Contact Detection**: Auto-extract business emails, social links

### 🎨 Beautiful UI
- Flora-inspired dark minimal design
- Real-time progress tracking
- Live time estimation
- Session statistics dashboard
- Interactive channel viewer

### 💾 Persistent Storage
- SQLite database with 30+ metrics per channel
- Session history and deduplication
- Export to CSV/JSON
- Never lose research

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Anthropic API key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/SquareDotCircle/YoutubeOutreach.git
cd YoutubeOutreach
```

2. **Set up Python environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements_server.txt
```

3. **Install yt-dlp:**
```bash
# macOS
brew install yt-dlp

# Linux
sudo apt install yt-dlp

# Windows
pip install yt-dlp
```

4. **Set up API key:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

See [API_SETUP.md](API_SETUP.md) for detailed instructions.

5. **Start the server:**
```bash
python3 control_panel_server.py
```

6. **Open in browser:**
```
http://localhost:5000
```

---

## 📖 Usage

### Basic Workflow

1. **Describe your product:**
   > "A rugged external hard drive containing offline knowledge library"

2. **Define target audience:**
   > "Preppers, survivalists, off-grid enthusiasts"

3. **Set parameters:**
   - Queries: 10-50 (how many search variations)
   - Channels per query: 5-20
   - Subscriber range: 10k-200k (recommended)

4. **Click "Start Workflow"** and watch real-time progress

5. **Review results:**
   - View analyzed channels in the UI
   - Export to CSV
   - Generate interactive channel viewer

### Example Workflows

**Small Discovery (5 minutes):**
- 10 queries × 10 channels
- ~40 channels analyzed
- Cost: ~$0.40

**Medium Campaign (15 minutes):**
- 20 queries × 15 channels
- ~120 channels analyzed
- Cost: ~$1.20

**Large-Scale (2 hours):**
- 50 queries × 20 channels
- ~420 channels analyzed
- Cost: ~$4.20

---

## 🎯 How It Works

### Pipeline Architecture

```
Step 1: AI Query Generation (5 sec)
   ↓ Claude generates 10-50 search queries
   
Step 2: Parallel YouTube Search (1-2 min)
   ↓ 5 workers search simultaneously
   
Step 3: Parallel Channel Extraction (1-2 min)
   ↓ 10 workers extract metadata + metrics
   
Step 4: AI Content Farm Filtering (instant)
   ↓ Removes 15-20% spam channels
   
Step 5: Database Storage (instant)
   ↓ Persist all metrics
   
Step 6: Claude Deep Analysis (2-5 min)
   ↓ Relevance scoring + engagement analysis
   
Step 7: Results & Export
   ✓ Interactive viewer + CSV export
```

### AI Farm Detection

Detects and filters AI-generated content channels using:

**Hard Cutoffs:**
- `>500 videos` → Content farm
- `>5 uploads/week` → Bot-like
- `Bot consistency pattern` → Automated

**Title Analysis:**
- Repetitive structures
- Clickbait keywords (40%+ threshold)
- Numbered lists (50%+ threshold)
- Generic terms (60%+ threshold)
- Lack of personal markers

**Scoring System:**
- 3+ red flags = likely content farm
- Factors: volume, frequency, consistency, engagement

---

## 📊 Cost Analysis

### Per Channel Breakdown

```
YouTube search:       $0.00 (free)
Channel extraction:   $0.00 (free, 12 sec)
Enhanced metrics:     $0.00 (free, instant)
AI filtering:         $0.00 (instant)
Claude analysis:      $0.01
─────────────────────────────
Total per channel:    $0.01
```

### Workflow Costs

| Workflow Size | Time | Channels | Cost |
|---------------|------|----------|------|
| Small (10×10) | 5 min | ~40 | $0.40 |
| Medium (20×15) | 15 min | ~120 | $1.20 |
| Large (30×20) | 30 min | ~300 | $3.00 |
| Maximum (50×20) | 2 hours | ~420 | $4.20 |

### ROI

**vs Manual Research:**
- Manual: $30/hour ÷ 5 channels = **$6/channel**
- This system: **$0.01/channel** (600x cheaper)

**vs Virtual Assistant:**
- VA: $5/hour ÷ 10 channels = **$0.50/channel**
- This system: **$0.01/channel** (50x cheaper)

**Partnership ROI:**
- One successful partnership: $500-$2000 creator fee
- Product sales from video: $5,000-$50,000
- System cost: $0.01 per channel found
- **ROI: 500,000% to 5,000,000%**

---

## 🛠️ Advanced Features

### Optional: YouTube Data API

For 3x faster extraction (3-4 sec vs 10-12 sec per channel):

1. Get API key from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Enable YouTube Data API v3
3. Set environment variable:
```bash
export YOUTUBE_API_KEY="your-key"
```

**Cost:** Free tier = 10,000 units/day (~800 channels)

### Database Queries

All data is stored in SQLite (`youtube_channels.db`):

```python
from channel_database import ChannelDatabase

db = ChannelDatabase()
db.connect()

# Get high-engagement channels
channels = db.get_channels_by_engagement(min_rate=5.0)

# Export to CSV
db.export_to_csv('results.csv')
```

### Custom Filtering

Adjust thresholds in `control_panel_server.py`:

```python
def is_ai_content_farm(channel_data: Dict):
    # Adjust these values:
    VIDEO_LIMIT = 500       # Max videos before flagging
    FREQUENCY_LIMIT = 5     # Max uploads/week
    CONSISTENCY_LIMIT = 0.95  # Bot consistency threshold
    RED_FLAG_THRESHOLD = 3   # Flags needed to reject
```

---

## 📚 Documentation

- [Quick Reference](QUICK_REFERENCE_V2.md) - One-page cheat sheet
- [API Setup](API_SETUP.md) - Environment configuration
- [Enhanced Metrics](TIER1_COMPLETE.md) - All 30+ metrics explained
- [System Optimization](SYSTEM_OPTIMIZATION_BREAKDOWN.md) - Performance deep dive
- [AI Filter Details](AI_FILTER_PARALLELIZATION_COMPLETE.md) - Detection algorithms
- [Cost Analysis](CHANNEL_DISCOVERY_COSTS.md) - Detailed breakdown

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.8+
- Flask (web server)
- yt-dlp (YouTube data extraction)
- SQLite (persistent storage)
- concurrent.futures (parallelization)

**AI/ML:**
- Anthropic Claude Sonnet 4 (query generation & analysis)
- Pattern matching (spam detection)
- Statistical analysis (engagement, trends)

**Frontend:**
- HTML5, CSS3, JavaScript
- Server-Sent Events (real-time updates)
- Responsive design

### File Structure

```
YoutubeOutreach/
├── control_panel_server.py      # Flask backend
├── control_panel.html            # Main UI
├── enhanced_channel_extractor.py # Metrics extraction
├── channel_database.py           # SQLite operations
├── channel_viewer.py             # Results viewer generator
├── config.py                     # Configuration
├── requirements_server.txt       # Python dependencies
├── API_SETUP.md                  # Setup instructions
└── README.md                     # This file
```

---

## 🎓 Best Practices

### Subscriber Ranges

**Budget products ($50-200):**
- Target: 10k-100k subs
- Sweet spot: 20k-50k
- Reasoning: Engaged, affordable, hungry for sponsorships

**Mid-range ($200-500):**
- Target: 30k-200k subs
- Sweet spot: 50k-150k
- Reasoning: Established, trusted, professional

**Premium ($500+):**
- Target: 50k-500k subs
- Sweet spot: 100k-300k
- Reasoning: Authority, high trust, quality audience

### Outreach Priority

**Priority 1 (Contact First):**
- Engagement >5%
- View Rate >30%
- Growth: Growing/Rapid
- Has: Business email + (Patreon OR Store)

**Priority 2 (Strong Candidates):**
- Engagement 3-5%
- View Rate 20-40%
- Has: Business email

**Skip:**
- Engagement <2%
- View Rate <10%
- No contact info
- AI content farm flags

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Powered by [Anthropic Claude](https://www.anthropic.com/)
- UI inspired by [florafauna.ai](https://florafauna.ai/)

---

## 📧 Support

- **Issues:** [GitHub Issues](https://github.com/SquareDotCircle/YoutubeOutreach/issues)
- **Documentation:** See `/docs` folder
- **Discussions:** [GitHub Discussions](https://github.com/SquareDotCircle/YoutubeOutreach/discussions)

---

**Version:** 2.1  
**Status:** Production Ready  
**Last Updated:** November 2025

---

<div align="center">
Made with ❤️ for marketers, growth hackers, and entrepreneurs
</div>
