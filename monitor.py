#!/usr/bin/env python3
"""
ABA Industry News Monitor for specialneedsusa.com
Reliable version for GitHub Actions + Firecrawl v4+
"""

import os
import sys
from datetime import datetime
from firecrawl import Firecrawl
from agentmail import AgentMail

# === Configuration ===
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY")
SEND_TO = "admin@specialneedsusa.com"
INBOX_ID = "trickytruck172@agentmail.to"

if not FIRECRAWL_API_KEY or not AGENTMAIL_API_KEY:
    print("❌ Missing API keys in environment")
    sys.exit(1)

print(f"🚀 Starting ABA News Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M')}")

def scrape_recent_aba_news():
    print("🔍 Searching for recent ABA / autism news...")
    fc = Firecrawl(api_key=FIRECRAWL_API_KEY)
    
    try:
        results = fc.search(
            query="ABA therapy OR BCBA OR \"applied behavior analysis\" OR autism insurance OR autism legislation",
            limit=10,
            scrape_options={"formats": ["markdown"]}
        )
        
        items = results.data if hasattr(results, 'data') else getattr(results, 'data', results.get("data", []))
        articles = []
        
        for item in items[:7]:
            url = getattr(item, 'url', None) or item.get('url') if isinstance(item, dict) else None
            if not url:
                continue
                
            title = getattr(item, 'title', None) or item.get('title', 'Untitled')
            print(f"  → Found: {title}")
            
            try:
                page = fc.scrape(url=url, formats=["markdown"], only_main_content=True)
                markdown = getattr(page, 'markdown', None) or page.get('markdown', '') if isinstance(page, dict) else str(page)
                
                articles.append({
                    "title": title,
                    "url": url,
                    "source": url.split("/")[2].replace("www.", ""),
                    "summary": markdown[:650] + "..." if markdown else "No content extracted"
                })
            except Exception as scrape_err:
                print(f"    ⚠️ Could not scrape full article: {scrape_err}")
                articles.append({"title": title, "url": url, "source": url.split("/")[2].replace("www.", ""), "summary": "Content could not be extracted."})
        
        print(f"✅ Successfully processed {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

def create_report(articles):
    report = f"# ABA Industry News Report — {datetime.now().strftime('%B %d, %Y')}\n\n"
    report += "Weekly summary for specialneedsusa.com (ABA therapy clinic directory)\n\n"
    
    if not articles:
        report += "No recent articles found this week.\n"
        return report
    
    for i, article in enumerate(articles, 1):
        report += f"## {i}. {article['title']}\n"
        report += f"**Source:** {article['source']}\n"
        report += f"**Link:** {article['url']}\n\n"
        report += f"{article['summary']}\n\n"
        report += "**Newsjacking Opportunity:** Create targeted content or update clinic listings based on this development.\n"
        report += "─" * 60 + "\n\n"
    
    report += "\nReport generated automatically via Firecrawl + GitHub Actions."
    return report

def send_report(report_text):
    print("📧 Sending report via AgentMail...")
    try:
        client = AgentMail(api_key=AGENTMAIL_API_KEY)
        client.inboxes.messages.send(
            inbox_id=INBOX_ID,
            to=SEND_TO,
            subject=f"ABA News Monitor • {datetime.now().strftime('%B %d, %Y')}",
            text=report_text,
            html=f"<pre style='white-space:pre-wrap;font-family:Arial;line-height:1.6'>{report_text.replace('\n', '<br>')}</pre>"
        )
        print("✅ Report successfully sent to admin@specialneedsusa.com")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print(report_text)  # fallback: print to logs

if __name__ == "__main__":
    articles = scrape_recent_aba_news()
    report = create_report(articles)
    send_report(report)
    print("🎉 ABA News Monitor finished.")
