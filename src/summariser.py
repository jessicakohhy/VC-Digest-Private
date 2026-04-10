"""Claude-powered summarisation for the digest and on-demand queries."""

import json
import anthropic
from typing import Dict, List


def summarise_bucket(
    bucket_name: str,
    bucket_desc: str,
    articles: List[Dict],
    client: anthropic.Anthropic,
) -> List[Dict]:
    """Select and summarise 3-4 top articles from a bucket using Claude."""
    if not articles:
        return []

    articles_text = ""
    for i, art in enumerate(articles[:15]):
        articles_text += f"\n[{i + 1}] {art['title']}\n"
        articles_text += f"Source: {art['source']} | URL: {art['url']}\n"
        if art["summary"]:
            articles_text += f"Preview: {art['summary'][:300]}\n"
        articles_text += "\n"

    prompt = f"""You are a VC analyst assistant creating a daily news digest for a Singapore-based venture capitalist.

Bucket: {bucket_name} — {bucket_desc}

Today's articles:
{articles_text}

Select the 3-4 most important articles for a VC investor. For each, provide:
1. A one-sentence summary of what happened (factual, specific)
2. A one-sentence "why it matters for a VC" insight (investment angle, market signal, or risk)

Return a JSON array — no other text:
[
  {{
    "index": <1-based article index>,
    "headline": "<original article title>",
    "summary": "<one sentence: what happened>",
    "vc_angle": "<one sentence: why this matters for a VC>"
  }}
]

Prioritise: funding activity, regulatory shifts, technology inflection points, competitive dynamics, market structure changes."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        selected = json.loads(response.content[0].text)
        result = []
        for item in selected:
            idx = item["index"] - 1
            if 0 <= idx < len(articles):
                orig = articles[idx]
                result.append({
                    "headline": item["headline"],
                    "summary": item["summary"],
                    "vc_angle": item["vc_angle"],
                    "source": orig["source"],
                    "url": orig["url"],
                    "paywalled": orig["paywalled"],
                })
        return result
    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        print(f"  [summariser] Parse error for {bucket_name}: {exc}")
        return []


def generate_tldr(bucket_summaries: Dict[str, dict], client: anthropic.Anthropic) -> str:
    """Generate a 3-5 line TLDR covering the single most important story per bucket."""
    top_stories = []
    for bucket_data in bucket_summaries.values():
        stories = bucket_data.get("stories", [])
        if stories:
            top = stories[0]
            top_stories.append(
                f"- [{top['source']}] {top['headline']}: {top['summary']} {top['vc_angle']}"
            )

    if not top_stories:
        return "_No significant stories today._"

    prompt = f"""You are a VC analyst writing a morning briefing for a Singapore-based venture capitalist.

Top stories today:
{chr(10).join(top_stories)}

Write a TLDR of 3-5 bullet points. Each bullet must:
- Lead with the "so what for a VC" takeaway — not just a restatement of the headline
- Be one line maximum
- Be specific (name the company, country, or figure if relevant)

Return only markdown bullet points (using - ). No heading, no preamble."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()


def handle_on_demand_query(topic: str, client: anthropic.Anthropic) -> str:
    """Generate a structured reading list for an on-demand topic request."""
    prompt = f"""You are a VC analyst assistant for a Singapore-based venture capitalist.

The user requests a reading list on: "{topic}"

Produce a structured reading list in two sections:

### Recent News (last 30 days)
3-5 bullets on recent developments. Format each as:
- **[Source]** "Headline or story description" — One sentence summary. *VC angle: why this matters.*

### Longer Reads
2-3 evergreen essays, research reports, or deep dives. Format each as:
- **[Author / Publication]** "Title" — One sentence on why to read it.

Use real publication names (TechInAsia, Bloomberg, a16z, McKinsey, etc.). Be specific. Focus on content relevant to: venture capital, Southeast Asia, Singapore, technology, AI, and market dynamics.

Return only the markdown content, no preamble."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()
