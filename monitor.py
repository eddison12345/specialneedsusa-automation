#!/usr/bin/env python3
"""
ABA Industry News Monitor for specialneedsusa.com
FINAL robust version for GitHub Actions + Firecrawl v4
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
            query="ABA therapy OR BCBA OR \"applied behavior analysis\" OR autism insurance OR autism legislation",
            limit=12
        )
        
        # Robust handling for Firecrawl v4 response
        if hasattr(results, 'data'):
            items = results.data
        elif isinstance(results, dict):
            items = results.get('data', [])
        else:
            items = []
        
        articles = []
        
        for item in list(items)[:8]:
            # Handle both Pydantic model and dict
            if hasattr(item, 'url'):
                url = item.url
                title = getattr(item, 'title', 'Untitled')
            elif isinstance(item, dict):
                url = item.get('url')
                title = item.get('title', 'Untitled')
            else:
                continue
                
            if not url:
                continue
                
            print(f"  → Found: {title[:60]}...")
            
            try:
                page = fc.scrape(url=url, formats=["markdown"], only_main_content=True)
                content = getattr(page, 'markdown', None) or (page.get('markdown') if isinstance(page, dict) else '')
                summary = (content[:700] + "...") if content else "No content extracted."
            except Exception as scrape_err:
                print(f"    ⚠️ Scrape failed: {scrape_err}")
                summary = "Content could not be retrieved."
            
            articles.append({
                "title": title,
                "url": url,
                "source": url.split("//")[-1].split("/")[0].replace("www.", ""),
                "summary": summary
            })
        
        print(f"✅ Collected {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"❌ Major search error: {e}")
        import traceback
        traceback.print_exc()
        return []

def build_report(articles):
    lines = [f"# ABA Industry News Report — {datetime.now().strftime('%B %d, %Y')}", "",
             "Weekly summary for specialneedsusa.com (ABA therapy directory & clinics).\n"]
    
    if not articles:
        lines.append("⚠️ No articles were found this run. This may be temporary.")
    else:
        for i, article in enumerate(articles, 1):
            lines.extend([
                f"## {i}. {article['title']}",
                f"**Source:** {article['source']}",
                f"**Link:** {article['url']}\n",
                article['summary'],
                "\n**Newsjacking Idea:** Reference this in a blog post or update clinic listings in affected states.",
                "─" * 60 + "\n"
            ])
    
    lines.append("\nReport generated automatically using Firecrawl + GitHub Actions.")
    return "\n".join(lines)

def send_report(text_report):
    print("📧 Sending report via AgentMail...")
    try:
        client = AgentMail(api_key=AGENTMAIL_API_KEY)
        html_version = "<pre style='white-space:pre-wrap;font-family:Arial;line-height:1.6'>" + \
                      text_report.replace("\n", "<br>") + "</pre>"
        
        client.inboxes.messages.send(
            inbox_id=INBOX_ID,
            to=SEND_TO,
            subject=f"ABA News Monitor • {datetime.now().strftime('%B %d, %Y')}",
            text=text_report,
            html=html_version
        )
        print("✅ Email successfully sent to admin@specialneedsusa.com")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    articles = get_aba_news()
    report = build_report(articles)
    send_report(report)
    print("🏁 ABA News Monitor completed.")
