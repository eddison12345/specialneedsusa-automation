#!/usr/bin/env python3
"""
ABA News Monitor for specialneedsusa.com
Runs weekly via GitHub Actions
"""

import os
from datetime import datetime
from firecrawl import FirecrawlApp
from agentmail import AgentMail

# Configuration
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY")
SEND_TO_EMAIL = "admin@specialneedsusa.com"
INBOX_ID = "trickytruck172@agentmail.to"

if not FIRECRAWL_API_KEY or not AGENTMAIL_API_KEY:
    raise ValueError("Missing FIRECRAWL_API_KEY or AGENTMAIL_API_KEY")

def scrape_recent_news():
    print("🔎 Searching for recent ABA industry news...")
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    
    # Use search to find recent articles
    results = app.search(
        query="ABA therapy OR BCBA OR \"autism\" insurance OR \"autism legislation\" OR \"applied behavior analysis\"",
        limit=12
    )
    
    articles = []
    for item in results.get("data", [])[:8]:
        if not item.get("url"):
            continue
        try:
            page = app.scrape(
                url=item["url"],
                formats=["markdown"],
                only_main_content=True
            )
            articles.append({
                "title": item.get("title", "Untitled"),
                "url": item["url"],
                "source": item.get("source") or item.get("url").split("/")[2],
                "date": item.get("published_date", "Recent"),
                "summary": page.markdown[:600] if hasattr(page, 'markdown') else str(page)[:600]
            })
            print(f"✓ Scraped: {item.get('title', 'Article')}")
        except Exception as e:
            print(f"⚠️ Failed to scrape {item.get('url')}: {e}")
    
    return articles

def generate_report(articles):
    report = f"# ABA Industry News Report - {datetime.now().strftime('%B %d, %Y')}\n\n"
    report += "Latest relevant news for specialneedsusa.com (ABA therapy directory).\n\n"
    
    for i, article in enumerate(articles, 1):
        report += f"## {i}. {article['title']}\n"
        report += f"**Source:** {article['source']} | **Date:** {article['date']}\n"
        report += f"**Link:** {article['url']}\n\n"
        report += f"{article['summary']}\n\n"
        report += "**Newsjacking Ideas:**\n"
        report += "- Create a directory listing highlight or blog post referencing this news\n"
        report += "- Target clinics in affected states with updated listings\n\n"
        report += "---\n\n"
    
    report += "\n---\nReport generated automatically by GitHub Actions."
    return report

def send_email(report):
    print("📧 Sending report via AgentMail...")
    client = AgentMail(api_key=AGENTMAIL_API_KEY)
    
    response = client.inboxes.messages.send(
        inbox_id=INBOX_ID,
        to=SEND_TO_EMAIL,
        subject=f"ABA News Monitor • {datetime.now().strftime('%B %d, %Y')}",
        text=report,
        html=f"<pre style='white-space: pre-wrap; font-family: system-ui; line-height: 1.6;'>{report.replace(chr(10), '<br>')}</pre>"
    )
    print("✅ Email sent successfully!")

if __name__ == "__main__":
    print("🚀 Starting ABA News Monitor...")
    articles = scrape_recent_news()
    
    if not articles:
        print("⚠️ No articles found.")
        exit(1)
    
    report = generate_report(articles)
    send_email(report)
    print("🎉 ABA News Monitor completed successfully.")
