#!/usr/bin/env python3
"""
Fetches GitHub contribution data for Me-moir and generates an
isometric 3D terrain SVG where columns rise with commit activity.
Styled to match the existing profile palette.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
USERNAME    = "Me-moir"
OUTPUT_PATH = "terrain.svg"
TOKEN       = os.getenv("GITHUB_TOKEN", "")

# Palette — nebula blue
BG          = "#060d2e"
TEAL        = "#1a6eee"
TEAL2       = "#1a5acc"
TEAL3       = "#0d3a8e"
TEAL4       = "#0a2060"
TEAL_DIM    = "#0d2460"
BORDER      = "#0d2460"
TEXT_DIM    = "#6a8abf"
TEXT        = "#e0eeff"
AMBER       = "#ffab00"
# ─────────────────────────────────────────────────────────────────────────────

COLS = 52   # weeks
ROWS = 7    # days per week


def fetch_contributions() -> dict:
    """Use GitHub GraphQL API to get contribution calendar."""
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": USERNAME}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "terrain-svg-bot",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def build_grid(data: dict):
    """Returns (grid[col][row], max_val, total) — last 52 weeks."""
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    total = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

    # Take last 52 weeks
    weeks = weeks[-COLS:]

    grid = []
    for week in weeks:
        col = []
        days = week["contributionDays"]
        for day in days:
            col.append(day["contributionCount"])
        # Pad to 7 if needed
        while len(col) < ROWS:
            col.append(0)
        grid.append(col)

    # Pad columns if fewer than 52
    while len(grid) < COLS:
        grid.insert(0, [0] * ROWS)

    max_val = max(max(col) for col in grid) or 1
    return grid, max_val, total


def make_fallback_grid():
    """Simulated data if API fails."""
    import random
    random.seed(42)
    grid = []
    for c in range(COLS):
        col = []
        for r in range(ROWS):
            # simulate realistic commit pattern
            base = random.randint(0, 4)
            spike = random.randint(0, 8) if random.random() > 0.85 else 0
            col.append(base + spike)
        grid.append(col)
    max_val = max(max(col) for col in grid) or 1
    return grid, max_val, 0


# ── ISO projection ────────────────────────────────────────────────────────────
# Cell size
CW = 14   # cell width in iso space
CH = 7    # cell height in iso space
MAX_BAR_H = 60  # max column height in px

SVG_W = 900
SVG_H = 380

# Iso origin (top-center-ish)
ORIG_X = SVG_W / 2 - (COLS * CW) / 2 + 40
ORIG_Y = 120


def iso(col, row):
    """Convert grid col/row to isometric screen x,y (top face)."""
    x = ORIG_X + (col - row) * CW
    y = ORIG_Y + (col + row) * CH
    return x, y


def lerp_color(t):
    """0=deep navy → 1=bright blue, with amber spike at top."""
    if t < 0.0:
        t = 0.0
    if t > 1.0:
        t = 1.0
    if t < 0.5:
        # deep navy → mid blue
        r1, g1, b1 = 0x0a, 0x20, 0x60   # #0a2060
        r2, g2, b2 = 0x0d, 0x3a, 0x8e   # #0d3a8e
        f = t * 2
    elif t < 0.85:
        # mid blue → bright blue
        r1, g1, b1 = 0x0d, 0x3a, 0x8e   # #0d3a8e
        r2, g2, b2 = 0x1a, 0x6e, 0xee   # #1a6eee
        f = (t - 0.5) / 0.35
    else:
        # bright blue → amber peak
        r1, g1, b1 = 0x1a, 0x6e, 0xee   # #1a6eee
        r2, g2, b2 = 0xff, 0xab, 0x00   # #ffab00
        f = (t - 0.85) / 0.15

    r = int(r1 + (r2 - r1) * f)
    g = int(g1 + (g2 - g1) * f)
    b = int(b1 + (b2 - b1) * f)
    return f"#{r:02x}{g:02x}{b:02x}"


def darken(hex_color, factor=0.6):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"


def build_svg(grid, max_val, total) -> str:
    lines = []

    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">')

    # ── defs ──
    lines.append("<defs>")
    lines.append(f'  <style>')
    lines.append(f'    .label {{ font: 400 10px "Courier New", monospace; fill: {TEXT}; letter-spacing: 1px; }}')
    lines.append(f'    .title {{ font: 600 11px "Courier New", monospace; fill: {TEAL}; letter-spacing: 3px; text-transform: uppercase; }}')
    lines.append(f'    .sub   {{ font: 400 9px  "Courier New", monospace; fill: {TEXT_DIM}; letter-spacing: 2px; }}')
    lines.append(f'  </style>')
    # Glow filter
    lines.append(f'  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">')
    lines.append(f'    <feGaussianBlur stdDeviation="2" result="blur"/>')
    lines.append(f'    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>')
    lines.append(f'  </filter>')
    # Subtle glow for tall bars
    lines.append(f'  <filter id="glow2" x="-40%" y="-40%" width="180%" height="180%">')
    lines.append(f'    <feGaussianBlur stdDeviation="4" result="blur"/>')
    lines.append(f'    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>')
    lines.append(f'  </filter>')
    lines.append("</defs>")

    # ── background ──
    lines.append(f'<rect width="{SVG_W}" height="{SVG_H}" fill="{BG}"/>')

    # corner brackets
    bw = 12
    lines.append(f'<rect x="0" y="0" width="{SVG_W}" height="{SVG_H}" fill="none" stroke="{BORDER}" stroke-width="1" rx="2"/>')
    for cx, cy, dx, dy in [(0,0,1,1),(SVG_W,0,-1,1),(0,SVG_H,1,-1),(SVG_W,SVG_H,-1,-1)]:
        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+dx*bw}" y2="{cy}" stroke="{TEAL}" stroke-width="1.5"/>')
        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy+dy*bw}" stroke="{TEAL}" stroke-width="1.5"/>')

    # header gradient strip
    lines.append(f'<rect x="0" y="0" width="{SVG_W}" height="40" fill="none"/>')

    # pulse dot
    lines.append(f'<circle cx="24" cy="20" r="4" fill="{TEAL}" opacity=".9">')
    lines.append(f'  <animate attributeName="opacity" values="0.9;0.3;0.9" dur="2s" repeatCount="indefinite"/>')
    lines.append(f'</circle>')

    # title
    lines.append(f'<text x="36" y="25" class="title">Commit Terrain</text>')
    lines.append(f'<text x="{SVG_W-24}" y="17" class="sub" text-anchor="end">52 WEEKS</text>')
    lines.append(f'<text x="{SVG_W-24}" y="30" class="sub" text-anchor="end">{total} TOTAL CONTRIBUTIONS</text>')

    # top-edge glass line
    lines.append(f'<line x1="80" y1="1" x2="{SVG_W-80}" y2="1" stroke="rgba(0,217,200,0.4)" stroke-width="0.5"/>')

    # ── ground plane dots ──
    for c in range(0, COLS, 4):
        for r in range(0, ROWS, 2):
            gx, gy = iso(c, r)
            lines.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="0.8" fill="{TEXT_DIM}" opacity="0.4"/>')

    # ── bars — draw back-to-front for correct overlap ──
    # Sort: draw high col+row first (back), low col+row last (front)
    cells = []
    for c in range(COLS):
        for r in range(ROWS):
            cells.append((c, r))
    cells.sort(key=lambda x: x[0] + x[1])

    for c, r in cells:
        val = grid[c][r]
        t = val / max_val
        h = max(2, int(t * MAX_BAR_H))  # min height 2px so grid is visible

        top_color   = lerp_color(t)
        left_color  = darken(top_color, 0.55)
        right_color = darken(top_color, 0.40)

        # use glow filter for tall bars
        filt = ' filter="url(#glow2)"' if t > 0.8 else ''

        # iso corners of the top face
        tx, ty = iso(c, r)

        # Top face diamond
        p_top    = (tx,        ty - h)
        p_right  = (tx + CW,   ty + CH - h)
        p_bottom = (tx,        ty + CH*2 - h)
        p_left   = (tx - CW,   ty + CH - h)

        # Left face
        p_bl = (tx - CW, ty + CH)
        p_br = (tx,      ty + CH*2)

        # Right face
        p_rr = (tx + CW, ty + CH)

        def pt(p): return f"{p[0]:.1f},{p[1]:.1f}"

        # Left face
        left_pts = f"{pt(p_left)} {pt(p_bottom)} {pt(p_br)} {pt(p_bl)}"
        lines.append(f'<polygon points="{left_pts}" fill="{left_color}" stroke="{BG}" stroke-width="0.3"{filt}/>')

        # Right face
        right_pts = f"{pt(p_bottom)} {pt(p_right)} {pt(p_rr)} {pt(p_br)}"
        lines.append(f'<polygon points="{right_pts}" fill="{right_color}" stroke="{BG}" stroke-width="0.3"{filt}/>')

        # Top face
        top_pts = f"{pt(p_top)} {pt(p_right)} {pt(p_bottom)} {pt(p_left)}"
        lines.append(f'<polygon points="{top_pts}" fill="{top_color}" stroke="{BG}" stroke-width="0.3"{filt}/>')

        # Tiny glow cap on tall bars
        if t > 0.7:
            cx2 = (p_top[0] + p_bottom[0]) / 2
            cy2 = (p_top[1] + p_bottom[1]) / 2
            lines.append(f'<circle cx="{cx2:.1f}" cy="{cy2:.1f}" r="2" fill="{AMBER if t>0.9 else TEAL}" opacity="0.6" filter="url(#glow)"/>')

    # ── day labels (Mon, Wed, Fri) ──
    day_labels = {0: "MON", 2: "WED", 4: "FRI", 6: "SUN"}
    for r, label in day_labels.items():
        lx, ly = iso(0, r)
        lines.append(f'<text x="{lx-28:.1f}" y="{ly+4:.1f}" class="label" text-anchor="end">{label}</text>')

    # ── month labels ──
    months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
    now = datetime.now(timezone.utc)
    for i, interval in enumerate(range(0, COLS, 4)):
        mx, my = iso(interval, 0)
        month_idx = (now.month - 1 - (COLS // 4 - i) + 12) % 12
        lines.append(f'<text x="{mx:.1f}" y="{my-8:.1f}" class="sub" text-anchor="middle">{months[month_idx]}</text>')

    # ── footer ──
    ts = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    lines.append(f'<text x="{SVG_W//2}" y="{SVG_H-10}" class="sub" text-anchor="middle">SYNCED {ts} · AUTO-UPDATES EVERY 30 MIN</text>')

    lines.append("</svg>")
    return "\n".join(lines)


def main():
    try:
        data  = fetch_contributions()
        grid, max_val, total = build_grid(data)
        print(f"✅ Fetched contribution data — max {max_val}/day, {total} total")
    except Exception as exc:
        print(f"⚠ API fetch failed ({exc}), using simulated data")
        grid, max_val, total = make_fallback_grid()

    svg = build_svg(grid, max_val, total)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Written {OUTPUT_PATH}")


if __name__ == "__main__":
    main()