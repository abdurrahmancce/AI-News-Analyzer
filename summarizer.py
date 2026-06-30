from typing import Optional
import re

# Try to use transformers for better summarization
# Falls back to simple extractive summarization if not available
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class ArticleSummarizer:
    """
    Handles AI-powered article summarization.
    """
    
    def __init__(self):
        """
        Initialize the summarizer.
        """
        self.summarizer_pipeline = None
        self._load_model()
    
    def _load_model(self):
        """
        Lazy-load the transformer model.
        """
        if TRANSFORMERS_AVAILABLE and self.summarizer_pipeline is None:
            try:
                # Using a smaller model for faster loading
                self.summarizer_pipeline = pipeline(
                    "summarization",
                    model="sshleifer/distilbart-cnn-12-6",
                    max_length=150,
                    min_length=30,
                    do_sample=False
                )
            except Exception as e:
                print(f"Could not load transformer model: {e}")
                self.summarizer_pipeline = None
    
    def summarize(self, text: str, max_length: int = 150) -> str:
        """
        Generate a summary of the given text.
        
        Args:
            text: Article text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        if not text or len(text.strip()) < 50:
            return "Content too short to summarize."
        
        # Clean the text
        clean_text = self._clean_text(text)
        
        # Try transformer-based summarization first
        if self.summarizer_pipeline and len(clean_text) > 200:
            try:
                # Truncate if too long for the model
                input_text = clean_text[:3000]
                summary = self.summarizer_pipeline(
                    input_text,
                    max_length=max_length,
                    min_length=min(30, max_length // 2),
                    do_sample=False
                )
                return summary[0]["summary_text"].strip()
            except Exception as e:
                print(f"Transformer summarization failed: {e}")
        
        # Fallback to extractive summarization
        return self._extractive_summarize(clean_text, max_length)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for summarization.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might break summarization
        text = text.replace('\n', ' ').strip()
        return text
    
    def _extractive_summarize(self, text: str, max_length: int = 150) -> str:
        """
        Simple extractive summarization using sentence scoring.
        
        Args:
            text: Article text
            max_length: Maximum summary length
            
        Returns:
            Extractive summary
        """
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 2:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Score sentences by word frequency
        word_freq = {}
        for sentence in sentences:
            words = sentence.lower().split()
            for word in words:
                word = re.sub(r'[^\w]', '', word)
                if len(word) > 3:  # Ignore short words
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score sentences
        sentence_scores = []
        for sentence in sentences:
            score = 0
            words = sentence.lower().split()
            for word in words:
                word = re.sub(r'[^\w]', '', word)
                score += word_freq.get(word, 0)
            sentence_scores.append((sentence, score))
        
        # Sort by score and select top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 2-3 sentences
        num_sentences = min(3, len(sentence_scores))
        top_sentences = [s[0] for s in sentence_scores[:num_sentences]]
        
        # Restore original order
        summary = ' '.join(
            s for s in sentences if s in top_sentences
        )
        
        # Truncate if needed
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + "..."
        
        return summary
    
    def _split_sentences(self, text: str) -> list:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
