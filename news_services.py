# news_services.py

import feedparser
import sqlite3
from datetime import datetime
import csv
import json
from langdetect import detect, LangDetectException

DB_NAME = "news.db"
SUMMARY_JSON_FILE = "news_summary.json"

def create_table():
    """Create the news table in the SQLite database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS news")
        cursor.execute("""
            CREATE TABLE news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                published TEXT,
                source TEXT,
                country TEXT,
                summary TEXT,
                url TEXT UNIQUE,
                language TEXT
            )
        """)
        conn.commit()

def format_date(date_str):
    try:
        return str(datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z"))
    except Exception:
        return date_str

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

def fetch_and_store_news(rss_feeds):
    print("🔄 Fetching news from all RSS feeds...")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        for source, country, url in rss_feeds:
            print(f"📡 Fetching from: {source} ({country})")
            try:
                feed = feedparser.parse(url)
                if feed.bozo:
                    print(f"⚠️ Failed to parse feed: {url}")
                    continue

                for entry in feed.entries:
                    title = entry.get("title", "N/A")
                    summary = entry.get('summary') or entry.get('description') or entry.get('content', [{}])[0].get('value') or ''
                    link = entry.get("link", "N/A")
                    published = entry.get("published", "N/A")
                    published = format_date(published)
                    lang = detect_language(title + " " + summary)

                    cursor.execute("SELECT 1 FROM news WHERE url=?", (link,))
                    if cursor.fetchone():
                        continue  # skip duplicates

                    cursor.execute("""
                        INSERT INTO news (title, published, source, country, summary, url, language)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (title, published, source, country, summary, link, lang))

                conn.commit()
            except Exception as e:
                print(f"❌ Error fetching from {source}: {e}")

    print("✅ News fetching and storing completed.")

def export_to_csv(filename="news_export.csv"):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, published, source, country, summary, url, language FROM news")
        rows = cursor.fetchall()

    with open(filename, mode="w", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["title", "published", "source", "country", "summary", "url", "language"])
        writer.writerows(rows)
    print(f"✅ Data exported to CSV file: {filename}")

def export_to_json(filename="news_export.json"):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, published, source, country, summary, url, language FROM news")
        rows = cursor.fetchall()

    news_list = []
    for row in rows:
        news_list.append({
            "title": row[0],
            "published": row[1],
            "source": row[2],
            "country": row[3],
            "summary": row[4],
            "url": row[5],
            "language": row[6]
        })

    with open(filename, mode="w", encoding="utf-8") as jsonfile:
        json.dump(news_list, jsonfile, ensure_ascii=False, indent=4)
    print(f"✅ Data exported to JSON file: {filename}")

def generate_and_save_summary_json():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT country, GROUP_CONCAT(DISTINCT source), COUNT(*), MIN(published)
            FROM news
            GROUP BY country
        """)
        rows = cursor.fetchall()

    summary = []
    for row in rows:
        country, agencies, total_articles, earliest_date = row
        try:
            dt = datetime.strptime(earliest_date, "%Y-%m-%d %H:%M:%S")
            earliest_date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            earliest_date_str = "N/A"
        summary.append({
            "country": country,
            "news_agencies": agencies,
            "total_articles": total_articles,
            "historical_since": earliest_date_str
        })

    with open(SUMMARY_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)
    print(f"✅ Summary JSON saved as {SUMMARY_JSON_FILE}")
