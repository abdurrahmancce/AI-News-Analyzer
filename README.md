# 📰 AI News Analyzer

An AI-powered desktop application built with Python and Tkinter that allows users to fetch real-time news, generate AI-based summaries, perform sentiment analysis, and export results.

## 📌 Features

### 🔍 News Search

* Search news articles using keywords.
* Fetch top headlines from NewsAPI.
* View article title, source, author, publication date, and description.

### 🤖 AI-Powered Summarization

* Generate concise summaries of news articles.
* Uses Hugging Face Transformers when available.
* Falls back to extractive summarization if AI models are unavailable.

### 😊 Sentiment Analysis

* Analyze article sentiment as:

  * Positive
  * Negative
  * Neutral
* Displays sentiment score and confidence level.
* Uses VADER Sentiment Analyzer with TextBlob fallback support.

### 📊 Article Management

* Browse articles in a structured interface.
* View article details instantly.
* Open original articles directly in a web browser.

### 💾 Export Functionality

* Export analysis reports to TXT files.
* Export fetched articles to CSV format.
* Save summaries and sentiment analysis results.

### ⚡ Responsive User Experience

* Multi-threaded operations.
* Non-blocking GUI during API requests.
* Status updates and loading indicators.

---

## 🛠️ Technologies Used

* Python 3
* Tkinter
* NewsAPI
* Requests
* Transformers (Hugging Face)
* VADER Sentiment Analyzer
* TextBlob
* CSV
* Threading

---

## 📂 Project Structure

```text
AI-News-Analyzer/
│
├── main.py               # Main Tkinter GUI
├── news_fetcher.py       # NewsAPI integration
├── summarizer.py         # AI article summarization
├── sentiment.py          # Sentiment analysis
├── utils.py              # Utility functions and exporters
│
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/AI-News-Analyzer.git
cd AI-News-Analyzer
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install requests
pip install transformers
pip install torch
pip install vaderSentiment
pip install textblob
```

Or:

```bash
pip install -r requirements.txt
```

---

## 🔑 NewsAPI Setup

1. Visit:

https://newsapi.org

2. Create a free account.

3. Generate your API key.

4. Launch the application and enter the API key when prompted.

---

## ▶️ Running the Application

```bash
python main.py
```

---

## 📖 How to Use

1. Launch the application.
2. Enter your NewsAPI key.
3. Search for any news topic.
4. Select an article from the list.
5. Click **Summarize** to generate an AI summary.
6. Click **Analyze Sentiment** to evaluate sentiment.
7. Export results if needed.

---

## 📷 Main Functionalities

### News Fetching

* Search by keyword.
* Fetch top headlines.
* Display article metadata.

### Summarization

* AI-generated summaries.
* Automatic fallback mechanism.

### Sentiment Analysis

* Positive, Negative, Neutral detection.
* Confidence scoring.

### Export

* TXT report generation.
* CSV article export.

---

## 🎯 Learning Outcomes

This project demonstrates:

* GUI Development with Tkinter
* API Integration
* Natural Language Processing (NLP)
* Sentiment Analysis
* Multi-threading
* Object-Oriented Programming
* File Handling
* Software Architecture Design

---

## 🔮 Future Improvements

* Dark Mode
* News Category Filters
* Voice-Based News Reading
* Article Bookmarking
* PDF Export
* Data Visualization Dashboard
* Multi-Language Support

---

## 👨‍💻 Author

**Abdur Rahman**

Computer & Communication Engineering Student

GitHub:
https://github.com/abdurrahmancce

LinkedIn:
https://www.linkedin.com/in/abdur-rahman-akash26/

---

## 📜 License

This project is developed for educational and portfolio purposes.
Feel free to modify and enhance it for your own learning.
