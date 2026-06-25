"""
utils.py - Helper functions and utilities.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict
from tkinter import messagebox


class FileExporter:
    """
    Handles exporting results to files.
    """
    
    @staticmethod
    def export_to_csv(
        data: List[Dict], 
        filepath: str
    ) -> bool:
        """
        Export article data to CSV file.
        
        Args:
            data: List of article dictionaries
            filepath: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        if not data:
            messagebox.showwarning("Export Error", "No data to export!")
            return False
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            return False
    
    @staticmethod
    def export_to_text(
        content: str, 
        filepath: str
    ) -> bool:
        """
        Export text content to file.
        
        Args:
            content: Text to export
            filepath: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            return False
    
    @staticmethod
    def generate_export_content(
        article: Dict, 
        summary: str, 
        sentiment: Dict
    ) -> str:
        """
        Generate formatted export content.
        
        Args:
            article: Article dictionary
            summary: Generated summary
            sentiment: Sentiment results
            
        Returns:
            Formatted text content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""AI NEWS ANALYZER REPORT
{'=' * 50}

Generated: {timestamp}

ARTICLE INFORMATION
-------------------
Title: {article.get('title', 'N/A')}
Source: {article.get('source', 'N/A')}
Author: {article.get('author', 'N/A')}
Published: {article.get('published_at', 'N/A')}
URL: {article.get('url', 'N/A')}

AI SUMMARY
----------
{summary}

SENTIMENT ANALYSIS
------------------
Sentiment: {sentiment.get('label', 'N/A')} {sentiment.get('emoji', '')}
Score: {sentiment.get('score', 'N/A')}
Confidence: {sentiment.get('confidence', 'N/A')}

{'=' * 50}
"""
        return content


class Validator:
    """
    Input validation utilities.
    """
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate NewsAPI key format.
        
        Args:
            api_key: API key string
            
        Returns:
            True if valid format
        """
        return bool(api_key and len(api_key) > 20)
    
    @staticmethod
    def validate_keyword(keyword: str) -> bool:
        """
        Validate search keyword.
        
        Args:
            keyword: Search term
            
        Returns:
            True if valid
        """
        return bool(keyword and len(keyword.strip()) > 0)