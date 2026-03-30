#!/usr/bin/env python3
"""
ABA News Monitor for specialneedsusa.com
Runs weekly via GitHub Actions
"""

import os
import json
from datetime import datetime
from firecrawl import FirecrawlApp
from agentmail import AgentMail

# Load environment variables
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY")
SEND_TO_EMAIL = "admin@specialneedsusa.com"
INBOX_ID = "trickytruck172@agentmail.to"

if not FIRECRAWL_API_KEY or not AGENTMAIL_API_KEY:
    raise ValueError("Missing API keys")

def scrape_news():
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    
    # Search for recent ABA / autism industry news
    search_result = app.search(
        query="ABA therapy OR BCBA OR autism insurance OR autism legislation after:2 days",
        limit=10
    )
    
    articles = []
    for item in search_result.get("data", [])[:7]:
        if "url" in item:
            try:
                scraped = app.scrape(
                    url=item["url"],
                    formats=["markdown"],
                    only_main_content=True
                )
                articles.append({
                    "title": item.get("title", "No title"),
                    "url": item["url"],
                    "source": item.get("source", "Unknown"),
                    "date": item.get("published_date", "Recent"),
                    "summary": scraped.markdown[:800] if hasattr(scraped, 'markdown') else "No content available",
                    "newsjack_ideas": "Potential content ideas for specialneedsusa.com directory + clinic listings."
                })
            except Exception as e:
                print(f"Error scraping {item.get('url')}: {e}")
    
    return articles

def generate_report(articles):
    report = f"# ABA Industry News Report - {datetime.now().strftime('%B %d, %Y')}\n\n"
    report += "Here are the top recent stories relevant to ABA therapy clinics and specialneedsusa.com:\n\n"
    
    for i, article in enumerate(articles, 1):
        report += f"## {i}. {article['title']}\n"
        report += f"**Source:** {article['source']} | {article['date']}\n"
        report += f"**Link:** {article['url']}\n\n"
        report += f"{article['summary'][:500]}...\n\n"
        report += "**Content ideas for specialneedsusa.com:**\n"
        report += "- " + article.get("newsjack_ideas", "News-jacking opportunity") + "\n\n"
        report += "---\n\n"
    
    report += "\nReport generated automatically by specialneedsusa-automation."
    return report

def send_report(report):
    client = AgentMail(api_key=AGENTMAIL_API_KEY)
    
    client.inboxes.messages.send(
        inbox_id=INBOX_ID,
        to=SEND_TO_EMAIL,
        subject=f"ABA News Monitor - {datetime.now().strftime('%B %d, %Y')}",
        text=report,
        html=f"<pre style='white-space: pre-wrap; font-family: Arial'>{report}</pre>"
    )
    print("✅ Report sent successfully to admin@specialneedsusa.com")

if __name__ == "__main__":
    print("🚀 Starting ABA News Monitor...")
    articles = scrape_news()
    report = generate_report(articles)
    send_report(report)
    print("✅ ABA News Monitor completed.")
