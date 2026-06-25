"""
news_fetcher.py - Fetches news articles from NewsAPI.
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime


class NewsFetcher:
    """
    Handles fetching news articles from NewsAPI.
    """
    
    BASE_URL = "https://newsapi.org/v2/everything"
    TOP_HEADLINES_URL = "https://newsapi.org/v2/top-headlines"
    
    def __init__(self, api_key: str):
        """
        Initialize with NewsAPI key.
        
        Args:
            api_key: Your NewsAPI API key
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }
    
    def fetch_by_keyword(
        self, 
        keyword: str, 
        page_size: int = 20,
        language: str = "en"
    ) -> List[Dict]:
        """
        Fetch news articles by keyword search.
        
        Args:
            keyword: Search term
            page_size: Number of articles to fetch (max 100)
            language: Article language code
            
        Returns:
            List of article dictionaries
            
        Raises:
            ConnectionError: If network connection fails
            ValueError: If API returns an error
        """
        params = {
            "q": keyword,
            "pageSize": min(page_size, 100),
            "language": language,
            "sortBy": "publishedAt",
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(
                self.BASE_URL, 
                params=params, 
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                raise ValueError(
                    f"API Error: {data.get('message', 'Unknown error')}"
                )
            
            return self._process_articles(data.get("articles", []))
            
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Unable to connect to the internet. Please check your connection."
            )
        except requests.exceptions.Timeout:
            raise ConnectionError(
                "Request timed out. Please try again later."
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error: {str(e)}")
    
    def fetch_top_headlines(
        self, 
        country: str = "us",
        category: Optional[str] = None,
        page_size: int = 20
    ) -> List[Dict]:
        """
        Fetch top headlines.
        
        Args:
            country: Two-letter country code
            category: News category (business, entertainment, etc.)
            page_size: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        params = {
            "country": country,
            "pageSize": min(page_size, 100),
            "apiKey": self.api_key
        }
        
        if category:
            params["category"] = category
            
        try:
            response = requests.get(
                self.TOP_HEADLINES_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                raise ValueError(
                    f"API Error: {data.get('message', 'Unknown error')}"
                )
            
            return self._process_articles(data.get("articles", []))
            
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Unable to connect to the internet. Please check your connection."
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error: {str(e)}")
    
    def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Process raw articles into a clean format.
        
        Args:
            articles: Raw articles from API
            
        Returns:
            List of processed article dictionaries
        """
        processed = []
        
        for article in articles:
            # Skip articles with no content
            if not article.get("title"):
                continue
                
            processed.append({
                "title": article.get("title", "No Title"),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", ""),
                "author": article.get("author", "Unknown"),
                "image_url": article.get("urlToImage", "")
            })
        
        return processed
    
    def format_date(self, date_str: str) -> str:
        """
        Format ISO date string to readable format.
        
        Args:
            date_str: ISO format date string
            
        Returns:
            Formatted date string
        """
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except (ValueError, AttributeError):
            return date_str