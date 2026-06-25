"""
sentiment.py - Performs sentiment analysis on news articles.
"""

from typing import Dict, Tuple
from enum import Enum


class SentimentType(Enum):
    """Sentiment classification types."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SentimentAnalyzer:
    """
    Analyzes sentiment of news articles.
    """
    
    # Emoji mapping for sentiment types
    EMOJIS = {
        SentimentType.POSITIVE: "😊",
        SentimentType.NEGATIVE: "😞",
        SentimentType.NEUTRAL: "😐"
    }
    
    # Color coding for UI
    COLORS = {
        SentimentType.POSITIVE: "#2ecc71",  # Green
        SentimentType.NEGATIVE: "#e74c3c",  # Red
        SentimentType.NEUTRAL: "#95a5a6"    # Gray
    }
    
    def __init__(self, use_vader: bool = True):
        """
        Initialize sentiment analyzer.
        
        Args:
            use_vader: Use VADER instead of TextBlob
        """
        self.analyzer = None
        self.use_vader = use_vader
        self._load_analyzer()
    
    def _load_analyzer(self):
        """
        Load the appropriate sentiment analyzer.
        """
        if self.use_vader:
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                self.analyzer = SentimentIntensityAnalyzer()
            except ImportError:
                print("VADER not available, falling back to TextBlob")
                self.use_vader = False
        
        if not self.use_vader:
            try:
                from textblob import TextBlob
                self.analyzer = TextBlob
            except ImportError:
                raise ImportError(
                    "Neither VADER nor TextBlob is installed. "
                    "Please install one: pip install vaderSentiment or pip install textblob"
                )
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of the given text.
        
        Args:
            text: Article text to analyze
            
        Returns:
            Dictionary with sentiment results
        """
        if not text or len(text.strip()) < 10:
            return {
                "sentiment": SentimentType.NEUTRAL,
                "label": "Neutral",
                "emoji": self.EMOJIS[SentimentType.NEUTRAL],
                "score": 0.0,
                "color": self.COLORS[SentimentType.NEUTRAL],
                "confidence": 0.0
            }
        
        if self.use_vader:
            return self._analyze_vader(text)
        else:
            return self._analyze_textblob(text)
    
    def _analyze_vader(self, text: str) -> Dict:
        """
        Analyze using VADER sentiment analyzer.
        
        Args:
            text: Input text
            
        Returns:
            Sentiment results dictionary
        """
        scores = self.analyzer.polarity_scores(text)
        compound = scores["compound"]
        
        # VADER compound score thresholds
        if compound >= 0.05:
            sentiment = SentimentType.POSITIVE
        elif compound <= -0.05:
            sentiment = SentimentType.NEGATIVE
        else:
            sentiment = SentimentType.NEUTRAL
        
        # Calculate confidence (normalized)
        confidence = abs(compound)
        
        return {
            "sentiment": sentiment,
            "label": sentiment.value.capitalize(),
            "emoji": self.EMOJIS[sentiment],
            "score": round(compound, 3),
            "color": self.COLORS[sentiment],
            "confidence": round(confidence, 3),
            "details": {
                "positive": round(scores["pos"], 3),
                "negative": round(scores["neg"], 3),
                "neutral": round(scores["neu"], 3)
            }
        }
    
    def _analyze_textblob(self, text: str) -> Dict:
        """
        Analyze using TextBlob.
        
        Args:
            text: Input text
            
        Returns:
            Sentiment results dictionary
        """
        blob = self.analyzer(text)
        polarity = blob.sentiment.polarity
        
        # TextBlob polarity: -1 to 1
        if polarity > 0.1:
            sentiment = SentimentType.POSITIVE
        elif polarity < -0.1:
            sentiment = SentimentType.NEGATIVE
        else:
            sentiment = SentimentType.NEUTRAL
        
        confidence = abs(polarity)
        
        return {
            "sentiment": sentiment,
            "label": sentiment.value.capitalize(),
            "emoji": self.EMOJIS[sentiment],
            "score": round(polarity, 3),
            "color": self.COLORS[sentiment],
            "confidence": round(confidence, 3),
            "details": {
                "subjectivity": round(blob.sentiment.subjectivity, 3)
            }
        }
    
    def get_sentiment_badge(self, text: str) -> str:
        """
        Get a formatted sentiment badge string.
        
        Args:
            text: Article text
            
        Returns:
            Formatted badge string
        """
        result = self.analyze(text)
        return f"{result['emoji']} {result['label']} (Score: {result['score']})"