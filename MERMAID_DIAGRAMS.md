# Script Flow - Mermaid Diagrams

These diagrams can be rendered in GitHub, VS Code (with Mermaid extension), or any Mermaid viewer.

---

## 📊 High-Level System Overview

```mermaid
graph TB
    Start([Start: Research Prepper Videos])
    
    Start --> Manual[Manually Watch 9 Videos<br/>and Collect URLs]
    
    Manual --> Script1[extract_creator_contacts.py]
    
    Script1 --> Output1[creator_contacts.md<br/>creator_contacts.csv]
    
    Output1 --> Decision{Found Enough<br/>Channels?}
    
    Decision -->|No| Script2[find_more_channels.py<br/>Search YouTube for More]
    
    Script2 --> Output2[discovered_channels.md<br/>discovered_channels.csv]
    
    Output2 --> Manual2[Manually Check Channel<br/>'About' Pages for Contact Info]
    
    Manual2 --> AddMore[Add New Video URLs<br/>to Script 1]
    
    AddMore --> Script1
    
    Decision -->|Yes| Outreach[Begin Creator Outreach<br/>Using outreach_tracker.csv]
    
    Outreach --> Success([Launch Product with<br/>Creator Partnerships])
    
    style Start fill:#e1f5e1
    style Success fill:#e1f5e1
    style Script1 fill:#e3f2fd
    style Script2 fill:#e3f2fd
    style Output1 fill:#fff3e0
    style Output2 fill:#fff3e0
    style Outreach fill:#f3e5f5
```

---

## 🔍 Script 1: extract_creator_contacts.py

### Main Flow

```mermaid
flowchart TD
    Start([Start Script])
    
    Start --> LoadURLs[Load VIDEO_URLS List<br/>9 YouTube Video URLs]
    
    LoadURLs --> Loop{For Each<br/>Video URL}
    
    Loop --> ExtractInfo[Function: extract_channel_info<br/>Run yt-dlp --dump-json]
    
    ExtractInfo --> GetJSON[Get JSON Response<br/>with Channel Metadata]
    
    GetJSON --> ParseInfo[Extract:<br/>- Channel Name/ID/URL<br/>- Subscriber Count<br/>- Video Title<br/>- Full Description Text]
    
    ParseInfo --> ExtractContacts[Function: extract_contacts_from_description<br/>Apply Regex Patterns]
    
    ExtractContacts --> FindEmail[Find Emails<br/>Pattern: xxx@xxx.com]
    
    FindEmail --> FindInsta[Find Instagram<br/>Pattern: instagram.com/username]
    
    FindInsta --> FindTwitter[Find Twitter<br/>Pattern: twitter.com/username]
    
    FindTwitter --> FindFB[Find Facebook<br/>Pattern: facebook.com/username]
    
    FindFB --> FindTikTok[Find TikTok<br/>Pattern: tiktok.com/@username]
    
    FindTikTok --> FindWebsites[Find Websites<br/>Exclude Social Media Domains]
    
    FindWebsites --> CombineData[Combine Channel Info<br/>+ Contacts Dictionary]
    
    CombineData --> AddToList[Add to channels_data Array]
    
    AddToList --> Loop
    
    Loop -->|All Done| Categorize[Function: generate_markdown_report<br/>Categorize Channels]
    
    Categorize --> CheckPrepper{Contains Prepper<br/>Keywords?}
    
    CheckPrepper -->|Yes| PrepperList[Add to Prepper Channels]
    CheckPrepper -->|No| OtherList[Add to Other Channels]
    
    PrepperList --> GenMarkdown[Generate Markdown Report<br/>with Contact Info + Templates]
    OtherList --> GenMarkdown
    
    GenMarkdown --> SaveMD[Save: creator_contacts.md]
    
    SaveMD --> GenCSV[Generate CSV Version]
    
    GenCSV --> SaveCSV[Save: creator_contacts.csv]
    
    SaveCSV --> End([End Script<br/>Files Created Successfully])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style ExtractInfo fill:#bbdefb
    style ExtractContacts fill:#bbdefb
    style GenMarkdown fill:#c5cae9
    style SaveMD fill:#fff9c4
    style SaveCSV fill:#fff9c4
```

### Detailed: extract_channel_info() Function

```mermaid
flowchart LR
    Input[Input: Video URL<br/>youtube.com/watch?v=ABC123]
    
    Input --> Command[Run Command:<br/>yt-dlp --skip-download<br/>--dump-json URL]
    
    Command --> Process[yt-dlp Fetches<br/>Video Metadata<br/>from YouTube]
    
    Process --> JSON[Returns JSON Object]
    
    JSON --> Parse[Parse JSON<br/>Extract Fields]
    
    Parse --> Field1[video_id]
    Parse --> Field2[video_title]
    Parse --> Field3[channel_name]
    Parse --> Field4[channel_id]
    Parse --> Field5[channel_url]
    Parse --> Field6[subscriber_count]
    Parse --> Field7[description]
    Parse --> Field8[view_count]
    
    Field1 --> Dict[Create Python Dictionary]
    Field2 --> Dict
    Field3 --> Dict
    Field4 --> Dict
    Field5 --> Dict
    Field6 --> Dict
    Field7 --> Dict
    Field8 --> Dict
    
    Dict --> Output[Return Dictionary<br/>to Main Function]
    
    style Input fill:#e3f2fd
    style Command fill:#bbdefb
    style JSON fill:#90caf9
    style Dict fill:#fff9c4
    style Output fill:#a5d6a7
```

### Detailed: extract_contacts_from_description() Function

```mermaid
flowchart TB
    Input[Input: Description Text<br/>Full video description string]
    
    Input --> Init[Initialize Empty<br/>Contacts Dictionary]
    
    Init --> Email[Apply Email Regex<br/>Pattern: xxx@domain.com]
    Email --> EmailFound{Emails<br/>Found?}
    EmailFound -->|Yes| SaveEmail[Add to contacts['emails']]
    EmailFound -->|No| NextInsta[Continue]
    SaveEmail --> NextInsta
    
    NextInsta --> Insta[Apply Instagram Regex<br/>Pattern: instagram.com/USER]
    Insta --> InstaFound{Instagram<br/>Found?}
    InstaFound -->|Yes| SaveInsta[Add to contacts['instagram']]
    InstaFound -->|No| NextTwitter[Continue]
    SaveInsta --> NextTwitter
    
    NextTwitter --> Twitter[Apply Twitter Regex<br/>Pattern: twitter.com/USER]
    Twitter --> TwitterFound{Twitter<br/>Found?}
    TwitterFound -->|Yes| SaveTwitter[Add to contacts['twitter']]
    TwitterFound -->|No| NextFB[Continue]
    SaveTwitter --> NextFB
    
    NextFB --> FB[Apply Facebook Regex<br/>Pattern: facebook.com/USER]
    FB --> FBFound{Facebook<br/>Found?}
    FBFound -->|Yes| SaveFB[Add to contacts['facebook']]
    FBFound -->|No| NextTT[Continue]
    SaveFB --> NextTT
    
    NextTT --> TikTok[Apply TikTok Regex<br/>Pattern: tiktok.com/@USER]
    TikTok --> TTFound{TikTok<br/>Found?}
    TTFound -->|Yes| SaveTT[Add to contacts['tiktok']]
    TTFound -->|No| NextWeb[Continue]
    SaveTT --> NextWeb
    
    NextWeb --> Web[Apply Website Regex<br/>Pattern: https?://domain.com]
    Web --> WebFilter[Filter Out<br/>Social Media Domains]
    WebFilter --> WebFound{Websites<br/>Found?}
    WebFound -->|Yes| SaveWeb[Add to contacts['websites']]
    WebFound -->|No| Cleanup[Clean Up Duplicates]
    SaveWeb --> Cleanup
    
    Cleanup --> Output[Return Complete<br/>Contacts Dictionary]
    
    style Input fill:#e3f2fd
    style Init fill:#c5cae9
    style Output fill:#a5d6a7
    style Email fill:#fff9c4
    style Insta fill:#fff9c4
    style Twitter fill:#fff9c4
    style FB fill:#fff9c4
    style TikTok fill:#fff9c4
    style Web fill:#fff9c4
```

---

## 🔎 Script 2: find_more_channels.py

### Main Flow

```mermaid
flowchart TD
    Start([Start Script])
    
    Start --> LoadTerms[Load SEARCH_TERMS List<br/>10 Search Queries]
    
    LoadTerms --> AllChannels[Initialize:<br/>all_channels = empty dict]
    
    AllChannels --> LoopTerms{For Each<br/>Search Term}
    
    LoopTerms --> SearchYT[Function: search_youtube<br/>Query YouTube with Term]
    
    SearchYT --> YTCommand[Run Command:<br/>yt-dlp --get-id --flat-playlist<br/>ytsearch10:TERM]
    
    YTCommand --> GetIDs[Get Video IDs<br/>Up to 10 Results]
    
    GetIDs --> ConvertURLs[Convert IDs to<br/>Full YouTube URLs]
    
    ConvertURLs --> LoopVideos{For Each<br/>Video URL}
    
    LoopVideos --> GetChannel[Function: get_channel_info<br/>Extract Channel Metadata]
    
    GetChannel --> CheckDupe{Channel Already<br/>in all_channels?}
    
    CheckDupe -->|Yes| SkipDupe[Skip Duplicate]
    CheckDupe -->|No| AddChannel[Add to all_channels<br/>Key: channel_id]
    
    SkipDupe --> LoopVideos
    AddChannel --> LoopVideos
    
    LoopVideos -->|All Videos Done| LoopTerms
    
    LoopTerms -->|All Terms Done| Sort[Sort Channels by<br/>Subscriber Count<br/>High to Low]
    
    Sort --> Filter[Filter Channels:<br/>Keep Only 10k-500k Subs]
    
    Filter --> GenReport[Generate Markdown Report<br/>Target Channels Section +<br/>All Channels List]
    
    GenReport --> SaveMD[Save: discovered_channels.md]
    
    SaveMD --> GenCSV[Generate CSV Version]
    
    GenCSV --> SaveCSV[Save: discovered_channels.csv]
    
    SaveCSV --> Summary[Print Summary:<br/>Total Channels Found<br/>Target Range Count]
    
    Summary --> End([End Script<br/>Files Created Successfully])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style SearchYT fill:#bbdefb
    style GetChannel fill:#bbdefb
    style Filter fill:#c5cae9
    style SaveMD fill:#fff9c4
    style SaveCSV fill:#fff9c4
```

### Detailed: search_youtube() Function

```mermaid
flowchart LR
    Input[Input: Search Query<br/>e.g., 'prepper grid down'<br/>max_results: 10]
    
    Input --> BuildQuery[Build yt-dlp Query:<br/>ytsearch10:QUERY]
    
    BuildQuery --> Command[Run Command:<br/>yt-dlp --skip-download<br/>--get-id --flat-playlist<br/>ytsearchN:QUERY]
    
    Command --> YTSearch[yt-dlp Searches<br/>YouTube with Query]
    
    YTSearch --> GetResults[Returns Video IDs<br/>One per line]
    
    GetResults --> Parse[Parse Output:<br/>Split by Newlines]
    
    Parse --> IDs[List of Video IDs<br/>['abc123', 'def456', ...]]
    
    IDs --> Convert[Convert Each ID to URL<br/>youtube.com/watch?v=ID]
    
    Convert --> URLs[List of Full URLs]
    
    URLs --> Output[Return URL List<br/>to Main Function]
    
    style Input fill:#e3f2fd
    style Command fill:#bbdefb
    style YTSearch fill:#90caf9
    style URLs fill:#fff9c4
    style Output fill:#a5d6a7
```

### Data Flow Through Scripts

```mermaid
graph LR
    subgraph "Input Data"
        URLs[Video URLs<br/>or<br/>Search Terms]
    end
    
    subgraph "Processing"
        YTD[yt-dlp<br/>YouTube API Calls]
        Regex[Regex Pattern<br/>Matching]
        Filter[Filtering &<br/>Categorization]
    end
    
    subgraph "Output Data"
        MD[Markdown Reports<br/>.md files]
        CSV[Spreadsheet Data<br/>.csv files]
    end
    
    URLs --> YTD
    YTD --> Regex
    Regex --> Filter
    Filter --> MD
    Filter --> CSV
    
    style URLs fill:#e3f2fd
    style YTD fill:#bbdefb
    style Regex fill:#c5cae9
    style Filter fill:#fff9c4
    style MD fill:#a5d6a7
    style CSV fill:#a5d6a7
```

---

## 🎨 Modification Points (Interactive)

```mermaid
flowchart TB
    subgraph "What Do You Want to Change?"
        Mod1[Add More Videos<br/>to Analyze]
        Mod2[Search for Different<br/>Channel Types]
        Mod3[Change Subscriber<br/>Filter Range]
        Mod4[Add New Contact<br/>Types Discord/Patreon]
        Mod5[Change Output<br/>Format/Filename]
    end
    
    Mod1 --> Edit1[Edit: extract_creator_contacts.py<br/>Line 8-18: VIDEO_URLS list]
    Mod2 --> Edit2[Edit: find_more_channels.py<br/>Line 11-23: SEARCH_TERMS list]
    Mod3 --> Edit3[Edit: find_more_channels.py<br/>Line ~75: subscriber filter]
    Mod4 --> Edit4[Edit: extract_creator_contacts.py<br/>Function: extract_contacts_from_description<br/>Add new regex pattern]
    Mod5 --> Edit5[Edit: Both scripts<br/>Line ~160-170: output_file variables]
    
    Edit1 --> Run1[Run: python3 extract_creator_contacts.py]
    Edit2 --> Run2[Run: python3 find_more_channels.py]
    Edit3 --> Run2
    Edit4 --> Run1
    Edit5 --> Run1
    Edit5 --> Run2
    
    Run1 --> Check[Check Output Files]
    Run2 --> Check
    
    Check --> Success{Looks Good?}
    Success -->|Yes| Done([✓ Modification Complete])
    Success -->|No| Debug[Add Debug Prints<br/>Check Error Messages]
    Debug --> Edit1
    Debug --> Edit2
    
    style Mod1 fill:#e3f2fd
    style Mod2 fill:#e3f2fd
    style Mod3 fill:#e3f2fd
    style Mod4 fill:#e3f2fd
    style Mod5 fill:#e3f2fd
    style Done fill:#a5d6a7
    style Debug fill:#ffcdd2
```

---

## 🔄 Data Structure Transformations

### How Data Changes Through Script 1

```mermaid
graph TB
    subgraph "Input"
        URL["Video URL<br/>youtube.com/watch?v=ABC123"]
    end
    
    subgraph "Step 1: yt-dlp Response"
        JSON["JSON Object<br/>{<br/>  id: 'ABC123',<br/>  title: 'Video Title',<br/>  uploader: 'Channel Name',<br/>  channel_id: 'UCxxx',<br/>  description: 'Full text...',<br/>  channel_follower_count: 50000<br/>}"]
    end
    
    subgraph "Step 2: Extracted Info"
        Info["Channel Info Dict<br/>{<br/>  video_id: 'ABC123',<br/>  channel_name: 'Channel Name',<br/>  channel_url: 'youtube.com/channel/UCxxx',<br/>  subscriber_count: 50000,<br/>  description: 'Full text...'<br/>}"]
    end
    
    subgraph "Step 3: Regex Extraction"
        Contacts["Contacts Dict<br/>{<br/>  emails: ['contact@example.com'],<br/>  instagram: ['channelname'],<br/>  twitter: ['channelname'],<br/>  websites: ['example.com']<br/>}"]
    end
    
    subgraph "Step 4: Combined"
        Combined["Complete Channel Data<br/>{<br/>  ...channel_info,<br/>  contacts: {<br/>    emails: [...],<br/>    instagram: [...],<br/>    ...<br/>  }<br/>}"]
    end
    
    subgraph "Step 5: Output"
        Output["Markdown + CSV Files<br/>### Channel Name<br/>Email: contact@example.com<br/>Instagram: @channelname<br/>..."]
    end
    
    URL --> JSON
    JSON --> Info
    Info --> Contacts
    Info --> Combined
    Contacts --> Combined
    Combined --> Output
    
    style URL fill:#e3f2fd
    style JSON fill:#bbdefb
    style Info fill:#90caf9
    style Contacts fill:#fff9c4
    style Combined fill:#ffecb3
    style Output fill:#a5d6a7
```

---

## 🎯 Real-World Usage Flow

```mermaid
sequenceDiagram
    participant User
    participant Script1 as extract_creator_contacts.py
    participant Script2 as find_more_channels.py
    participant YTDLP as yt-dlp
    participant YouTube
    participant Files as Output Files
    
    User->>Script1: Run with 9 video URLs
    Script1->>YTDLP: Request metadata for each video
    YTDLP->>YouTube: Fetch video/channel data
    YouTube-->>YTDLP: Return JSON data
    YTDLP-->>Script1: Pass JSON to script
    Script1->>Script1: Extract contacts with regex
    Script1->>Files: Create creator_contacts.md + .csv
    Files-->>User: Review contact information
    
    User->>Script2: Run to find more channels
    Script2->>YTDLP: Search "prepper grid down"
    YTDLP->>YouTube: Execute search query
    YouTube-->>YTDLP: Return 10 video IDs
    YTDLP-->>Script2: Pass video IDs
    Script2->>YTDLP: Get metadata for each video
    YTDLP->>YouTube: Fetch channel data
    YouTube-->>YTDLP: Return channel info
    YTDLP-->>Script2: Pass channel data
    Script2->>Script2: Filter by subscriber count
    Script2->>Files: Create discovered_channels.md + .csv
    Files-->>User: Review new channels
    
    User->>User: Visit channel 'About' pages
    User->>User: Find contact info manually
    User->>Script1: Add new video URLs
    Script1->>YTDLP: Process new videos
    Note right of User: Repeat cycle until<br/>enough contacts found
```

---

## 📊 Key Functions Map

```mermaid
mindmap
  root((Creator Contact Scripts))
    extract_creator_contacts.py
      extract_channel_info
        Runs yt-dlp
        Parses JSON
        Returns dict
      extract_contacts_from_description
        Email regex
        Instagram regex
        Twitter regex
        Facebook regex
        TikTok regex
        Website regex
      generate_markdown_report
        Categorizes channels
        Formats markdown
        Adds templates
      Main function
        Loops through URLs
        Combines data
        Saves files
    find_more_channels.py
      search_youtube
        Builds query
        Calls yt-dlp
        Returns URLs
      get_channel_info
        Fetches metadata
        Returns channel dict
      Main function
        Loops searches
        Deduplicates
        Filters by subs
        Saves reports
```

---

## 🛠️ How to View These Diagrams

### Option 1: GitHub
Upload this file to GitHub - diagrams render automatically!

### Option 2: VS Code
Install the "Markdown Preview Mermaid Support" extension

### Option 3: Online Viewer
Copy any diagram and paste into: https://mermaid.live/

### Option 4: Export as Image
Use Mermaid Live Editor to export as PNG/SVG

---

## 💡 Interactive Diagram: Choose Your Path

```mermaid
flowchart TD
    Start([I want to...])
    
    Start --> Choice1{What's Your Goal?}
    
    Choice1 -->|Find Contact Info| Path1[Use extract_creator_contacts.py]
    Choice1 -->|Discover New Channels| Path2[Use find_more_channels.py]
    Choice1 -->|Both| Path3[Use Both Scripts]
    
    Path1 --> Step1a[1. Add video URLs to VIDEO_URLS]
    Step1a --> Step1b[2. Run script]
    Step1b --> Step1c[3. Check creator_contacts.md]
    Step1c --> Step1d{Found Contacts?}
    Step1d -->|Yes| Outreach1[Start Outreach]
    Step1d -->|No| Manual1[Check Channel About Pages]
    
    Path2 --> Step2a[1. Customize SEARCH_TERMS]
    Step2a --> Step2b[2. Run script]
    Step2b --> Step2c[3. Check discovered_channels.md]
    Step2c --> Step2d[4. Visit channel About pages]
    Step2d --> Step2e[5. Add promising videos to Script 1]
    
    Path3 --> Step3a[1. Run Script 2 to discover]
    Step3a --> Step3b[2. Add discovered videos to Script 1]
    Step3b --> Step3c[3. Run Script 1 to extract]
    Step3c --> Outreach2[Begin Outreach]
    
    Outreach1 --> Track[Update outreach_tracker.csv]
    Outreach2 --> Track
    Manual1 --> Step1a
    Step2e --> Step1a
    
    Track --> Success([Launch with Partners!])
    
    style Start fill:#e1f5e1
    style Success fill:#a5d6a7
    style Path1 fill:#e3f2fd
    style Path2 fill:#fff3e0
    style Path3 fill:#f3e5f5
```

---

## 🔍 Detailed Regex Pattern Flow

```mermaid
flowchart LR
    subgraph "Input Text"
        Text["Follow us on Instagram:<br/>instagram.com/channelname<br/>Email: contact@example.com<br/>Visit: example.com"]
    end
    
    subgraph "Regex Patterns"
        P1[Email Pattern<br/>[A-Za-z0-9._%+-]+@...]
        P2[Instagram Pattern<br/>instagram.com/...]
        P3[Website Pattern<br/>https?://...]
    end
    
    subgraph "Matches Found"
        M1[contact@example.com]
        M2[channelname]
        M3[example.com]
    end
    
    subgraph "Organized Output"
        Out["contacts = {<br/>  'emails': ['contact@example.com'],<br/>  'instagram': ['channelname'],<br/>  'websites': ['example.com']<br/>}"]
    end
    
    Text --> P1
    Text --> P2
    Text --> P3
    
    P1 --> M1
    P2 --> M2
    P3 --> M3
    
    M1 --> Out
    M2 --> Out
    M3 --> Out
    
    style Text fill:#e3f2fd
    style P1 fill:#fff9c4
    style P2 fill:#fff9c4
    style P3 fill:#fff9c4
    style Out fill:#a5d6a7
```

---

**Copy any diagram above and paste into [mermaid.live](https://mermaid.live/) to see it rendered beautifully!**

