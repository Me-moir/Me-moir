#!/usr/bin/env python3
"""
Fetches GitHub contribution data for Me-moir and generates a
futuristic commit grid SVG — like the GitHub heatmap but better.
Runs inside GitHub Actions — GITHUB_TOKEN is injected automatically.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────────────────
USERNAME    = "Me-moir"
OUTPUT_PATH = "commitgrid.svg"
TOKEN       = os.getenv("GITHUB_TOKEN", "")

# Palette — nebula blue
BG          = "#060d2e"
BLUE_0      = "#0a1640"   # no commits
BLUE_1      = "#0d2a7a"   # low
BLUE_2      = "#1a4acc"   # mid
BLUE_3      = "#1a6eee"   # high
BLUE_4      = "#4a9fff"   # very high
AMBER       = "#ffab00"   # peak / streak
BORDER      = "#0d2460"
TEXT_DIM    = "#6a8abf"
TEXT        = "#e0eeff"
TEAL        = "#1a6eee"

# Grid config
COLS        = 52
ROWS        = 7
CELL        = 13    # cell size px
GAP         = 2     # gap between cells
SVG_W       = 900
LABEL_W     = 32    # left label space
TOP_H       = 56    # header height
MONTH_H     = 20    # month label row
BOTTOM_H    = 36    # footer
# ─────────────────────────────────────────────────────────────────────────────


def fetch_contributions() -> dict:
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
                weekday
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
            "User-Agent": "commitgrid-svg-bot",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def build_grid(data: dict):
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    total = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    weeks = weeks[-COLS:]

    grid = []
    dates = []
    for week in weeks:
        col_vals = []
        col_dates = []
        days = week["contributionDays"]
        for day in days:
            col_vals.append(day["contributionCount"])
            col_dates.append(day["date"])
        while len(col_vals) < ROWS:
            col_vals.append(0)
            col_dates.append("")
        grid.append(col_vals)
        dates.append(col_dates)

    while len(grid) < COLS:
        grid.insert(0, [0] * ROWS)
        dates.insert(0, [""] * ROWS)

    max_val = max(max(col) for col in grid) or 1
    return grid, dates, max_val, total


def make_fallback_grid():
    import random
    random.seed(99)
    grid, dates = [], []
    for c in range(COLS):
        col, dcol = [], []
        for r in range(ROWS):
            base  = random.randint(0, 3)
            spike = random.randint(0, 10) if random.random() > 0.88 else 0
            col.append(base + spike)
            dcol.append("")
        grid.append(col)
        dates.append(dcol)
    return grid, dates, max(max(c) for c in grid) or 1, 0


def cell_color(val, max_val):
    if val == 0:
        return BLUE_0
    t = val / max_val
    if t < 0.25:  return BLUE_1
    if t < 0.50:  return BLUE_2
    if t < 0.75:  return BLUE_3
    if t < 0.90:  return BLUE_4
    return AMBER


def glow_opacity(val, max_val):
    if max_val == 0: return 0
    t = val / max_val
    return round(min(t * 0.8, 0.7), 2)


def escape(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")


def build_svg(grid, dates, max_val, total) -> str:
    grid_w   = COLS * (CELL + GAP) - GAP
    grid_h   = ROWS * (CELL + GAP) - GAP
    left_pad = LABEL_W + 10
    svg_h    = TOP_H + MONTH_H + grid_h + BOTTOM_H + 20

    # Center the grid horizontally
    grid_x   = (SVG_W - grid_w) // 2

    L = []
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{svg_h}" viewBox="0 0 {SVG_W} {svg_h}">')

    # ── defs ──
    L.append("<defs>")
    L.append(f'  <style>')
    L.append(f'    .title {{ font: 600 11px "Courier New",monospace; fill:{TEAL}; letter-spacing:3px; text-transform:uppercase; }}')
    L.append(f'    .sub   {{ font: 400 9px  "Courier New",monospace; fill:{TEXT_DIM}; letter-spacing:2px; }}')
    L.append(f'    .label {{ font: 400 9px  "Courier New",monospace; fill:{TEXT_DIM}; letter-spacing:1px; }}')
    L.append(f'    .total {{ font: 700 13px "Courier New",monospace; fill:{TEXT}; letter-spacing:1px; }}')
    L.append(f'  </style>')
    # glow filter for active cells
    L.append(f'  <filter id="cg" x="-40%" y="-40%" width="180%" height="180%">')
    L.append(f'    <feGaussianBlur stdDeviation="2.5" result="b"/>')
    L.append(f'    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>')
    L.append(f'  </filter>')
    L.append(f'  <filter id="hg" x="-20%" y="-20%" width="140%" height="140%">')
    L.append(f'    <feGaussianBlur stdDeviation="6" result="b"/>')
    L.append(f'    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>')
    L.append(f'  </filter>')
    # scan line pattern
    L.append(f'  <pattern id="scan" x="0" y="0" width="1" height="3" patternUnits="userSpaceOnUse">')
    L.append(f'    <rect x="0" y="0" width="1" height="1" fill="{TEAL}" fill-opacity="0.03"/>')
    L.append(f'  </pattern>')
    L.append("</defs>")

    # ── background ──
    L.append(f'<rect width="{SVG_W}" height="{svg_h}" fill="{BG}" rx="2"/>')
    # scanline overlay
    L.append(f'<rect width="{SVG_W}" height="{svg_h}" fill="url(#scan)" rx="2"/>')
    L.append(f'<rect width="{SVG_W}" height="{svg_h}" fill="none" stroke="{BORDER}" stroke-width="1" rx="2"/>')

    # corner brackets
    bw = 12
    for cx, cy, dx, dy in [(0,0,1,1),(SVG_W,0,-1,1),(0,svg_h,1,-1),(SVG_W,svg_h,-1,-1)]:
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+dx*bw}" y2="{cy}" stroke="{TEAL}" stroke-width="1.5"/>')
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy+dy*bw}" stroke="{TEAL}" stroke-width="1.5"/>')

    # glass catchlight
    L.append(f'<line x1="80" y1="1" x2="{SVG_W-80}" y2="1" stroke="rgba(100,160,255,0.4)" stroke-width="0.5"/>')

    # ── header ──
    # header gradient strip
    L.append(f'<rect x="0" y="0" width="{SVG_W}" height="{TOP_H}" fill="{TEAL}" fill-opacity="0.06" rx="2"/>')
    L.append(f'<rect x="0" y="{TOP_H}" width="{SVG_W}" height="1" fill="{BORDER}"/>')

    # pulse dot
    L.append(f'<circle cx="28" cy="{TOP_H//2}" r="4" fill="{TEAL}">'
             f'<animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/></circle>')
    L.append(f'<circle cx="28" cy="{TOP_H//2}" r="9" fill="{TEAL}" fill-opacity="0">'
             f'<animate attributeName="r" values="5;12;5" dur="2s" repeatCount="indefinite"/>'
             f'<animate attributeName="fill-opacity" values="0.1;0;0.1" dur="2s" repeatCount="indefinite"/></circle>')

    L.append(f'<text x="44" y="{TOP_H//2-5}" class="title">Commit Grid</text>')
    L.append(f'<text x="44" y="{TOP_H//2+10}" class="sub">@{USERNAME.upper()} · 52 WEEKS</text>')
    L.append(f'<text x="{SVG_W-28}" y="{TOP_H//2-5}" class="total" text-anchor="end">{total}</text>')
    L.append(f'<text x="{SVG_W-28}" y="{TOP_H//2+10}" class="sub" text-anchor="end">TOTAL CONTRIBUTIONS</text>')

    # ── month labels ──
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    now = datetime.now(timezone.utc)
    month_y = TOP_H + MONTH_H - 4
    prev_month = -1
    for c in range(COLS):
        month_idx = (now.month - 1 - (COLS - 1 - c) // 4 + 120) % 12
        if month_idx != prev_month:
            mx = grid_x + c * (CELL + GAP)
            L.append(f'<text x="{mx}" y="{month_y}" class="label">{months[month_idx]}</text>')
            prev_month = month_idx

    # ── day labels ──
    day_labels = {0: "Mon", 2: "Wed", 4: "Fri", 6: "Sun"}
    grid_top = TOP_H + MONTH_H
    for r, label in day_labels.items():
        ly = grid_top + r * (CELL + GAP) + CELL - 2
        L.append(f'<text x="{grid_x - 6}" y="{ly}" class="label" text-anchor="end">{label}</text>')

    # ── cells ──
    for c in range(COLS):
        for r in range(ROWS):
            val   = grid[c][r]
            color = cell_color(val, max_val)
            gop   = glow_opacity(val, max_val)
            cx    = grid_x + c * (CELL + GAP)
            cy    = grid_top + r * (CELL + GAP)

            use_glow = val > 0 and gop > 0.2

            # cell background (empty slot)
            L.append(f'<rect x="{cx}" y="{cy}" width="{CELL}" height="{CELL}" rx="2" fill="{BLUE_0}" fill-opacity="0.6"/>')

            if val > 0:
                # glow halo behind cell
                if use_glow:
                    L.append(f'<rect x="{cx-1}" y="{cy-1}" width="{CELL+2}" height="{CELL+2}" rx="3" '
                             f'fill="{color}" fill-opacity="{gop}" filter="url(#hg)"/>')

                # main cell
                filt = ' filter="url(#cg)"' if val >= max_val * 0.8 else ''
                L.append(f'<rect x="{cx}" y="{cy}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"{filt}/>')

                # inner shine on active cells
                L.append(f'<rect x="{cx+1}" y="{cy+1}" width="{CELL-2}" height="3" rx="1" '
                         f'fill="white" fill-opacity="0.08"/>')

                # amber peak marker
                if val >= max_val * 0.9:
                    L.append(f'<rect x="{cx+2}" y="{cy+2}" width="{CELL-4}" height="{CELL-4}" rx="1" '
                             f'fill="{AMBER}" fill-opacity="0.25"/>')
            else:
                # empty cell with subtle inner border
                L.append(f'<rect x="{cx+0.5}" y="{cy+0.5}" width="{CELL-1}" height="{CELL-1}" rx="2" '
                         f'fill="none" stroke="{BORDER}" stroke-width="0.5"/>')

    # ── legend ──
    legend_y = grid_top + grid_h + 16
    legend_x = grid_x
    L.append(f'<text x="{legend_x}" y="{legend_y+10}" class="label">LESS</text>')
    lx = legend_x + 38
    for color in [BLUE_0, BLUE_1, BLUE_2, BLUE_3, BLUE_4, AMBER]:
        L.append(f'<rect x="{lx}" y="{legend_y}" width="12" height="12" rx="2" fill="{color}"/>')
        lx += 16
    L.append(f'<text x="{lx+2}" y="{legend_y+10}" class="label">MORE</text>')

    # timestamp
    ts = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    L.append(f'<text x="{SVG_W-28}" y="{legend_y+10}" class="sub" text-anchor="end">SYNCED {escape(ts)}</text>')

    L.append("</svg>")
    return "\n".join(L)


def main():
    try:
        data = fetch_contributions()
        grid, dates, max_val, total = build_grid(data)
        print(f"✅ Fetched data — max {max_val}/day, {total} total")
    except Exception as exc:
        print(f"⚠ API failed ({exc}), using fallback")
        grid, dates, max_val, total = make_fallback_grid()

    svg = build_svg(grid, dates, max_val, total)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Written {OUTPUT_PATH}")


if __name__ == "__main__":
    main()