# app.py

import os
from flask import Flask, jsonify, request, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler

from rss_feeds import rss_feeds
import news_services

app = Flask(__name__, static_folder='static')

@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

@app.route('/news')
def get_news():
    country = request.args.get('country')
    language = request.args.get('language')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = "SELECT * FROM news WHERE 1=1"
    params = []

    if country:
        query += " AND LOWER(country) = ?"
        params.append(country.lower())
    if language:
        query += " AND LOWER(language) = ?"
        params.append(language.lower())
    if start_date:
        query += " AND published >= ?"
        params.append(start_date)
    if end_date:
        query += " AND published <= ?"
        params.append(end_date)

    query += " ORDER BY published DESC"

    with news_services.sqlite3.connect(news_services.DB_NAME) as conn:
        conn.row_factory = news_services.sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        news = [dict(row) for row in rows]
    return jsonify(news)

@app.route('/news/summary/download')
def download_news_summary():
    if os.path.exists(news_services.SUMMARY_JSON_FILE):
        return send_from_directory(directory=os.getcwd(), filename=news_services.SUMMARY_JSON_FILE, as_attachment=True)
    else:
        return jsonify({"error": "Summary file not found. Please wait for the next update."}), 404

def scheduled_job():
    print("🕒 Scheduled job started.")
    news_services.fetch_and_store_news(rss_feeds)
    news_services.export_to_csv()
    news_services.export_to_json()
    news_services.generate_and_save_summary_json()
    print("🕒 Scheduled job finished.")

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, 'interval', hours=5)
scheduler.start()

if __name__ == "__main__":
    news_services.create_table()
    scheduled_job()  # run once before starting the server
    app.run(host='0.0.0.0', port=8000, debug=True)
