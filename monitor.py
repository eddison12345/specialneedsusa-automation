#!/usr/bin/env python3
"""
ABA Industry News Monitor for specialneedsusa.com
Robust version for GitHub Actions
"""

import os
import sys
from datetime import datetime
from firecrawl import Firecrawl
from agentmail import AgentMail

# Configuration
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY")
SEND_TO = "admin@specialneedsusa.com"
INBOX_ID = "trickytruck172@agentmail.to"

if not FIRECRAWL_API_KEY or not AGENTMAIL_API_KEY:
    print("❌ Missing API keys")
    sys.exit(1)

print(f"🚀 ABA News Monitor started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def get_aba_news():
    print("🔍 Searching for recent ABA news...")
    fc = Firecrawl(api_key=FIRECRAWL_API_KEY)
    
    try:
        results = fc.search(
            query="ABA therapy OR BCBA OR \"applied behavior analysis\" OR autism insurance",
            limit=10
        )
        
        items = results.data if hasattr(results, 'data') else getattr(results, 'data', results.get("data", []))
        articles = []
        
        for item in list(items)[:7]:
            url = getattr(item, 'url', None) or (item.get('url') if isinstance(item, dict) else None)
            if not url:
                continue
                
            title = getattr(item, 'title', None) or item.get('title', 'No Title')
            
            try:
                page = fc.scrape(url=url, formats=["markdown"], only_main_content=True)
                content = getattr(page, 'markdown', None) or (page.get('markdown') if isinstance(page, dict) else str(page))
                summary = content[:650] if content else "No content available."
            except Exception:
                summary = "Could not extract full article."
            
            articles.append({
                "title": title,
                "url": url,
                "source": url.split("//")[-1].split("/")[0].replace("www.", ""),
                "summary": summary
            })
            print(f"  ✓ {title[:60]}...")
        
        return articles
    except Exception as e:
        print(f"❌ Search error: {e}")
        return []

def build_report(articles):
    lines = [f"# ABA News Report - {datetime.now().strftime('%B %d, %Y')}", "",
             "Weekly update for specialneedsusa.com ABA directory.\n"]
    
    if not articles:
        lines.append("No new articles found this period.")
    else:
        for i, a in enumerate(articles, 1):
            lines.append(f"## {i}. {a['title']}")
            lines.append(f"**Source:** {a['source']}")
            lines.append(f"**URL:** {a['url']}\n")
            lines.append(a['summary'])
            lines.append("\n**Opportunity:** Good for newsjacking or creating local clinic content.\n")
            lines.append("─" * 50 + "\n")
    
    lines.append("\nGenerated automatically.")
    return "\n".join(lines)

def send_report(text_report):
    print("📧 Sending email via AgentMail...")
    try:
        client = AgentMail(api_key=AGENTMAIL_API_KEY)
        html_report = "<pre style='white-space:pre-wrap; font-family:Arial; line-height:1.6;'>" + \
                     text_report.replace("\n", "<br>") + "</pre>"
        
        client.inboxes.messages.send(
            inbox_id=INBOX_ID,
            to=SEND_TO,
            subject=f"ABA News Monitor - {datetime.now().strftime('%B %d, %Y')}",
            text=text_report,
            html=html_report
        )
        print("✅ Report sent to admin@specialneedsusa.com")
    except Exception as e:
        print(f"❌ Email failed: {e}")
        print("--- Report content ---")
        print(text_report)

if __name__ == "__main__":
    articles = get_aba_news()
    report = build_report(articles)
    send_report(report)
    print("🏁 ABA News Monitor completed.")
