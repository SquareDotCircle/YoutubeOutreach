# Environment Variables Setup

## Required API Keys

### Anthropic Claude API Key (Required)

1. Get your API key from: https://console.anthropic.com/
2. Set the environment variable:

**macOS/Linux:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Or add to your shell profile (~/.zshrc or ~/.bashrc):**
```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

### YouTube Data API Key (Optional - for faster extraction)

1. Get your API key from: https://console.cloud.google.com/apis/credentials
2. Enable "YouTube Data API v3"
3. Set the environment variable:

```bash
export YOUTUBE_API_KEY="your-youtube-api-key-here"
```

## Verify Setup

Run this command to verify your API key is set:

```bash
echo $ANTHROPIC_API_KEY
```

If it returns your key, you're all set!

## Security Note

**NEVER commit API keys to git!** Always use environment variables.

