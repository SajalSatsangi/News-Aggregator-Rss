---
# 🌍 News Aggregator with RSS Feeds

This project is a **Flask-based news aggregator** that collects news articles from various **RSS feeds** around the world, detects their language, stores them in a local SQLite database, and exports them to both CSV and JSON formats. It also provides a downloadable **summary JSON** file for insights such as total articles, sources, and earliest publication dates per country.
---

## 📌 Features

- Collects news from multiple international RSS feeds.
- Extracts key details: title, publication date, source, country, summary, URL, and language.
- Detects article language using `langdetect`.
- Automatically updates the database every 5 hours using APScheduler.
- Exports news data to:

  - `news_export.csv`
  - `news_export.json`
  - `news_summary.json` – grouped summary per country

- REST API to fetch and filter news by country, language, or date.
- HTML frontend (`static/index.html`) for basic UI interaction.
- Supports file downloads via `/news/summary/download`.

---

## 📁 Project Structure

```
.
├── app.py                   # Main Flask backend
├── rss_feeds.py             # Contains the list of RSS feeds (source, country, url)
├── news_services.py         # Logic to fetch, store, export news data
├── static/
│   └── index.html           # Basic frontend interface
├── news.db                  # SQLite database file (auto-generated)
├── news_export.csv          # Exported CSV file (auto-generated)
├── news_export.json         # Exported JSON file (auto-generated)
├── news_summary.json        # Summary JSON (auto-generated)
├── requirements.txt         # Python dependencies
└── README.md                # You're reading this
```

---

## 📊 Example Summary Data (`news_summary.json`)

```json
[
  {
    "country": "USA",
    "news_agencies": "CNN, Fox News, NYT",
    "total_articles": 1245,
    "historical_since": "2021-03-04"
  },
  {
    "country": "India",
    "news_agencies": "NDTV, Times of India",
    "total_articles": 948,
    "historical_since": "2022-01-15"
  }
]
```

---

## 🌐 API Endpoints

| Endpoint                 | Method | Description                                                                         |
| ------------------------ | ------ | ----------------------------------------------------------------------------------- |
| `/`                      | GET    | Serves the HTML page                                                                |
| `/news`                  | GET    | Fetches news with optional filters: `country`, `language`, `start_date`, `end_date` |
| `/news/summary/download` | GET    | Download the `news_summary.json` file                                               |

**Example query:**
`/news?country=india&language=en&start_date=2024-01-01&end_date=2024-12-31`

---

## 🛠 Dependencies

Install with:

```bash
pip install -r requirements.txt
```

**`requirements.txt` includes:**

```
Flask==2.3.2
feedparser==6.0.11
langdetect==1.0.9
APScheduler==3.10.4
```

---

## 🚀 How to Run This Project

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/news-aggregator-rss.git
cd news-aggregator-rss
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
python app.py
```

The app will:

- Fetch and store the latest news from all RSS feeds.
- Create and/or update `news.db`, `news_export.csv`, `news_export.json`, and `news_summary.json`.
- Start the server at `http://localhost:8000`.

---

## 💡 Bonus Features Implemented

- 🕒 **Scheduled fetching** every 5 hours using APScheduler.
- 🌍 **Language detection** for each article.
- 📥 **Summary JSON** that groups total articles per country, their sources, and history.
- 📦 **Auto-export** to CSV and JSON formats.

---

## 🧩 Issues Encountered

- Some RSS feeds may not consistently provide summaries or publication dates.
- Language detection may return `"unknown"` if not enough text is available.
- Timezone inconsistencies were handled using basic string parsing for dates.

---
