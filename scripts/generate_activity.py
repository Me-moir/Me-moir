#!/usr/bin/env python3
"""
Fetches the latest public GitHub events for Me-moir and regenerates activity.svg.
Runs inside GitHub Actions — GITHUB_TOKEN is injected automatically.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────────────────
USERNAME = "Me-moir"
MAX_EVENTS = 7
OUTPUT_PATH = "activity.svg"          # repo root
TOKEN = os.getenv("GITHUB_TOKEN", "") # injected by Actions
# ─────────────────────────────────────────────────────────────────────────────


def fetch_events():
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=30"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        "User-Agent": "activity-svg-bot",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def relative_time(iso: str) -> str:
    ts = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    diff = int((datetime.now(timezone.utc) - ts).total_seconds())
    if diff < 60:
        return "just now"
    if diff < 3600:
        return f"{diff // 60}m ago"
    if diff < 86400:
        return f"{diff // 3600}h ago"
    return f"{diff // 86400}d ago"


def describe_event(ev: dict) -> tuple[str, str]:
    """Returns (icon_char, description_text)."""
    t = ev["type"]
    repo = ev["repo"]["name"]
    short = repo.split("/")[-1]

    if t == "PushEvent":
        commits = ev["payload"].get("commits", [])
        msg = commits[0]["message"].split("\n")[0][:55] if commits else "pushed"
        return "⬆", f"Pushed to {short}: {msg}"

    if t == "PullRequestEvent":
        action = ev["payload"].get("action", "")
        title = ev["payload"]["pull_request"]["title"][:50]
        return "⤵", f"PR {action}: {title}"

    if t == "IssuesEvent":
        action = ev["payload"].get("action", "")
        title = ev["payload"]["issue"]["title"][:50]
        return "●", f"Issue {action}: {title}"

    if t == "WatchEvent":
        return "★", f"Starred {short}"

    if t == "ForkEvent":
        return "⑂", f"Forked {short}"

    if t == "CreateEvent":
        ref_type = ev["payload"].get("ref_type", "")
        ref = ev["payload"].get("ref", "")
        return "✦", f"Created {ref_type} {ref} in {short}".strip()

    if t == "DeleteEvent":
        ref_type = ev["payload"].get("ref_type", "")
        return "✖", f"Deleted {ref_type} in {short}"

    if t == "IssueCommentEvent":
        return "💬", f"Commented on issue in {short}"

    if t == "ReleaseEvent":
        tag = ev["payload"]["release"]["tag_name"]
        return "⬡", f"Released {tag} in {short}"

    return "◆", f"{t.replace('Event','')} on {short}"


# ── SVG builder ───────────────────────────────────────────────────────────────
BG       = "#040c0e"
ACCENT   = "#00d9c8"
DIM      = "#3a7a78"
BORDER   = "#0d2b29"
WHITE    = "#e0f4f3"
ROW_H    = 44
HEADER_H = 52
FOOTER_H = 20
PAD      = 24
WIDTH    = 900


def escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def build_svg(rows: list[tuple]) -> str:
    n = len(rows)
    height = HEADER_H + n * ROW_H + FOOTER_H + PAD

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">',
        "<defs>",
        f'  <style>',
        f'    .title {{ font: 600 13px "Segoe UI",system-ui,sans-serif; fill:{ACCENT}; letter-spacing:.08em; text-transform:uppercase; }}',
        f'    .icon  {{ font: 500 15px "Segoe UI",monospace,sans-serif; fill:{ACCENT}; }}',
        f'    .desc  {{ font: 400 13px "Segoe UI",system-ui,sans-serif; fill:{WHITE}; }}',
        f'    .time  {{ font: 400 12px "Segoe UI",system-ui,sans-serif; fill:{DIM}; }}',
        f'    .sep   {{ stroke:{BORDER}; stroke-width:1; }}',
        f'  </style>',
        f'  <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">',
        f'    <stop offset="0%"   stop-color="{ACCENT}" stop-opacity=".15"/>',
        f'    <stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/>',
        f'  </linearGradient>',
        "</defs>",

        # background
        f'<rect width="{WIDTH}" height="{height}" rx="12" fill="{BG}"/>',
        f'<rect width="{WIDTH}" height="{height}" rx="12" fill="none" stroke="{BORDER}" stroke-width="1"/>',

        # header bar
        f'<rect x="0" y="0" width="{WIDTH}" height="{HEADER_H}" rx="12" fill="url(#g)"/>',
        f'<rect x="0" y="{HEADER_H-1}" width="{WIDTH}" height="1" fill="{BORDER}"/>',

        # pulse dot
        f'<circle cx="{PAD+6}" cy="{HEADER_H//2}" r="5" fill="{ACCENT}" opacity=".9">',
        f'  <animate attributeName="opacity" values="0.9;0.3;0.9" dur="2s" repeatCount="indefinite"/>',
        f'</circle>',

        # title
        f'<text x="{PAD+20}" y="{HEADER_H//2+5}" class="title">Recent Activity</text>',

        # timestamp (right-aligned)
        f'<text x="{WIDTH-PAD}" y="{HEADER_H//2+5}" class="time" text-anchor="end">',
        f'  Updated {datetime.now(timezone.utc).strftime("%d %b %Y %H:%M")} UTC',
        f'</text>',
    ]

    for i, (icon, desc, ts) in enumerate(rows):
        y = HEADER_H + i * ROW_H
        mid = y + ROW_H // 2

        # subtle hover-row tint on even rows
        if i % 2 == 0:
            lines.append(f'<rect x="1" y="{y}" width="{WIDTH-2}" height="{ROW_H}" fill="{ACCENT}" fill-opacity=".03"/>')

        # row separator
        if i > 0:
            lines.append(f'<line x1="{PAD}" y1="{y}" x2="{WIDTH-PAD}" y2="{y}" class="sep"/>')

        # icon
        lines.append(f'<text x="{PAD+4}" y="{mid+5}" class="icon">{escape(icon)}</text>')

        # description (truncate long strings visually via SVG)
        lines.append(
            f'<text x="{PAD+30}" y="{mid+5}" class="desc">'
            f'<tspan>{escape(desc[:80])}</tspan>'
            f'</text>'
        )

        # relative time
        lines.append(f'<text x="{WIDTH-PAD}" y="{mid+5}" class="time" text-anchor="end">{escape(ts)}</text>')

    lines.append("</svg>")
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    try:
        events = fetch_events()
    except Exception as exc:
        print(f"⚠ Could not fetch events: {exc}")
        events = []

    rows = []
    for ev in events:
        if len(rows) >= MAX_EVENTS:
            break
        try:
            icon, desc = describe_event(ev)
            ts = relative_time(ev["created_at"])
            rows.append((icon, desc, ts))
        except Exception:
            continue

    if not rows:
        rows = [("◆", "No recent public activity found.", "—")]

    svg = build_svg(rows)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Written {OUTPUT_PATH} ({len(rows)} events)")


if __name__ == "__main__":
    main()