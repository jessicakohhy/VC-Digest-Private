"""
Main entry point.

Usage:
  python digest.py digest              # run the daily digest
  python digest.py on-demand <issue_number> <topic>
"""

import os
import sys
from datetime import datetime, timezone

import anthropic
import pytz

from fetcher import fetch_all_buckets, load_sources
from formatter import format_digest, format_on_demand_comment
from github_client import GitHubClient
from summariser import generate_tldr, handle_on_demand_query, summarise_bucket

SGT = pytz.timezone("Asia/Singapore")

# Singapore public holidays 2025-2026 (YYYY-MM-DD in SGT)
SG_PUBLIC_HOLIDAYS = {
    # 2025
    "2025-01-01", "2025-01-29", "2025-01-30",
    "2025-04-18", "2025-05-01", "2025-05-12",
    "2025-06-07", "2025-08-09", "2025-10-20",
    "2025-12-25",
    # 2026
    "2026-01-01", "2026-02-17", "2026-02-18",
    "2026-04-03", "2026-05-01", "2026-05-31",
    "2026-06-26", "2026-08-10", "2026-11-09",
    "2026-12-25",
}


def is_weekend_or_holiday(utc_now: datetime) -> bool:
    sgt = utc_now.astimezone(SGT)
    date_str = sgt.strftime("%Y-%m-%d")
    return sgt.weekday() >= 5 or date_str in SG_PUBLIC_HOLIDAYS


def run_digest():
    now = datetime.now(timezone.utc)
    is_weekend = is_weekend_or_holiday(now)
    print(f"Running digest — {now.isoformat()} (weekend/holiday: {is_weekend})")

    claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    gh = GitHubClient()
    gh.ensure_labels()

    print("Fetching RSS feeds...")
    sources = load_sources()
    all_buckets = fetch_all_buckets(sources)

    print("Summarising with Claude...")
    bucket_summaries: dict = {}
    for key, data in all_buckets.items():
        print(f"  {data['name']}...")
        stories = summarise_bucket(data["name"], data["description"], data["articles"], claude)
        bucket_summaries[key] = {"name": data["name"], "stories": stories}

    print("Generating TLDR...")
    tldr = generate_tldr(bucket_summaries, claude)

    title, body = format_digest(now, tldr, bucket_summaries, is_weekend)

    print(f"Posting issue: {title}")
    issue = gh.create_issue(title, body, labels=["daily-digest"])
    print(f"Done → {issue['html_url']}")


def run_on_demand(issue_number: int, topic: str):
    print(f"On-demand query: '{topic}' (issue #{issue_number})")

    claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    gh = GitHubClient()

    content = handle_on_demand_query(topic, claude)
    comment = format_on_demand_comment(topic, content)
    gh.create_comment(issue_number, comment)
    gh.close_issue(issue_number)
    print(f"Posted reading list on issue #{issue_number}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "digest"

    if mode == "digest":
        run_digest()
    elif mode == "on-demand":
        if len(sys.argv) < 4:
            print("Usage: digest.py on-demand <issue_number> <topic>")
            sys.exit(1)
        run_on_demand(int(sys.argv[2]), sys.argv[3])
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
