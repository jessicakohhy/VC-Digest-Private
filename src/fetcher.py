"""RSS feed fetcher — pulls articles from all configured sources."""

import re
import time
import yaml
import feedparser
from datetime import datetime, timedelta, timezone
from typing import Dict, List


HOURS_LOOKBACK = 24


def load_sources(config_path: str = "config/sources.yml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def _parse_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            return datetime(*val[:6], tzinfo=timezone.utc)
    return None


def fetch_feed(url: str, name: str, paywalled: bool, lookback_hours: int = HOURS_LOOKBACK) -> List[Dict]:
    """Fetch a single RSS feed and return articles published within lookback window."""
    try:
        d = feedparser.parse(url, request_headers={"User-Agent": "VCDigestBot/1.0"})
        cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        articles = []

        for entry in d.entries[:20]:
            pub_date = _parse_date(entry)
            if pub_date and pub_date < cutoff:
                continue  # too old

            raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            summary = _clean_html(raw_summary)[:400]

            articles.append({
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", ""),
                "summary": summary,
                "published": pub_date.isoformat() if pub_date else None,
                "source": name,
                "paywalled": paywalled,
            })

        return articles

    except Exception as exc:
        print(f"  [fetcher] Error fetching {name}: {exc}")
        return []


def fetch_all_buckets(sources: dict) -> Dict[str, dict]:
    """Fetch all RSS feeds, returning articles organised by bucket key."""
    result = {}

    for bucket_key, bucket_cfg in sources["buckets"].items():
        articles = []
        for feed in bucket_cfg["feeds"]:
            feed_articles = fetch_feed(feed["url"], feed["name"], feed.get("paywalled", False))
            articles.extend(feed_articles)
            time.sleep(0.3)  # polite crawl delay

        result[bucket_key] = {
            "name": bucket_cfg["name"],
            "description": bucket_cfg["description"],
            "articles": articles,
        }
        print(f"  [fetcher] {bucket_cfg['name']}: {len(articles)} articles")

    return result
