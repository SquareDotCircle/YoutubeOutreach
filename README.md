# YouTube Creator Outreach Tools

This folder contains automated tools and research for your "Grid-Down Knowledge Drive" product launch and creator collaboration strategy.

## 📁 Files Overview

### Research & Strategy Documents

1. **`knowledge_drive_research.md`** - Your complete market research
   - Analysis of 9 prepper/survival YouTube videos
   - Market validation and target customer segments
   - Product positioning and pricing strategy
   - Marketing hooks and messaging
   - Content curation priorities

2. **`action_plan.md`** - Step-by-step execution roadmap
   - Week-by-week action items
   - Financial projections and break-even analysis
   - Risk mitigation strategies
   - Decision frameworks

### Creator Contact Information

3. **`creator_contacts.md`** - Full contact report for the 9 channels you researched
   - Email addresses found
   - Social media profiles (Instagram, Twitter, Facebook, TikTok)
   - Website URLs
   - Outreach templates (email, DM, Twitter)
   - Priority rankings

4. **`creator_contacts.csv`** - Same data in spreadsheet format
   - Easy to import into CRM or spreadsheet
   - Quick reference for contact info

5. **`outreach_tracker.csv`** - Your outreach management system
   - Pre-populated with priority channels
   - Columns for: contact date, response status, follow-ups, notes
   - **ACTION ITEM:** Open this in Excel/Google Sheets to track your outreach efforts

### Automation Scripts

6. **`extract_creator_contacts.py`** - Automated contact extractor
   - Input: YouTube video URLs
   - Output: Contact information, social media, emails
   - Already run for your 9 videos, but can be used for new channels

7. **`find_more_channels.py`** - YouTube channel discovery tool
   - Searches YouTube for prepper/survival content
   - Identifies channels in your target size range (10k-500k subs)
   - Generates list of potential collaboration partners
   - **Run when ready:** `python3 find_more_channels.py`

---

## 🚀 Quick Start Guide

### Phase 1: Review Your Research (TODAY)

1. Open `knowledge_drive_research.md` and read through it
2. Review the "Key Insights" and "Recommended Strategy" sections
3. Decide: Am I doing this? (It's okay if not!)

### Phase 2: If Yes, Test Demand (THIS WEEK)

1. Create a simple landing page with product description
2. Use the marketing hooks from `knowledge_drive_research.md`
3. Run a small YouTube ad test ($200-500)
4. Goal: 50+ email signups or 10+ pre-orders = green light

### Phase 3: Begin Creator Outreach (WEEK 2-3)

1. Open `outreach_tracker.csv` in Excel/Google Sheets
2. Start with Tier 1 channels (50k-500k subscribers):
   - **The Ready Life** (58k subs) - thereadylife.com
   - **The Bug Out Location** (72k subs) - thebugoutlocation.net
   - **Fallout Raccoon** (49k subs) - check YouTube About page

3. Use the email template from `creator_contacts.md`
4. **Personalize each message** (reference specific videos)
5. Update `outreach_tracker.csv` as you go

### Phase 4: Discover More Channels (ONGOING)

Run the channel finder script:
```bash
python3 find_more_channels.py
```

This will:
- Search YouTube for relevant prepper/survival content
- Find 50+ additional channels in your target range
- Generate `discovered_channels.md` with details
- Give you a much larger outreach list

---

## 📊 Priority Outreach List

Based on the research, here's your immediate action priority:

### ✅ IMMEDIATE (This Week)

1. **The Ready Life** (58k subs)
   - Why: Perfect size, "90-day survival" focus aligns with your product
   - Contact: thereadylife.com (find contact page)
   - Reference: Congressman Bartlett grid-down video

2. **The Bug Out Location** (72k subs)
   - Why: Active channel, "2026 Prepper Checklist" - your product fits perfectly
   - Contact: thebugoutlocation.net
   - Reference: 15 critical items video

3. **Fallout Raccoon** (49k subs)
   - Why: "Knowledge as force multiplier" aligns PERFECTLY with your messaging
   - Contact: Check YouTube About page
   - Reference: 7 Tools survival video

### 📅 FOLLOW-UP (Next Week)

4. **A Small Town Prepper** (16k subs)
   - Why: Has direct email, smaller channel = more responsive
   - Contact: asmalltownprepper@gmail.com
   - Reference: Prepper Blacklist video (mention your drive is "untracked")

5. **ESSENTIAL PREPPER** (31k subs)
   - Why: "90 Days No Power" is EXACTLY your use case
   - Contact: YouTube About page or recent video comments
   - Reference: 90-day blackout video

6. **Readiness Nation** (5.6k subs)
   - Why: Small but engaged, critical of mainstream advice
   - Contact: @readiness_nation on Instagram
   - Reference: CIA preparedness critique video

### 🎯 STRETCH GOALS (Month 2)

7. **City Prepping** (1.2M subs)
   - Why: Huge reach, but might be hard to reach
   - Contact: @cityprepping on Instagram
   - Try: Instagram DM or comment on recent videos first

---

## 📧 Outreach Best Practices

### DO:
✅ Personalize every message (reference specific videos)
✅ Lead with value (free product, no strings)
✅ Make it easy (provide discount codes, talking points)
✅ Follow up after 7 days if no response
✅ Start with 2-3 smaller channels to get testimonials
✅ Track everything in `outreach_tracker.csv`

### DON'T:
❌ Send generic copy-paste messages
❌ Be pushy or desperate
❌ Contact huge channels first (City Prepping, WIRED)
❌ Expect immediate responses
❌ Give up after one no-response
❌ Forget to update your tracker

---

## 🛠️ Using the Automation Scripts

### Extract Contacts from New Videos

If you find new YouTube videos/channels:

```bash
# Edit extract_creator_contacts.py and add new video URLs to the VIDEO_URLS list
# Then run:
python3 extract_creator_contacts.py
```

It will generate updated `creator_contacts.md` and `creator_contacts.csv` files.

### Discover More Channels

To find 50+ more potential collaboration partners:

```bash
python3 find_more_channels.py
```

This will take 5-10 minutes to run and will generate:
- `discovered_channels.md` - Full report with details
- `discovered_channels.csv` - Spreadsheet format

You can then manually visit each channel's "About" page to find contact information.

### Modify Search Terms

Edit `find_more_channels.py` and change the `SEARCH_TERMS` list:

```python
SEARCH_TERMS = [
    "your custom search",
    "another search term",
    # etc.
]
```

---

## 💡 Pro Tips

### Getting Contact Info When Not Listed

Many channels don't list contact info in video descriptions. Here's how to find it:

1. **YouTube Channel "About" Tab**
   - Click channel name → "About" tab
   - Look for "Business inquiries" email
   - Some channels hide it until you're logged in

2. **Check Their Website**
   - Most prepper channels have websites
   - Look for "Contact" or "Advertise" pages
   - Sometimes hidden in footer

3. **Social Media DMs**
   - Instagram DMs often get responses
   - Twitter DMs (if open)
   - Be professional and brief

4. **Comment on Recent Videos**
   - "Love your content! Do you have a business email?"
   - Creators often reply to genuine comments
   - Don't pitch in comments, just ask for contact method

5. **Patreon/Locals/Membership Pages**
   - Check if they have premium membership platforms
   - Often list contact info for business inquiries

### Best Time to Reach Out

- **Avoid Mondays** (creators catching up from weekend)
- **Tuesday-Thursday mornings** are best
- **After they post a video** (they're actively checking responses)
- **NOT right before/after major events** (holidays, disasters, etc.)

### What to Send First

**Free Drive > Pitch**

Don't ask if they want to promote it. Just say:
"I'm sending you a free unit. No obligations. If you like it, great. If not, keep it anyway."

This is way more effective than asking permission.

---

## 📈 Tracking Your Success

Update `outreach_tracker.csv` with:

- **Date Contacted** - When you sent the first message
- **Response Received** - Yes/No/Pending
- **Status** - Not Started / Contacted / Responded / Sent Drive / Reviewing / Published / Declined
- **Follow-Up Date** - When to check in again
- **Notes** - Any relevant details

### Success Metrics

**Phase 1 (First 30 Days):**
- Goal: Contact 15-20 channels
- Success: 5 responses (25% response rate)
- Win: 2-3 agree to review

**Phase 2 (First 60 Days):**
- Send drives to reviewers
- Goal: 2-3 published reviews
- Success: 50-100 sales from reviews

**Phase 3 (First 90 Days):**
- Expand outreach based on what's working
- Build affiliate program
- Scale successful partnerships

---

## 🎯 Next Actions

**Right now, you should:**

1. ✅ Review `knowledge_drive_research.md` (read the Executive Summary at minimum)
2. ✅ Read through `creator_contacts.md` to see the outreach templates
3. ✅ Decide if you're moving forward with this product
4. ✅ If yes: Open `outreach_tracker.csv` in Excel/Google Sheets
5. ✅ Draft your first outreach email to "The Ready Life" (best fit)
6. ✅ Optionally: Run `python3 find_more_channels.py` to discover more channels

**Questions to ask yourself:**

- Do I have 40-80 hours to curate content for the drive?
- Can I invest $500-1000 to test this idea?
- Am I interested in the prepper/survival niche?
- Do I want to build this business?

If yes to all → Start with the landing page this week.
If no to any → That's totally fine! You've learned valuable skills.

---

## 🤝 Need Help?

If you have questions about:
- Running the scripts → Check the comments in each .py file
- Outreach strategy → Review `creator_contacts.md` templates section
- Product strategy → See `knowledge_drive_research.md` recommended strategy
- Next steps → Follow `action_plan.md` phase by phase

---

## 📝 File Modification Log

- Initial research: 9 YouTube videos analyzed
- Contact extraction: Completed
- Outreach tracker: Created, ready for use
- Channel finder: Created, ready to run when needed

**Last Updated:** Today (when you ran the extraction script)

---

Good luck with your outreach! 🚀

Remember: The worst they can say is no. And even a 10% success rate means 1-2 partnerships from your first 15 contacts. That's enough to test and validate the market.

