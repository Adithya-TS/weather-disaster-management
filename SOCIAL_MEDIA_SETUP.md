# Real Social Media Data Integration Setup

## Overview
The Weather Disaster Management system now supports **real social media data** from multiple free sources instead of synthetic data. The system will automatically try to fetch real data and fall back to weather-based synthetic reports if APIs are unavailable.

## Available Data Sources

### 1. Reddit API (FREE) ⭐ RECOMMENDED
- **Cost**: 100% FREE
- **Data**: Real-time weather discussions, disaster reports from location-based subreddits
- **Rate Limit**: 60 requests/minute
- **Setup Instructions**:
  1. Go to https://www.reddit.com/prefs/apps
  2. Click "Create App" or "Create Another App"
  3. Fill in:
     - Name: "Weather Disaster Monitor"
     - App type: Select "script"
     - Description: "Weather disaster monitoring system"
     - About URL: (leave blank)
     - Redirect URI: http://localhost:8080
  4. Click "Create App"
  5. Copy the **client ID** (under app name) and **client secret**
  6. Add to `.env`:
     ```
     REDDIT_CLIENT_ID=your_client_id_here
     REDDIT_CLIENT_SECRET=your_client_secret_here
     ```

### 2. News API (FREE TIER) ⭐ RECOMMENDED
- **Cost**: FREE tier (100 requests/day)
- **Data**: News articles about weather disasters from multiple news sources
- **Setup Instructions**:
  1. Go to https://newsapi.org/register
  2. Sign up with email (no credit card required)
  3. Verify your email
  4. Copy your API key from dashboard
  5. Add to `.env`:
     ```
     NEWS_API_KEY=your_news_api_key_here
     ```

### 3. RSS Feeds (FREE)
- **Cost**: 100% FREE
- **Data**: Weather service RSS feeds
- **Setup**: No API key required - works out of the box
- **Sources**: Weather.com, AccuWeather, local weather services

### 4. Telegram Bot (OPTIONAL)
- **Cost**: 100% FREE
- **Data**: Messages from public Telegram weather/emergency channels
- **Setup Instructions** (Optional):
  1. Open Telegram and search for "BotFather"
  2. Send `/newbot` command
  3. Follow instructions to create bot
  4. Copy the bot token
  5. Add to `.env`:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token_here
     ```
  6. Note: You'll need to add the bot to public channels to fetch data

## Quick Start

### Minimum Setup (2 minutes)
For immediate real data access, set up **Reddit + News API**:

1. **Copy the example .env**:
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Get Reddit API credentials** (1 minute):
   - Visit: https://www.reddit.com/prefs/apps
   - Create app, copy client ID and secret
   - Paste into `.env`

3. **Get News API key** (1 minute):
   - Visit: https://newsapi.org/register
   - Sign up (free, no credit card)
   - Copy API key
   - Paste into `.env`

4. **Restart the backend**:
   ```powershell
   uvicorn src.api.fastapi_app:app --reload
   ```

### Your `.env` File Should Look Like:
```env
# Required for weather data
GOOGLE_API_KEY=your_google_api_key
OPENWEATHER_API_KEY=your_openweather_key

# Social Media APIs (Reddit + News = Real Data!)
REDDIT_CLIENT_ID=abcd1234efgh5678
REDDIT_CLIENT_SECRET=xyz9876_secretkey_here
NEWS_API_KEY=abc123def456ghi789jkl012

# Telegram (optional)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

## How It Works

### Data Flow
1. **User requests social media reports** for a location (e.g., "Chennai")
2. **System tries data sources in order**:
   - ✅ Reddit API → Search for weather discussions in location-based subreddits
   - ✅ News API → Fetch recent weather news articles about the location
   - ✅ RSS Feeds → Parse weather service feeds (no API key needed)
   - ✅ Telegram → Check configured channels (if token provided)
3. **Fallback**: If all APIs fail (no credentials or rate limit exceeded), system generates synthetic reports based on real weather data

### Example Real Data Output
```
📱 [Reddit] Heavy rain reported in Chennai - Adyar area flooding - @ChennaiRains
📱 [News] Chennai Weather Alert: IMD forecasts thunderstorms - @TimesofIndia
📱 [RSS] Chennai: Scattered showers expected today - @WeatherService
```

## Testing

### Test Without API Keys (Fallback Mode)
```bash
# Social media will use synthetic data based on real weather
curl http://localhost:8000/api/v1/social-media/Chennai
```

### Test With Reddit API
```bash
# After adding REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env
curl http://localhost:8000/api/v1/social-media/Chennai
# Should see real Reddit posts about Chennai weather
```

### Test With News API
```bash
# After adding NEWS_API_KEY to .env
curl http://localhost:8000/api/v1/social-media/Miami
# Should see real news articles about Miami weather
```

## Troubleshooting

### No Real Data Showing Up
1. **Check .env file**: Make sure API keys are added correctly (no quotes, no spaces)
2. **Restart backend**: Social media integrations load credentials on startup
3. **Check logs**: Look for `reddit.initialized`, `news.initialized` messages
4. **Verify credentials**: Test API keys directly:
   - Reddit: Use PRAW test script
   - News: Visit https://newsapi.org/account to check API key status

### Rate Limits
- **Reddit**: 60 requests/minute - very generous
- **News API Free**: 100 requests/day - sufficient for testing
- **Solution**: System automatically falls back to synthetic data if rate limit hit

### Reddit No Results
- Reddit searches for recent posts (24 hours)
- If no posts found, falls back to News/RSS
- Try popular locations: "Chennai", "Miami", "New York", "Tokyo"

## Cost Breakdown

| Service | Free Tier | Paid Tier | Recommendation |
|---------|-----------|-----------|----------------|
| Reddit | ✅ Unlimited | N/A | Use this! |
| News API | ✅ 100/day | $449/month | Free tier enough |
| RSS Feeds | ✅ Unlimited | N/A | Always enabled |
| Telegram | ✅ Unlimited | N/A | Optional |
| **Total Cost** | **$0/month** | - | **100% Free!** |

## Implementation Details

### Files Modified
1. **requirements.txt**: Added `python-telegram-bot`, `newsapi-python`, `feedparser`
2. **src/tools/social_media_sources.py**: New module with Reddit, News, RSS, Telegram clients
3. **src/tools/custom_tools.py**: Updated `get_social_media_reports()` to use real APIs
4. **.env.example**: Added API key placeholders with setup instructions

### Architecture
```
get_social_media_reports(location)
    ↓
get_real_social_media_reports(location) 
    ├── RedditSource.fetch_reports()
    ├── NewsSource.fetch_reports()
    ├── RSSSource.fetch_reports()
    └── TelegramSource.fetch_reports()
    ↓
    If all fail ↓
Fallback to synthetic reports (weather-based)
```

## Next Steps

1. ✅ Add API credentials to `.env`
2. ✅ Restart backend
3. ✅ Test social media endpoint
4. 🔄 (Optional) Set up Telegram bot for additional data
5. 🔄 (Optional) Upgrade News API if you need >100 requests/day

## Support
- Reddit API docs: https://www.reddit.com/dev/api
- News API docs: https://newsapi.org/docs
- Telegram Bot API: https://core.telegram.org/bots/api
