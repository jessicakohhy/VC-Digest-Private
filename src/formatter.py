"""Markdown formatter for GitHub Issues."""

from datetime import datetime, timezone
from typing import Dict

import pytz

SGT = pytz.timezone("Asia/Singapore")


def format_digest(
    now: datetime,
    tldr: str,
    bucket_summaries: Dict[str, dict],
    is_weekend: bool,
) -> tuple[str, str]:
    """Return (issue_title, issue_body) for the daily digest."""
    sgt = now.astimezone(SGT)
    date_str = sgt.strftime("%A, %d %B %Y")
    edition = "Weekend Edition" if is_weekend else "Weekday Edition"

    title = f"VC Daily Digest — {date_str}"

    lines = [
        f"# VC Daily Digest",
        f"**{date_str}** · {edition} · _Generated {sgt.strftime('%H:%M SGT')}_",
        "",
        "---",
        "",
        "## 📋 TLDR",
        "",
        tldr,
        "",
        "---",
        "",
    ]

    for bucket_data in bucket_summaries.values():
        lines.append(f"## {bucket_data['name']}")
        lines.append("")
        stories = bucket_data.get("stories", [])

        if not stories:
            lines.append("_No significant stories in this window._")
        else:
            for story in stories:
                lock = " 🔒" if story.get("paywalled") else ""
                src = story["source"]
                url = story.get("url", "")
                src_link = f"[{src}]({url})" if url else src

                lines.append(f"- **{story['headline']}**{lock} · {src_link}")
                lines.append(f"  {story['summary']} *{story['vc_angle']}*")
                lines.append("")

        lines += ["---", ""]

    lines += [
        "_Want a deeper dive? Create an issue titled `Query: your topic` and add the `vc-query` label — "
        "the bot will post a reading list within minutes._",
    ]

    return title, "\n".join(lines)


def format_on_demand_comment(topic: str, content: str) -> str:
    """Return the comment body for an on-demand reading list."""
    sgt_now = datetime.now(SGT)
    return (
        f"## Reading List: {topic}\n\n"
        f"{content}\n\n"
        f"---\n"
        f"_Generated at {sgt_now.strftime('%H:%M SGT on %d %b %Y')}_"
    )
