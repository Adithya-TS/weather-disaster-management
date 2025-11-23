"""
Real Social Media Data Sources
Integrates Reddit, Telegram, and News APIs for real-time citizen reports
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


class RedditSource:
    """Fetch weather-related posts from Reddit"""
    
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = "WeatherDisasterManagement/1.0"
        self.reddit = None
        
    def initialize(self):
        """Initialize Reddit API client"""
        if not self.client_id or not self.client_secret:
            logger.warning("reddit.no_credentials")
            return False
            
        try:
            import praw
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            logger.info("reddit.initialized")
            return True
        except Exception as e:
            logger.error("reddit.init_failed", error=str(e))
            return False
    
    def fetch_reports(self, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch weather-related posts from location-based subreddits
        
        Args:
            location: Location name (e.g., "Chennai", "Miami")
            limit: Maximum number of posts to fetch
            
        Returns:
            List of report dictionaries
        """
        if not self.reddit and not self.initialize():
            return []
        
        reports = []
        search_terms = ["weather", "storm", "rain", "flood", "disaster", "fog", "heat"]
        
        try:
            # Search in location-specific subreddits
            for term in search_terms[:2]:  # Limit searches to avoid rate limits
                query = f"{term} {location}"
                
                try:
                    for submission in self.reddit.subreddit("all").search(
                        query, 
                        sort="new", 
                        time_filter="day", 
                        limit=limit
                    ):
                        reports.append({
                            "source": "Reddit",
                            "platform": "reddit",
                            "author": f"u/{submission.author.name}" if submission.author else "deleted",
                            "content": f"{submission.title}\n{submission.selftext[:200]}" if submission.selftext else submission.title,
                            "timestamp": datetime.fromtimestamp(submission.created_utc).isoformat(),
                            "url": f"https://reddit.com{submission.permalink}",
                            "location": location
                        })
                        
                        if len(reports) >= limit:
                            break
                except Exception as e:
                    logger.warning("reddit.search_failed", term=term, error=str(e))
                    continue
            
            logger.info("reddit.fetched", count=len(reports), location=location)
            return reports[:limit]
            
        except Exception as e:
            logger.error("reddit.fetch_failed", location=location, error=str(e))
            return []


class TelegramSource:
    """Fetch reports from public Telegram channels"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot = None
        
    def initialize(self):
        """Initialize Telegram Bot API"""
        if not self.bot_token:
            logger.warning("telegram.no_token")
            return False
            
        try:
            from telegram import Bot
            self.bot = Bot(token=self.bot_token)
            logger.info("telegram.initialized")
            return True
        except Exception as e:
            logger.error("telegram.init_failed", error=str(e))
            return False
    
    def fetch_reports(self, location: str, channels: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch messages from public Telegram channels
        
        Args:
            location: Location name
            channels: List of public channel usernames (without @)
            limit: Maximum messages per channel
            
        Returns:
            List of report dictionaries
        """
        if not self.bot and not self.initialize():
            return []
        
        # Default weather/emergency channels (these are examples - replace with real channels)
        if not channels:
            channels = [
                "weatheralerts",
                "emergencyupdates", 
                "disasternews"
            ]
        
        reports = []
        
        try:
            for channel in channels:
                try:
                    # Note: This requires the bot to be added to the channel
                    # For public channels, you might need different approach
                    # This is a simplified example
                    
                    logger.info("telegram.skipped", reason="Requires channel-specific implementation")
                    # Actual implementation would use bot.get_chat() and channel history
                    
                except Exception as e:
                    logger.warning("telegram.channel_failed", channel=channel, error=str(e))
                    continue
            
            return reports
            
        except Exception as e:
            logger.error("telegram.fetch_failed", error=str(e))
            return []


class NewsSource:
    """Fetch weather news from News APIs"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.client = None
        
    def initialize(self):
        """Initialize News API client"""
        if not self.api_key:
            logger.warning("news.no_api_key")
            return False
            
        try:
            from newsapi import NewsApiClient
            self.client = NewsApiClient(api_key=self.api_key)
            logger.info("news.initialized")
            return True
        except Exception as e:
            logger.error("news.init_failed", error=str(e))
            return False
    
    def fetch_reports(self, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch news articles about weather in the location
        
        Args:
            location: Location name
            limit: Maximum number of articles
            
        Returns:
            List of report dictionaries
        """
        if not self.client and not self.initialize():
            return []
        
        reports = []
        
        try:
            # Search for weather-related news
            query = f"{location} AND (weather OR storm OR disaster OR flood OR rain)"
            
            # Get articles from the past 24 hours
            from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            articles = self.client.get_everything(
                q=query,
                language="en",
                sort_by="publishedAt",
                from_param=from_date,
                page_size=limit
            )
            
            if articles.get("status") == "ok":
                for article in articles.get("articles", []):
                    reports.append({
                        "source": "News",
                        "platform": article.get("source", {}).get("name", "News"),
                        "author": article.get("author", "News Agency"),
                        "content": article.get("title", "") + "\n" + (article.get("description", "") or ""),
                        "timestamp": article.get("publishedAt", datetime.now().isoformat()),
                        "url": article.get("url", ""),
                        "location": location
                    })
                
                logger.info("news.fetched", count=len(reports), location=location)
            
            return reports[:limit]
            
        except Exception as e:
            logger.error("news.fetch_failed", location=location, error=str(e))
            return []


class RSSSource:
    """Fetch weather reports from RSS feeds"""
    
    def fetch_reports(self, location: str, feeds: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch weather reports from RSS feeds
        
        Args:
            location: Location name
            feeds: List of RSS feed URLs
            limit: Maximum entries to fetch
            
        Returns:
            List of report dictionaries
        """
        if not feeds:
            # Default weather RSS feeds (examples - customize based on location)
            feeds = [
                "https://weather.com/rss/weather/today",
                "https://rss.accuweather.com/rss/liveweather_rss.asp"
            ]
        
        reports = []
        
        try:
            import feedparser
            
            for feed_url in feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:limit]:
                        # Filter by location if mentioned
                        content = f"{entry.get('title', '')} {entry.get('summary', '')}"
                        if location.lower() in content.lower():
                            reports.append({
                                "source": "RSS",
                                "platform": feed.feed.get("title", "RSS Feed"),
                                "author": entry.get("author", "Weather Service"),
                                "content": entry.get("title", "") + "\n" + entry.get("summary", "")[:200],
                                "timestamp": entry.get("published", datetime.now().isoformat()),
                                "url": entry.get("link", ""),
                                "location": location
                            })
                    
                except Exception as e:
                    logger.warning("rss.feed_failed", feed=feed_url, error=str(e))
                    continue
            
            logger.info("rss.fetched", count=len(reports), location=location)
            return reports[:limit]
            
        except Exception as e:
            logger.error("rss.fetch_failed", error=str(e))
            return []


def get_real_social_media_reports(location: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Aggregate reports from all available sources
    
    Args:
        location: Location name
        limit: Total number of reports to return
        
    Returns:
        Combined list of reports from all sources
    """
    all_reports = []
    
    # Try Reddit
    try:
        reddit = RedditSource()
        reddit_reports = reddit.fetch_reports(location, limit=5)
        all_reports.extend(reddit_reports)
    except Exception as e:
        logger.warning("reddit.disabled", error=str(e))
    
    # Try News API
    try:
        news = NewsSource()
        news_reports = news.fetch_reports(location, limit=5)
        all_reports.extend(news_reports)
    except Exception as e:
        logger.warning("news.disabled", error=str(e))
    
    # Try RSS
    try:
        rss = RSSSource()
        rss_reports = rss.fetch_reports(location, limit=5)
        all_reports.extend(rss_reports)
    except Exception as e:
        logger.warning("rss.disabled", error=str(e))
    
    # Try Telegram (if configured)
    try:
        telegram = TelegramSource()
        telegram_reports = telegram.fetch_reports(location, limit=5)
        all_reports.extend(telegram_reports)
    except Exception as e:
        logger.warning("telegram.disabled", error=str(e))
    
    # Sort by timestamp (most recent first)
    all_reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    logger.info("social_media.aggregated", total=len(all_reports), location=location)
    
    return all_reports[:limit]
