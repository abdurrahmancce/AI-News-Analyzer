"""
main.py - Main GUI application for AI News Analyzer.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import webbrowser
import threading
from typing import Optional

from news_fetcher import NewsFetcher
from summarizer import ArticleSummarizer
from sentiment import SentimentAnalyzer
from utils import FileExporter, Validator


class NewsAnalyzerApp:
    """
    Main application class for AI News Analyzer.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("AI News Analyzer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize components
        self.news_fetcher: Optional[NewsFetcher] = None
        self.summarizer = ArticleSummarizer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.exporter = FileExporter()
        
        # Data storage
        self.current_articles = []
        self.selected_article = None
        self.current_summary = ""
        self.current_sentiment = {}
        
        # Create UI
        self._create_styles()
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()
        
        # API Key dialog on startup
        self.root.after(100, self._show_api_key_dialog)
    
    def _create_styles(self):
        """Configure ttk styles."""
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 11, "bold"))
        self.style.configure("Status.TLabel", font=("Helvetica", 9))
    
    def _create_menu(self):
        """Create application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Summary...", command=self._export_summary)
        file_menu.add_command(label="Export All to CSV...", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self):
        """Create the main application layout."""
        # Main container with padding
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # === TOP: Search Bar ===
        self._create_search_bar()
        
        # === MIDDLE: Content Area ===
        self._create_content_area()
        
        # === BOTTOM: Analysis Panel ===
        self._create_analysis_panel()
    
    def _create_search_bar(self):
        """Create the search bar at the top."""
        search_frame = ttk.LabelFrame(self.main_frame, text="Search News", padding="10")
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        # Keyword entry
        ttk.Label(search_frame, text="Keyword:", style="Header.TLabel").grid(
            row=0, column=0, padx=(0, 10)
        )
        
        self.keyword_var = tk.StringVar()
        self.keyword_entry = ttk.Entry(search_frame, textvariable=self.keyword_var, font=("Helvetica", 11))
        self.keyword_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.keyword_entry.bind("<Return>", lambda e: self._search_news())
        
        # Search button
        self.search_btn = ttk.Button(
            search_frame, 
            text="🔍 Search", 
            command=self._search_news
        )
        self.search_btn.grid(row=0, column=2, padx=(0, 5))
        
        # Top Headlines button
        self.headlines_btn = ttk.Button(
            search_frame,
            text="📰 Top Headlines",
            command=self._fetch_headlines
        )
        self.headlines_btn.grid(row=0, column=3)
        
        # Progress bar
        self.progress = ttk.Progressbar(search_frame, mode="indeterminate", length=150)
        self.progress.grid(row=0, column=4, padx=(10, 0))
    
    def _create_content_area(self):
        """Create the middle content area with news list and details."""
        # Left: News List
        list_frame = ttk.LabelFrame(self.main_frame, text="News Articles", padding="5")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for news list
        columns = ("source", "date")
        self.news_tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings",
            selectmode="browse",
            height=15
        )
        self.news_tree.heading("#0", text="Title")
        self.news_tree.heading("source", text="Source")
        self.news_tree.heading("date", text="Date")
        
        self.news_tree.column("#0", width=300, minwidth=200)
        self.news_tree.column("source", width=120, minwidth=100)
        self.news_tree.column("date", width=150, minwidth=120)
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.news_tree.yview)
        self.news_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.news_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll.grid(row=0, column=1, sticky="ns")
        
        # Bind selection event
        self.news_tree.bind("<<TreeviewSelect>>", self._on_article_select)
        
        # Right: Article Details
        details_frame = ttk.LabelFrame(self.main_frame, text="Article Details", padding="10")
        details_frame.grid(row=1, column=1, sticky="nsew")
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)
        
        # Title
        self.detail_title = ttk.Label(
            details_frame, 
            text="Select an article to view details", 
            style="Title.TLabel",
            wraplength=500
        )
        self.detail_title.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Metadata
        self.detail_meta = ttk.Label(details_frame, text="", wraplength=500)
        self.detail_meta.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Description
        self.detail_desc = scrolledtext.ScrolledText(
            details_frame, 
            wrap=tk.WORD, 
            height=8,
            font=("Helvetica", 10)
        )
        self.detail_desc.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.detail_desc.config(state=tk.DISABLED)
        
        # Buttons
        btn_frame = ttk.Frame(details_frame)
        btn_frame.grid(row=3, column=0, sticky="ew")
        
        self.open_url_btn = ttk.Button(
            btn_frame, 
            text="🔗 Open Article", 
            command=self._open_article_url,
            state=tk.DISABLED
        )
        self.open_url_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.summarize_btn = ttk.Button(
            btn_frame,
            text="📝 Summarize",
            command=self._summarize_article,
            state=tk.DISABLED
        )
        self.summarize_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.analyze_btn = ttk.Button(
            btn_frame,
            text="💭 Analyze Sentiment",
            command=self._analyze_sentiment,
            state=tk.DISABLED
        )
        self.analyze_btn.pack(side=tk.LEFT)
    
    def _create_analysis_panel(self):
        """Create the bottom analysis panel."""
        analysis_frame = ttk.LabelFrame(self.main_frame, text="AI Analysis", padding="10")
        analysis_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.columnconfigure(1, weight=1)
        
        # Summary Section
        summary_frame = ttk.Frame(analysis_frame)
        summary_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        summary_frame.columnconfigure(0, weight=1)
        
        ttk.Label(summary_frame, text="AI Summary", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        
        self.summary_text = scrolledtext.ScrolledText(
            summary_frame,
            wrap=tk.WORD,
            height=6,
            font=("Helvetica", 10)
        )
        self.summary_text.grid(row=1, column=0, sticky="nsew")
        self.summary_text.config(state=tk.DISABLED)
        
        # Copy button
        self.copy_btn = ttk.Button(
            summary_frame,
            text="📋 Copy Summary",
            command=self._copy_summary,
            state=tk.DISABLED
        )
        self.copy_btn.grid(row=2, column=0, sticky="w", pady=(5, 0))
        
        # Sentiment Section
        sentiment_frame = ttk.Frame(analysis_frame)
        sentiment_frame.grid(row=0, column=1, sticky="nsew")
        sentiment_frame.columnconfigure(0, weight=1)
        
        ttk.Label(sentiment_frame, text="Sentiment Analysis", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        
        # Sentiment display
        self.sentiment_label = ttk.Label(
            sentiment_frame,
            text="No analysis yet",
            font=("Helvetica", 24)
        )
        self.sentiment_label.grid(row=1, column=0, pady=10)
        
        self.sentiment_details = ttk.Label(
            sentiment_frame,
            text="",
            font=("Helvetica", 11)
        )
        self.sentiment_details.grid(row=2, column=0, sticky="w")
        
        # Export button
        self.export_btn = ttk.Button(
            sentiment_frame,
            text="💾 Export Results",
            command=self._export_summary,
            state=tk.DISABLED
        )
        self.export_btn.grid(row=3, column=0, sticky="w", pady=(10, 0))
    
    def _create_status_bar(self):
        """Create status bar at the bottom."""
        self.status_var = tk.StringVar(value="Ready - Please enter your API key")
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            style="Status.TLabel",
            relief=tk.SUNKEN,
            padding=(5, 2)
        )
        self.status_bar.grid(row=1, column=0, sticky="ew")
    
    def _show_api_key_dialog(self):
        """Show dialog to enter API key."""
        dialog = tk.Toplevel(self.root)
        dialog.title("NewsAPI Key Required")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(
            dialog, 
            text="Enter your NewsAPI API Key:", 
            font=("Helvetica", 11)
        ).pack(pady=10)
        
        api_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=api_var, width=40, show="*")
        entry.pack(pady=5)
        entry.focus()
        
        def save_key():
            key = api_var.get().strip()
            if Validator.validate_api_key(key):
                self.news_fetcher = NewsFetcher(key)
                self.status_var.set("Ready - Enter a keyword to search news")
                dialog.destroy()
            else:
                messagebox.showerror(
                    "Invalid Key", 
                    "Please enter a valid NewsAPI key (get one free at newsapi.org)"
                )
        
        ttk.Button(dialog, text="Save", command=save_key).pack(pady=10)
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
    
    def _set_loading(self, loading: bool):
        """Toggle loading state."""
        if loading:
            self.progress.start()
            self.search_btn.config(state=tk.DISABLED)
            self.headlines_btn.config(state=tk.DISABLED)
        else:
            self.progress.stop()
            self.search_btn.config(state=tk.NORMAL)
            self.headlines_btn.config(state=tk.NORMAL)
    
    def _search_news(self):
        """Search news by keyword."""
        keyword = self.keyword_var.get().strip()
        
        if not Validator.validate_keyword(keyword):
            messagebox.showwarning("Invalid Input", "Please enter a search keyword")
            return
        
        if not self.news_fetcher:
            messagebox.showwarning("No API Key", "Please set your API key first")
            return
        
        self._set_loading(True)
        self.status_var.set(f"Searching for '{keyword}'...")
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._fetch_search_results, args=(keyword,))
        thread.daemon = True
        thread.start()
    
    def _fetch_search_results(self, keyword: str):
        """Fetch search results in background thread."""
        try:
            articles = self.news_fetcher.fetch_by_keyword(keyword)
            self.root.after(0, self._update_news_list, articles)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._set_loading, False)
    
    def _fetch_headlines(self):
        """Fetch top headlines."""
        if not self.news_fetcher:
            messagebox.showwarning("No API Key", "Please set your API key first")
            return
        
        self._set_loading(True)
        self.status_var.set("Fetching top headlines...")
        
        thread = threading.Thread(target=self._fetch_headlines_thread)
        thread.daemon = True
        thread.start()
    
    def _fetch_headlines_thread(self):
        """Fetch headlines in background thread."""
        try:
            articles = self.news_fetcher.fetch_top_headlines()
            self.root.after(0, self._update_news_list, articles)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._set_loading, False)
    
    def _update_news_list(self, articles: list):
        """Update the news list with fetched articles."""
        # Clear existing items
        for item in self.news_tree.get_children():
            self.news_tree.delete(item)
        
        self.current_articles = articles
        
        if not articles:
            self.status_var.set("No articles found")
            return
        
        # Insert articles
        for idx, article in enumerate(articles):
            date = self.news_fetcher.format_date(article.get("published_at", ""))
            self.news_tree.insert(
                "", 
                "end", 
                iid=str(idx),
                text=article.get("title", "No Title")[:80],
                values=(
                    article.get("source", "Unknown"),
                    date
                )
            )
        
        self.status_var.set(f"Found {len(articles)} articles")
    
    def _on_article_select(self, event=None):
        """Handle article selection."""
        selection = self.news_tree.selection()
        if not selection:
            return
        
        idx = int(selection[0])
        self.selected_article = self.current_articles[idx]
        
        # Update details
        article = self.selected_article
        
        self.detail_title.config(text=article.get("title", "No Title"))
        
        meta_text = f"Source: {article.get('source', 'Unknown')}\n"
        meta_text += f"Author: {article.get('author', 'Unknown')}\n"
        meta_text += f"Date: {self.news_fetcher.format_date(article.get('published_at', ''))}"
        self.detail_meta.config(text=meta_text)
        
        self.detail_desc.config(state=tk.NORMAL)
        self.detail_desc.delete(1.0, tk.END)
        self.detail_desc.insert(1.0, article.get("description", "No description available"))
        self.detail_desc.config(state=tk.DISABLED)
        
        # Enable buttons
        self.open_url_btn.config(state=tk.NORMAL)
        self.summarize_btn.config(state=tk.NORMAL)
        self.analyze_btn.config(state=tk.NORMAL)
        
        self.status_var.set(f"Selected: {article.get('title', '')[:50]}...")
    
    def _open_article_url(self):
        """Open article URL in browser."""
        if self.selected_article and self.selected_article.get("url"):
            webbrowser.open(self.selected_article["url"])
    
    def _summarize_article(self):
        """Generate summary for selected article."""
        if not self.selected_article:
            return
        
        content = self.selected_article.get("content", "") or self.selected_article.get("description", "")
        
        if not content:
            messagebox.showinfo("No Content", "This article has no content to summarize")
            return
        
        self.status_var.set("Generating summary...")
        self.summarize_btn.config(state=tk.DISABLED)
        
        # Run in thread
        thread = threading.Thread(target=self._summarize_thread, args=(content,))
        thread.daemon = True
        thread.start()
    
    def _summarize_thread(self, content: str):
        """Generate summary in background."""
        try:
            summary = self.summarizer.summarize(content)
            self.root.after(0, self._update_summary, summary)
        except Exception as e:
            self.root.after(0, self._show_error, f"Summarization failed: {str(e)}")
        finally:
            self.root.after(0, lambda: self.summarize_btn.config(state=tk.NORMAL))
    
    def _update_summary(self, summary: str):
        """Update summary display."""
        self.current_summary = summary
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state=tk.DISABLED)
        
        self.copy_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL)
        self.status_var.set("Summary generated successfully")
    
    def _analyze_sentiment(self):
        """Analyze sentiment of selected article."""
        if not self.selected_article:
            return
        
        content = (
            self.selected_article.get("content", "") 
            or self.selected_article.get("description", "")
            or self.selected_article.get("title", "")
        )
        
        if not content:
            messagebox.showinfo("No Content", "No content available for analysis")
            return
        
        self.status_var.set("Analyzing sentiment...")
        self.analyze_btn.config(state=tk.DISABLED)
        
        # Run in thread
        thread = threading.Thread(target=self._sentiment_thread, args=(content,))
        thread.daemon = True
        thread.start()
    
    def _sentiment_thread(self, content: str):
        """Analyze sentiment in background."""
        try:
            result = self.sentiment_analyzer.analyze(content)
            self.root.after(0, self._update_sentiment, result)
        except Exception as e:
            self.root.after(0, self._show_error, f"Sentiment analysis failed: {str(e)}")
        finally:
            self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
    
    def _update_sentiment(self, result: dict):
        """Update sentiment display."""
        self.current_sentiment = result
        
        self.sentiment_label.config(
            text=f"{result['emoji']} {result['label']}",
            foreground=result['color']
        )
        
        details = f"Score: {result['score']}\n"
        details += f"Confidence: {result['confidence']}"
        
        if 'details' in result:
            for key, value in result['details'].items():
                details += f"\n{key.capitalize()}: {value}"
        
        self.sentiment_details.config(text=details)
        self.export_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Sentiment: {result['label']} (Score: {result['score']})")
    
    def _copy_summary(self):
        """Copy summary to clipboard."""
        if self.current_summary:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_summary)
            self.status_var.set("Summary copied to clipboard!")
    
    def _export_summary(self):
        """Export current analysis to text file."""
        if not self.selected_article:
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        content = self.exporter.generate_export_content(
            self.selected_article,
            self.current_summary or "No summary generated",
            self.current_sentiment or {"label": "N/A", "emoji": "", "score": "N/A"}
        )
        
        if self.exporter.export_to_text(content, filepath):
            self.status_var.set(f"Exported to {filepath}")
            messagebox.showinfo("Export Successful", f"Results saved to:\n{filepath}")
    
    def _export_csv(self):
        """Export all articles to CSV."""
        if not self.current_articles:
            messagebox.showwarning("No Data", "No articles to export")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        if self.exporter.export_to_csv(self.current_articles, filepath):
            self.status_var.set(f"Exported to {filepath}")
            messagebox.showinfo("Export Successful", f"Articles saved to:\n{filepath}")
    
    def _show_error(self, message: str):
        """Display error message."""
        self.status_var.set(f"Error: {message}")
        messagebox.showerror("Error", message)
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About AI News Analyzer",
            "AI News Analyzer v1.0\n\n"
            "A desktop application for fetching, summarizing, and analyzing news articles.\n\n"
            "Features:\n"
            "• News search by keyword\n"
            "• AI-powered summarization\n"
            "• Sentiment analysis\n"
            "• Export capabilities\n\n"
            "Powered by NewsAPI, Transformers, and VADER"
        )


def main():
    """Main entry point."""
    root = tk.Tk()
    app = NewsAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()