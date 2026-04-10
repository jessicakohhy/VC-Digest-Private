# VC Daily Digest — Setup Guide

## How it works

| What | How |
|------|-----|
| **Delivery channel** | GitHub Issues on a private repo |
| **Scheduler** | GitHub Actions (free, no extra hosting) |
| **AI** | Claude API (`claude-sonnet-4-6`) |
| **On-demand queries** | Create an Issue → bot replies as a comment |

---

## Step 1 — Create a private GitHub repo

Create a new **private** repository, e.g. `yourname/vc-digest-private`.  
This is where your daily digests will appear as Issues.

---

## Step 2 — Copy this project into the repo

Push the contents of this folder into the repo root:

```bash
cd /path/to/vc-digest
git init
git remote add origin git@github.com:yourname/vc-digest-private.git
git add .
git commit -m "Initial setup"
git push -u origin main
```

---

## Step 3 — Add secrets to the repo

Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (from console.anthropic.com) |

> `GITHUB_TOKEN` is provided automatically by GitHub Actions — no setup needed.

---

## Step 4 — Enable Issues on the repo

Go to **Settings → General → Features** and make sure **Issues** is checked.

---

## Step 5 — Test it manually

Go to **Actions → Daily VC Digest → Run workflow**.  
After ~2 minutes, check **Issues** — your first digest should appear.

---

## Daily schedule

| Day | Time (SGT) | Cron (UTC) |
|-----|-----------|------------|
| Mon–Fri (non-holiday) | 8:30 AM | `30 0 * * 1-5` |
| Sat–Sun + public holidays | 11:00 AM | `0 3 * * 0,6` |

Singapore public holidays for 2025–2026 are pre-loaded in `src/digest.py`.

---

## On-demand reading lists

1. Go to **Issues → New issue**
2. Title it: `Query: vertical SaaS in SEA` (or any topic)
3. Add the label **`vc-query`**
4. Submit — the bot posts a reading list as a comment within ~60 seconds and closes the issue

> The labels `daily-digest` and `vc-query` are created automatically on first run.

---

## Customise news sources

Edit `config/sources.yml` to add or remove RSS feeds. Each feed entry:

```yaml
- name: "Display Name"
  url: "https://example.com/feed.rss"
  paywalled: true   # adds 🔒 flag to articles from this source
```

---

## Cost estimate

| Item | Cost |
|------|------|
| GitHub Actions | Free (2,000 min/month on free tier) |
| Claude API (~30 API calls/day) | ~$0.05–0.10/day |
| GitHub private repo | Free |

**Total: ~$1.50–3/month.**

---

## Notifications

GitHub will email you when a new Issue is created (the daily digest) — check your **Settings → Notifications** to confirm Issues are enabled for this repo. You can also pin the repo or watch it on the GitHub mobile app.
