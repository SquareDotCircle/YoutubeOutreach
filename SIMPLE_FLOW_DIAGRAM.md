# Simple Flow Diagrams - Ready to Render

Copy any of these diagrams and paste into **https://mermaid.live/** to see them rendered!

---

## 🎯 Quick Overview: How Both Scripts Work Together

**Copy this entire block (including the ```mermaid) and paste into mermaid.live:**

```mermaid
graph TB
    Start([You Want to Find<br/>Prepper Creators])
    
    Start --> Research[Watch YouTube Videos<br/>Find 9 Interesting Channels]
    
    Research --> Script1[Run: extract_creator_contacts.py<br/>Input: 9 Video URLs]
    
    Script1 --> Extract[For Each Video:<br/>📧 Extract emails<br/>📱 Find Instagram/Twitter<br/>🌐 Find websites]
    
    Extract --> Output1[📄 creator_contacts.md<br/>📊 creator_contacts.csv<br/>✓ 9 channels analyzed]
    
    Output1 --> Question{Enough<br/>Contacts?}
    
    Question -->|Need More| Script2[Run: find_more_channels.py<br/>Input: Search Terms]
    
    Script2 --> Search[Search YouTube 10 Times:<br/>'prepper grid down'<br/>'survival knowledge'<br/>'off grid living'<br/>etc.]
    
    Search --> Discover[Discover New Channels<br/>Filter by Subscriber Count<br/>Remove Duplicates]
    
    Discover --> Output2[📄 discovered_channels.md<br/>📊 discovered_channels.csv<br/>✓ 38 new channels found<br/>✓ 17 in target range]
    
    Output2 --> Manual[Visit Channel<br/>'About' Pages<br/>Find Contact Info]
    
    Manual --> AddMore[Add Promising Videos<br/>to Script 1]
    
    AddMore --> Script1
    
    Question -->|Yes| Outreach[🎯 Start Creator Outreach<br/>Track in outreach_tracker.csv]
    
    Outreach --> Partner[Partner with Creators<br/>Get Reviews & Affiliates]
    
    Partner --> Success([🚀 Launch Product!])
    
    style Start fill:#e1f5e1
    style Script1 fill:#bbdefb
    style Script2 fill:#ffb74d
    style Output1 fill:#fff9c4
    style Output2 fill:#ffecb3
    style Outreach fill:#ce93d8
    style Success fill:#81c784
    style Question fill:#f48fb1
```

---

## 🔍 How find_more_channels.py Works (Simplified)

**Copy and render this:**

```mermaid
flowchart TD
    Start([Script Starts])
    
    Start --> Init[all_channels = {}<br/>Empty dictionary]
    
    Init --> Loop1[Loop 1 of 10<br/>Search: 'prepper grid down']
    
    Loop1 --> YT1[YouTube Search<br/>Returns 5 video URLs]
    
    YT1 --> Loop2[For each of 5 URLs...]
    
    Loop2 --> Get1[Get channel info<br/>from video]
    
    Get1 --> Check1{Channel ID<br/>already in<br/>dictionary?}
    
    Check1 -->|No - New!| Add1[✓ Add to all_channels<br/>Print: ✓ Channel Name]
    
    Check1 -->|Yes - Dupe| Skip1[⏭️ Skip<br/>Already have it]
    
    Add1 --> Next1[Next URL...]
    Skip1 --> Next1
    
    Next1 --> Loop3[Loop 2 of 10<br/>Search: 'survival knowledge']
    
    Loop3 --> YT2[YouTube Search<br/>Returns 5 more URLs]
    
    YT2 --> Process[Same process...<br/>Get info, check dupes,<br/>add if new]
    
    Process --> More[Loops 3-10...<br/>8 more searches]
    
    More --> Done[All 10 searches complete]
    
    Done --> Count[Total: 38 unique channels<br/>in all_channels dict]
    
    Count --> Sort[Sort by<br/>subscriber count]
    
    Sort --> Filter[Filter:<br/>Keep only 10k-500k subs<br/>Result: 17 channels]
    
    Filter --> Save1[Save to<br/>discovered_channels.md]
    
    Save1 --> Save2[Save to<br/>discovered_channels.csv]
    
    Save2 --> End([✓ Complete!])
    
    style Start fill:#e1f5e1
    style Loop1 fill:#ffccbc
    style Loop3 fill:#ffab91
    style Check1 fill:#f48fb1
    style Add1 fill:#a5d6a7
    style Skip1 fill:#ff8a65
    style Filter fill:#ce93d8
    style End fill:#81c784
```

---

## 🔄 The Deduplication Magic

**Copy and render this:**

```mermaid
flowchart LR
    subgraph Search1[Search 1: 'prepper grid down']
        S1V1[City Prepping<br/>ID: UCmb2...]
        S1V2[Bug Out Location<br/>ID: UCgex...]
        S1V3[Reliable Prepper<br/>ID: UCcFr...]
    end
    
    subgraph Dict1[all_channels dictionary]
        D1[UCmb2: City Prepping<br/>UCgex: Bug Out Location<br/>UCcFr: Reliable Prepper]
    end
    
    subgraph Search2[Search 2: 'survival knowledge']
        S2V1[City Prepping<br/>ID: UCmb2... AGAIN!]
        S2V2[Austrian Knife Guy<br/>ID: UCM-O...]
    end
    
    subgraph Check[Duplicate Check]
        C1{Is UCmb2<br/>in dict?}
    end
    
    subgraph Result[Result]
        R1[✓ Skip City Prepping<br/>✓ Add Austrian Knife Guy]
    end
    
    subgraph Dict2[Updated dictionary]
        D2[UCmb2: City Prepping<br/>UCgex: Bug Out Location<br/>UCcFr: Reliable Prepper<br/>UCM-O: Austrian Knife Guy]
    end
    
    S1V1 --> Dict1
    S1V2 --> Dict1
    S1V3 --> Dict1
    
    Dict1 --> Search2
    
    S2V1 --> Check
    S2V2 --> Check
    
    Check --> C1
    C1 -->|YES| R1
    C1 -->|NO| R1
    
    R1 --> Dict2
    
    style Dict1 fill:#fff9c4
    style Dict2 fill:#c8e6c9
    style Check fill:#f48fb1
    style R1 fill:#a5d6a7
```

---

## 📧 How extract_creator_contacts.py Works

**Copy and render this:**

```mermaid
flowchart TD
    Start([Script Starts])
    
    Start --> Load[Load VIDEO_URLS<br/>9 YouTube video URLs]
    
    Load --> Loop{For each URL...}
    
    Loop --> URL1[URL 1:<br/>youtube.com/watch?v=wnhCuYRYCdM]
    
    URL1 --> Fetch[Run yt-dlp<br/>Fetch video metadata]
    
    Fetch --> JSON[Get JSON response:<br/>- channel_name: WIRED<br/>- subscriber_count: 12.6M<br/>- description: full text...]
    
    JSON --> Regex[Apply Regex Patterns<br/>to Description Text]
    
    Regex --> Find1[📧 Email Pattern:<br/>xxx@yyy.com<br/>Found: none]
    
    Find1 --> Find2[📸 Instagram Pattern:<br/>instagram.com/USER<br/>Found: @wired]
    
    Find2 --> Find3[🐦 Twitter Pattern:<br/>twitter.com/USER<br/>Found: @wired]
    
    Find3 --> Find4[📘 Facebook Pattern:<br/>facebook.com/USER<br/>Found: wired]
    
    Find4 --> Find5[🎵 TikTok Pattern:<br/>tiktok.com/@USER<br/>Found: @wired]
    
    Find5 --> Find6[🌐 Website Pattern:<br/>https://domain.com<br/>Found: wired.com, etc.]
    
    Find6 --> Combine[Combine channel info<br/>+ contacts found]
    
    Combine --> Add[Add to channels_data list]
    
    Add --> Loop
    
    Loop --> Next[URL 2, 3, 4... 9]
    
    Next --> AllDone[All 9 URLs processed]
    
    AllDone --> Categorize[Categorize:<br/>- Prepper channels<br/>- Other channels]
    
    Categorize --> Generate[Generate markdown report<br/>with contact info<br/>+ outreach templates]
    
    Generate --> Save1[Save to<br/>creator_contacts.md]
    
    Save1 --> Save2[Save to<br/>creator_contacts.csv]
    
    Save2 --> End([✓ Complete!])
    
    style Start fill:#e1f5e1
    style Loop fill:#ffccbc
    style Fetch fill:#bbdefb
    style Regex fill:#90caf9
    style Find1 fill:#e3f2fd
    style Find2 fill:#e3f2fd
    style Find3 fill:#e3f2fd
    style Find4 fill:#e3f2fd
    style Find5 fill:#e3f2fd
    style Find6 fill:#e3f2fd
    style Categorize fill:#ce93d8
    style End fill:#81c784
```

---

## 🎯 Your Actual Workflow (What You Just Did)

**Copy and render this:**

```mermaid
flowchart TD
    You([You])
    
    You --> Step1[📺 Watched 9 prepper videos]
    
    Step1 --> Step2[📝 Collected video URLs]
    
    Step2 --> Run1[💻 Ran:<br/>extract_creator_contacts.py]
    
    Run1 --> Result1[📄 Got creator_contacts.md<br/>✓ Found 1 email<br/>✓ Found 6 social accounts<br/>✓ Found 7 websites]
    
    Result1 --> Question{Enough<br/>channels?}
    
    Question -->|No| Run2[💻 Ran:<br/>find_more_channels.py]
    
    Run2 --> Result2[📄 Got discovered_channels.md<br/>✓ Found 38 unique channels<br/>✓ 17 in target range 10k-500k]
    
    Result2 --> Next[📋 Next Step:<br/>Visit channel About pages<br/>Find contact info<br/>Add to outreach tracker]
    
    Next --> Future[🎯 Future:<br/>Contact creators<br/>Send free drives<br/>Get reviews<br/>Launch product!]
    
    style You fill:#e1f5e1
    style Run1 fill:#bbdefb
    style Run2 fill:#ffb74d
    style Result1 fill:#fff9c4
    style Result2 fill:#c8e6c9
    style Future fill:#ce93d8
```

---

## 🔢 Data Flow Through Scripts

**Copy and render this:**

```mermaid
graph LR
    subgraph Input
        I1[Video URLs<br/>or<br/>Search Terms]
    end
    
    subgraph Processing
        P1[yt-dlp<br/>Contacts YouTube API]
        P2[Regex Patterns<br/>Extract contacts]
        P3[Filter & Sort<br/>By subscriber count]
    end
    
    subgraph Storage
        S1[Python Dictionaries<br/>& Lists]
        S2[Deduplication<br/>Logic]
    end
    
    subgraph Output
        O1[Markdown Reports<br/>.md files]
        O2[CSV Spreadsheets<br/>.csv files]
    end
    
    I1 --> P1
    P1 --> P2
    P1 --> P3
    P2 --> S1
    P3 --> S1
    S1 --> S2
    S2 --> O1
    S2 --> O2
    
    style I1 fill:#e3f2fd
    style P1 fill:#bbdefb
    style P2 fill:#90caf9
    style P3 fill:#64b5f6
    style S1 fill:#fff9c4
    style S2 fill:#ffecb3
    style O1 fill:#a5d6a7
    style O2 fill:#c8e6c9
```

---

## 🎨 How to View These Diagrams

### Option 1: Online (Easiest - Do This Now!)

1. Go to **https://mermaid.live/**
2. Copy ANY diagram above (including the \`\`\`mermaid and \`\`\`)
3. Paste into the left panel
4. See beautiful rendered diagram on the right!
5. Export as PNG/SVG if you want

### Option 2: VS Code

1. Install extension: **"Markdown Preview Mermaid Support"**
2. Open this file (`SIMPLE_FLOW_DIAGRAM.md`)
3. Click the preview button (top right)
4. All diagrams render automatically!

### Option 3: GitHub

1. Push this file to GitHub
2. Diagrams auto-render in the browser
3. Share link with others

---

## 🚀 Try It Right Now!

**Copy this block and paste into https://mermaid.live/:**

```mermaid
flowchart LR
    You[You Are Here] --> Action[Copy a Diagram]
    Action --> Paste[Paste into<br/>mermaid.live]
    Paste --> See[See Beautiful<br/>Visual Diagram!]
    See --> Export[Optional:<br/>Export as Image]
    
    style You fill:#e1f5e1
    style See fill:#a5d6a7
    style Export fill:#81c784
```

---

## 📊 All Your Documentation Files

```
Diagrams (Visual):
├── SIMPLE_FLOW_DIAGRAM.md ← YOU ARE HERE (easiest to render)
├── MERMAID_DIAGRAMS.md (comprehensive workflows)
├── PYTHON_CODE_DIAGRAMS.md (code internals)
└── FIND_MORE_CHANNELS_DIAGRAM.md (channel finder details)

Guides (Text):
├── QUICK_MODIFICATION_GUIDE.md (copy-paste changes)
├── VIEW_DIAGRAMS.md (how to view)
└── README.md (getting started)

Data (Results):
├── creator_contacts.md + .csv (9 original channels)
├── discovered_channels.md + .csv (38 new channels)
└── outreach_tracker.csv (track your outreach)

Strategy:
├── knowledge_drive_research.md (market research)
└── action_plan.md (step-by-step plan)
```

---

**🎯 Action: Go to https://mermaid.live/ right now and paste the first diagram!**

