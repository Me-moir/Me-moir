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
USERNAME    = "Me-moir"
MAX_EVENTS  = 8
OUTPUT_PATH = "activity.svg"
TOKEN       = os.getenv("GITHUB_TOKEN", "")

# Palette — nebula blue with light text
BG          = "#060d2e"
TEAL        = "#1a6eee"
TEAL_MID    = "#1a5acc"
TEAL_DIM    = "#0d2460"
BORDER      = "#0d2460"
TEXT        = "#6a8abf"
TEXT_BRIGHT = "#e0eeff"
AMBER       = "#ffab00"

WIDTH       = 900
ROW_H       = 46
HEADER_H    = 56
FOOTER_H    = 32
PAD         = 28
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
    if diff < 60:   return "just now"
    if diff < 3600: return f"{diff // 60}m ago"
    if diff < 86400:return f"{diff // 3600}h ago"
    return f"{diff // 86400}d ago"


# Event type → (tag_label, tag_color, icon, description_fn)
def describe_event(ev: dict):
    t     = ev["type"]
    repo  = ev["repo"]["name"]
    short = repo.split("/")[-1]

    if t == "PushEvent":
        commits = ev["payload"].get("commits", [])
        msg = commits[0]["message"].split("\n")[0][:60] if commits else "pushed"
        n   = len(commits)
        return "PUSH", TEAL, "↑", short, f"{msg}", f"+{n} commit{'s' if n!=1 else ''}"

    if t == "PullRequestEvent":
        action = ev["payload"].get("action", "")
        title  = ev["payload"]["pull_request"]["title"][:55]
        return "PR", TEAL_MID, "⤵", short, title, action.upper()

    if t == "IssuesEvent":
        action = ev["payload"].get("action", "")
        title  = ev["payload"]["issue"]["title"][:55]
        return "ISSUE", TEAL_DIM, "●", short, title, action.upper()

    if t == "WatchEvent":
        return "STAR", AMBER, "★", short, f"Starred {short}", ""

    if t == "ForkEvent":
        return "FORK", TEAL_MID, "⑂", short, f"Forked {short}", ""

    if t == "CreateEvent":
        ref_type = ev["payload"].get("ref_type", "")
        ref      = ev["payload"].get("ref", "")
        label    = f"{ref_type} {ref}".strip()
        return "CREATE", TEAL, "✦", short, f"Created {label}", ""

    if t == "DeleteEvent":
        ref_type = ev["payload"].get("ref_type", "")
        return "DELETE", TEAL_DIM, "✖", short, f"Deleted {ref_type} in {short}", ""

    if t == "IssueCommentEvent":
        return "COMMENT", TEAL_MID, "◈", short, f"Commented on issue in {short}", ""

    if t == "ReleaseEvent":
        tag = ev["payload"]["release"]["tag_name"]
        return "RELEASE", AMBER, "⬡", short, f"Released {tag}", ""

    return "EVENT", TEAL_DIM, "◆", short, f"{t.replace('Event','')} on {short}", ""


def escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def build_svg(rows: list) -> str:
    n      = len(rows)
    height = HEADER_H + n * ROW_H + FOOTER_H

    L = []

    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">')

    # ── defs ──
    L.append("<defs>")
    L.append(f"""  <style>
    .mono  {{ font-family: "Courier New", "Consolas", monospace; }}
    .title {{ font: 600 11px "Courier New",monospace; fill:{TEAL}; letter-spacing:3px; text-transform:uppercase; }}
    .sub   {{ font: 400 9px  "Courier New",monospace; fill:{TEAL_DIM}; letter-spacing:2px; }}
    .repo  {{ font: 400 9px  "Courier New",monospace; fill:{TEXT}; letter-spacing:1px; }}
    .msg   {{ font: 400 12px "Courier New",monospace; fill:{TEXT_BRIGHT}; }}
    .meta  {{ font: 400 10px "Courier New",monospace; fill:{TEXT}; }}
    .ts    {{ font: 400 10px "Courier New",monospace; fill:{TEAL_DIM}; }}
    .tag   {{ font: 600 8px  "Courier New",monospace; letter-spacing:1px; }}
  </style>""")
    # header gradient
    L.append(f'  <linearGradient id="hg" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="{TEAL}" stop-opacity=".12"/>'
             f'<stop offset="100%" stop-color="{TEAL}" stop-opacity="0"/></linearGradient>')
    # row hover gradient
    L.append(f'  <linearGradient id="rg" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="{TEAL}" stop-opacity=".06"/>'
             f'<stop offset="60%" stop-color="{TEAL}" stop-opacity=".02"/>'
             f'<stop offset="100%" stop-color="{TEAL}" stop-opacity="0"/></linearGradient>')
    # glow filter
    L.append(f'  <filter id="glow"><feGaussianBlur stdDeviation="2" result="b"/>'
             f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    L.append("</defs>")

    # ── background ──
    L.append(f'<rect width="{WIDTH}" height="{height}" fill="{BG}" rx="2"/>')
    L.append(f'<rect width="{WIDTH}" height="{height}" fill="none" stroke="{BORDER}" stroke-width="1" rx="2"/>')

    # corner brackets
    bw = 12
    for cx, cy, dx, dy in [(0,0,1,1),(WIDTH,0,-1,1),(0,height,1,-1),(WIDTH,height,-1,-1)]:
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+dx*bw}" y2="{cy}" stroke="{TEAL}" stroke-width="1.5"/>')
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy+dy*bw}" stroke="{TEAL}" stroke-width="1.5"/>')

    # top glass catchlight
    L.append(f'<line x1="80" y1="1" x2="{WIDTH-80}" y2="1" stroke="rgba(0,217,200,0.35)" stroke-width="0.5"/>')

    # ── header ──
    L.append(f'<rect x="0" y="0" width="{WIDTH}" height="{HEADER_H}" fill="url(#hg)" rx="2"/>')
    L.append(f'<rect x="0" y="{HEADER_H}" width="{WIDTH}" height="1" fill="{BORDER}"/>')

    # pulse dot
    L.append(f'<circle cx="{PAD}" cy="{HEADER_H//2}" r="4" fill="{TEAL}" filter="url(#glow)">')
    L.append(f'  <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/>')
    L.append(f'</circle>')
    L.append(f'<circle cx="{PAD}" cy="{HEADER_H//2}" r="8" fill="{TEAL}" fill-opacity="0.08">')
    L.append(f'  <animate attributeName="r" values="6;12;6" dur="2s" repeatCount="indefinite"/>')
    L.append(f'  <animate attributeName="fill-opacity" values="0.1;0;0.1" dur="2s" repeatCount="indefinite"/>')
    L.append(f'</circle>')

    L.append(f'<text x="{PAD+18}" y="{HEADER_H//2-4}" class="title">Recent Activity</text>')
    L.append(f'<text x="{PAD+18}" y="{HEADER_H//2+10}" class="sub">@{USERNAME.upper()}</text>')

    ts_now = datetime.now(timezone.utc).strftime("%d %b %Y  %H:%M UTC")
    L.append(f'<text x="{WIDTH-PAD}" y="{HEADER_H//2-4}" class="sub" text-anchor="end">SYNCED {ts_now}</text>')
    L.append(f'<text x="{WIDTH-PAD}" y="{HEADER_H//2+10}" class="sub" text-anchor="end">AUTO-UPDATES EVERY 30 MIN</text>')

    # ── rows ──
    for i, (tag, tag_color, icon, repo, msg, meta) in enumerate(rows):
        y   = HEADER_H + i * ROW_H
        mid = y + ROW_H // 2

        # alternating row bg
        if i % 2 == 0:
            L.append(f'<rect x="1" y="{y+1}" width="{WIDTH-2}" height="{ROW_H-1}" fill="url(#rg)"/>')

        # separator
        if i > 0:
            L.append(f'<line x1="{PAD}" y1="{y}" x2="{WIDTH-PAD}" y2="{y}" stroke="{BORDER}" stroke-width="1"/>')

        # left accent bar
        L.append(f'<rect x="0" y="{y+4}" width="2" height="{ROW_H-8}" fill="{tag_color}" opacity="0.6" rx="1"/>')

        # tag pill
        tag_w = len(tag) * 6 + 12
        L.append(f'<rect x="{PAD}" y="{mid-9}" width="{tag_w}" height="14" rx="2" fill="{tag_color}" fill-opacity="0.12" stroke="{tag_color}" stroke-opacity="0.3" stroke-width="0.5"/>')
        L.append(f'<text x="{PAD + tag_w//2}" y="{mid+3}" class="tag" fill="{tag_color}" text-anchor="middle">{escape(tag)}</text>')

        # repo name
        repo_x = PAD + tag_w + 10
        L.append(f'<text x="{repo_x}" y="{mid-1}" class="repo">{escape(repo)}</text>')

        # commit message
        msg_x = PAD + tag_w + 10
        L.append(f'<text x="{msg_x}" y="{mid+12}" class="msg">{escape(msg[:65])}</text>')

        # meta (commits count, action etc)
        if meta:
            L.append(f'<text x="{WIDTH - PAD - 80}" y="{mid-1}" class="meta" text-anchor="end">{escape(meta)}</text>')

        # timestamp
        ts = rows[i][0]  # placeholder — set below per row
        # (timestamp is passed separately — see main)

    L.append("</svg>")
    return "\n".join(L)


def main():
    try:
        events = fetch_events()
        print(f"✅ Fetched {len(events)} events")
    except Exception as exc:
        print(f"⚠ Could not fetch events: {exc}")
        events = []

    rows     = []
    ts_list  = []

    for ev in events:
        if len(rows) >= MAX_EVENTS:
            break
        try:
            tag, tag_color, icon, repo, msg, meta = describe_event(ev)
            ts = relative_time(ev["created_at"])
            rows.append((tag, tag_color, icon, repo, msg, meta))
            ts_list.append(ts)
        except Exception:
            continue

    if not rows:
        rows    = [("EVENT", TEAL_DIM, "◆", USERNAME, "No recent public activity found.", "")]
        ts_list = ["—"]

    # Build SVG with timestamps injected properly
    n      = len(rows)
    height = HEADER_H + n * ROW_H + FOOTER_H

    # We rebuild the rows section properly with timestamps
    svg = build_svg_full(rows, ts_list, height)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Written {OUTPUT_PATH} ({len(rows)} events)")


def build_svg_full(rows: list, ts_list: list, height: int) -> str:
    n = len(rows)
    L = []

    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">')
    L.append("<defs>")
    L.append(f"""  <style>
    .title {{ font: 600 11px "Courier New",monospace; fill:{TEAL}; letter-spacing:3px; text-transform:uppercase; }}
    .sub   {{ font: 400 9px  "Courier New",monospace; fill:{TEAL_DIM}; letter-spacing:2px; }}
    .repo  {{ font: 400 9px  "Courier New",monospace; fill:{TEXT}; letter-spacing:1px; text-transform:uppercase; }}
    .msg   {{ font: 400 12px "Courier New",monospace; fill:{TEXT_BRIGHT}; }}
    .meta  {{ font: 400 10px "Courier New",monospace; fill:{TEXT}; }}
    .ts    {{ font: 400 10px "Courier New",monospace; fill:{TEAL_DIM}; }}
    .tag   {{ font: 700 8px  "Courier New",monospace; letter-spacing:1px; }}
  </style>""")
    L.append(f'  <linearGradient id="hg" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="{TEAL}" stop-opacity=".12"/>'
             f'<stop offset="100%" stop-color="{TEAL}" stop-opacity="0"/></linearGradient>')
    L.append(f'  <linearGradient id="rg" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="{TEAL}" stop-opacity=".05"/>'
             f'<stop offset="100%" stop-color="{TEAL}" stop-opacity="0"/></linearGradient>')
    L.append(f'  <filter id="glow"><feGaussianBlur stdDeviation="2.5" result="b"/>'
             f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    L.append("</defs>")

    # bg + border
    L.append(f'<rect width="{WIDTH}" height="{height}" fill="{BG}" rx="2"/>')
    L.append(f'<rect width="{WIDTH}" height="{height}" fill="none" stroke="{BORDER}" stroke-width="1" rx="2"/>')

    # corner brackets
    bw = 12
    for cx, cy, dx, dy in [(0,0,1,1),(WIDTH,0,-1,1),(0,height,1,-1),(WIDTH,height,-1,-1)]:
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+dx*bw}" y2="{cy}" stroke="{TEAL}" stroke-width="1.5"/>')
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy+dy*bw}" stroke="{TEAL}" stroke-width="1.5"/>')

    # glass catchlight
    L.append(f'<line x1="80" y1="1" x2="{WIDTH-80}" y2="1" stroke="rgba(0,217,200,0.35)" stroke-width="0.5"/>')

    # header
    L.append(f'<rect x="0" y="0" width="{WIDTH}" height="{HEADER_H}" fill="url(#hg)" rx="2"/>')
    L.append(f'<rect x="0" y="{HEADER_H}" width="{WIDTH}" height="1" fill="{BORDER}"/>')

    # animated pulse
    L.append(f'<circle cx="{PAD}" cy="{HEADER_H//2}" r="4" fill="{TEAL}" filter="url(#glow)">'
             f'<animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/></circle>')
    L.append(f'<circle cx="{PAD}" cy="{HEADER_H//2}" r="8" fill="{TEAL}" fill-opacity="0.0">'
             f'<animate attributeName="r" values="5;11;5" dur="2s" repeatCount="indefinite"/>'
             f'<animate attributeName="fill-opacity" values="0.1;0;0.1" dur="2s" repeatCount="indefinite"/></circle>')

    L.append(f'<text x="{PAD+18}" y="{HEADER_H//2-4}" class="title">Recent Activity</text>')
    L.append(f'<text x="{PAD+18}" y="{HEADER_H//2+10}" class="sub">@{USERNAME.upper()}</text>')

    ts_now = datetime.now(timezone.utc).strftime("%d %b %Y  %H:%M UTC")
    L.append(f'<text x="{WIDTH-PAD}" y="{HEADER_H//2-4}" class="sub" text-anchor="end">SYNCED {escape(ts_now)}</text>')
    L.append(f'<text x="{WIDTH-PAD}" y="{HEADER_H//2+10}" class="sub" text-anchor="end">AUTO-UPDATES EVERY 30 MIN</text>')

    # rows
    for i, (tag, tag_color, icon, repo, msg, meta) in enumerate(rows):
        y   = HEADER_H + i * ROW_H
        mid = y + ROW_H // 2
        ts  = ts_list[i] if i < len(ts_list) else ""

        if i % 2 == 0:
            L.append(f'<rect x="1" y="{y+1}" width="{WIDTH-2}" height="{ROW_H-1}" fill="url(#rg)"/>')
        if i > 0:
            L.append(f'<line x1="{PAD}" y1="{y}" x2="{WIDTH-PAD}" y2="{y}" stroke="{BORDER}" stroke-width="1"/>')

        # left accent bar
        L.append(f'<rect x="0" y="{y+6}" width="2" height="{ROW_H-12}" fill="{tag_color}" opacity="0.7" rx="1"/>')

        # tag pill
        tag_w = len(tag) * 6 + 14
        L.append(f'<rect x="{PAD}" y="{mid-9}" width="{tag_w}" height="15" rx="2" '
                 f'fill="{tag_color}" fill-opacity="0.1" stroke="{tag_color}" stroke-opacity="0.4" stroke-width="0.5"/>')
        L.append(f'<text x="{PAD + tag_w//2}" y="{mid+3}" class="tag" fill="{tag_color}" text-anchor="middle">{escape(tag)}</text>')

        content_x = PAD + tag_w + 12

        # repo + message on two lines
        L.append(f'<text x="{content_x}" y="{mid-1}" class="repo">{escape(repo)}</text>')
        L.append(f'<text x="{content_x}" y="{mid+13}" class="msg">{escape(msg[:62])}</text>')

        # meta label
        if meta:
            L.append(f'<text x="{WIDTH-PAD-90}" y="{mid-1}" class="meta">{escape(meta)}</text>')

        # timestamp — right aligned
        L.append(f'<text x="{WIDTH-PAD}" y="{mid+13}" class="ts" text-anchor="end">{escape(ts)}</text>')

    # footer bar
    footer_y = HEADER_H + n * ROW_H
    L.append(f'<rect x="0" y="{footer_y}" width="{WIDTH}" height="{FOOTER_H}" fill="{BORDER}" fill-opacity="0.3" rx="2"/>')
    L.append(f'<rect x="0" y="{footer_y}" width="{WIDTH}" height="1" fill="{BORDER}"/>')
    L.append(f'<text x="{WIDTH//2}" y="{footer_y + FOOTER_H//2 + 4}" class="sub" text-anchor="middle">'
             f'github.com/{USERNAME}</text>')

    L.append("</svg>")
    return "\n".join(L)


if __name__ == "__main__":
    main()