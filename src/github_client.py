"""Thin GitHub REST API client for posting issues and comments."""

import os
from typing import Optional

import requests


class GitHubClient:
    def __init__(self):
        self.token = os.environ["GITHUB_TOKEN"]
        self.repo = os.environ["GITHUB_REPO"]  # e.g. "yourname/vc-digest-private"
        self._base = f"https://api.github.com/repos/{self.repo}"
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _post(self, path: str, payload: dict) -> dict:
        r = requests.post(f"{self._base}{path}", json=payload, headers=self._headers)
        r.raise_for_status()
        return r.json()

    def _patch(self, path: str, payload: dict) -> dict:
        r = requests.patch(f"{self._base}{path}", json=payload, headers=self._headers)
        r.raise_for_status()
        return r.json()

    def _get(self, path: str) -> list:
        r = requests.get(f"{self._base}{path}", headers=self._headers)
        r.raise_for_status()
        return r.json()

    def ensure_labels(self):
        """Create required labels if they don't already exist."""
        wanted = [
            {"name": "daily-digest", "color": "0075ca", "description": "Daily VC news digest"},
            {"name": "vc-query", "color": "e4e669", "description": "On-demand reading list request"},
        ]
        existing = {lbl["name"] for lbl in self._get("/labels")}
        for label in wanted:
            if label["name"] not in existing:
                requests.post(f"{self._base}/labels", json=label, headers=self._headers)

    def create_issue(self, title: str, body: str, labels: Optional[list] = None) -> dict:
        payload: dict = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        return self._post("/issues", payload)

    def create_comment(self, issue_number: int, body: str) -> dict:
        return self._post(f"/issues/{issue_number}/comments", {"body": body})

    def close_issue(self, issue_number: int) -> dict:
        return self._patch(f"/issues/{issue_number}", {"state": "closed"})
