"""Email delivery via Resend API."""

import os
import requests


def send_email(subject: str, html: str) -> None:
    """Send an email via Resend."""
    api_key = os.environ["RESEND_API_KEY"]
    to_email = os.environ["TO_EMAIL"]

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": "VC Digest <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html,
        },
    )
    response.raise_for_status()
    print(f"  [email] Sent to {to_email} — id: {response.json().get('id')}")
