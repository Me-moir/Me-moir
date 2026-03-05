#!/usr/bin/env python3
"""
Fetches GitHub contribution data for Me-moir and generates a
futuristic commit grid SVG with contribution numbers on each cell.
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

# Palette
BG          = "#060d2e"
CELL_EMPTY  = "#0a1640"
CELL_LOW    = "#0d2a7a"
CELL_MID    = "#1a4acc"
CELL_HIGH   = "#1a6eee"
CELL_PEAK   = "#ffab00"
BORDER      = "#0d2460"
TEXT_DIM    = "#c0d8ff"   # bright enough to read
TEXT        = "#e0eeff"
ACCENT      = "#1a6eee"

# Grid — 26 weeks, large cells for numbers
COLS        = 26
ROWS        = 7
CELL        = 28
GAP         = 3
SVG_W       = 900
TOP_H       = 56
MONTH_H     = 22
BOTTOM_H    = 40
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
        data = json.loads(resp.read())

    # Surface API-level errors (e.g. bad token, missing scopes) so the
    # caller's except block catches them and falls back correctly.
    if "errors" in data:
        raise RuntimeError(f"GitHub API errors: {data['errors']}")
    if "data" not in data or data["data"] is None:
        raise RuntimeError(f"Unexpected GitHub API response: {data}")

    return data


def build_grid(data: dict):
    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = calendar["weeks"]
    # Use the API's own total — this covers the full contribution year,
    # not just the 26-week window we render.
    total = calendar["totalContributions"]

    all_weeks = weeks  # keep all weeks for streak calculation
    weeks = weeks[-COLS:]

    grid, dates = [], []
    for week in weeks:
        col_vals, col_dates = [], []
        for day in week["contributionDays"]:
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

    # compute current streak from all days
    all_days = []
    for week in all_weeks:
        for day in week["contributionDays"]:
            all_days.append(day["contributionCount"])
    streak = 0
    for cnt in reversed(all_days):
        if cnt > 0:
            streak += 1
        else:
            break

    return grid, dates, max_val, total, streak


def make_fallback_grid():
    import random
    random.seed(77)
    grid, dates = [], []
    for c in range(COLS):
        col, dcol = [], []
        for r in range(ROWS):
            base  = random.randint(0, 4)
            spike = random.randint(3, 12) if random.random() > 0.85 else 0
            col.append(base + spike)
            dcol.append("")
        grid.append(col)
        dates.append(dcol)
    total = sum(sum(c) for c in grid)
    return grid, dates, max(max(c) for c in grid) or 1, total, 0


def cell_color(val, max_val):
    if val == 0: return CELL_EMPTY
    t = val / max_val
    if t < 0.25: return CELL_LOW
    if t < 0.55: return CELL_MID
    if t < 0.80: return CELL_HIGH
    return CELL_PEAK


def num_color(val, max_val):
    if val == 0: return BORDER
    t = val / max_val
    if t >= 0.80: return "#1a1a00"
    if t < 0.25:  return TEXT_DIM
    return TEXT


def escape(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")


def build_svg(grid, dates, max_val, total, streak) -> str:
    grid_w   = COLS * (CELL + GAP) - GAP
    grid_h   = ROWS * (CELL + GAP) - GAP
    grid_x   = (SVG_W - grid_w) // 2
    grid_top = TOP_H + MONTH_H
    svg_h    = grid_top + grid_h + BOTTOM_H + 10

    L = []
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{svg_h}" viewBox="0 0 {SVG_W} {svg_h}">')

    # defs
    L.append("<defs>")
    L.append(f'  <style>')
    L.append(f'    .title {{ font: 600 11px "Courier New",monospace; fill:{ACCENT}; letter-spacing:3px; text-transform:uppercase; }}')
    L.append(f'    .sub   {{ font: 400 9px  "Courier New",monospace; fill:{TEXT_DIM}; letter-spacing:2px; }}')
    L.append(f'    .lbl   {{ font: 400 9px  "Courier New",monospace; fill:{TEXT_DIM}; }}')
    L.append(f'    .num   {{ font: 700 9px  "Courier New",monospace; text-anchor:middle; }}')
    L.append(f'    .stat  {{ font: 700 15px "Courier New",monospace; fill:{TEXT}; }}')
    L.append(f'    .stlbl {{ font: 400 8px  "Courier New",monospace; fill:{TEXT_DIM}; letter-spacing:2px; }}')
    L.append(f'  </style>')
    L.append(f'  <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/>'
             f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    L.append("</defs>")

    # background + border
    L.append(f'<rect width="{SVG_W}" height="{svg_h}" fill="{BG}" rx="2"/>')
    L.append(f'<rect width="{SVG_W}" height="{svg_h}" fill="none" stroke="{BORDER}" stroke-width="1" rx="2"/>')

    # corner brackets
    for cx, cy, dx, dy in [(0,0,1,1),(SVG_W,0,-1,1),(0,svg_h,1,-1),(SVG_W,svg_h,-1,-1)]:
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+dx*12}" y2="{cy}" stroke="{ACCENT}" stroke-width="1.5"/>')
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy+dy*12}" stroke="{ACCENT}" stroke-width="1.5"/>')

    # glass catchlight
    L.append(f'<line x1="80" y1="1" x2="{SVG_W-80}" y2="1" stroke="rgba(100,160,255,0.4)" stroke-width="0.5"/>')

    # header bg
    L.append(f'<rect x="0" y="0" width="{SVG_W}" height="{TOP_H}" fill="{ACCENT}" fill-opacity="0.06" rx="2"/>')
    L.append(f'<rect x="0" y="{TOP_H}" width="{SVG_W}" height="1" fill="{BORDER}"/>')

    # pulse dot
    mid = TOP_H // 2
    L.append(f'<circle cx="28" cy="{mid}" r="4" fill="{ACCENT}">'
             f'<animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/></circle>')
    L.append(f'<circle cx="28" cy="{mid}" r="9" fill="{ACCENT}" fill-opacity="0">'
             f'<animate attributeName="r" values="5;12;5" dur="2s" repeatCount="indefinite"/>'
             f'<animate attributeName="fill-opacity" values="0.1;0;0.1" dur="2s" repeatCount="indefinite"/></circle>')

    # left: title + subtitle
    L.append(f'<text x="44" y="{mid-6}" class="title">Commit Grid</text>')
    L.append(f'<text x="44" y="{mid+9}" class="sub">@{USERNAME.upper()} · LAST 26 WEEKS · NUMBERS = DAILY COMMITS</text>')

    # right: total contributions | current streak  (two stat blocks)
    # streak block
    L.append(f'<text x="{SVG_W-28}" y="{mid-6}" class="stat" text-anchor="end">{total} CONTRIBUTIONS</text>')
    L.append(f'<text x="{SVG_W-28}" y="{mid+9}" class="stlbl" text-anchor="end">{streak} DAY STREAK</text>')

    # vertical separator between title and stats
    L.append(f'<line x1="{SVG_W-220}" y1="10" x2="{SVG_W-220}" y2="{TOP_H-10}" stroke="{BORDER}" stroke-width="1"/>')

    # month labels
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    now = datetime.now(timezone.utc)
    prev_month = -1
    for c in range(COLS):
        weeks_back  = COLS - 1 - c
        approx_month = now.month - (weeks_back * 7 // 30)
        approx_year  = now.year
        while approx_month <= 0:
            approx_month += 12
            approx_year  -= 1
        month_idx = (approx_month - 1) % 12
        if month_idx != prev_month:
            mx = grid_x + c * (CELL + GAP)
            L.append(f'<text x="{mx}" y="{TOP_H + MONTH_H - 5}" class="lbl">{months[month_idx]} {approx_year}</text>')
            prev_month = month_idx

    # day labels
    for r, label in {0:"Mon", 2:"Wed", 4:"Fri", 6:"Sun"}.items():
        ly = grid_top + r * (CELL + GAP) + CELL // 2 + 3
        L.append(f'<text x="{grid_x - 8}" y="{ly}" class="lbl" text-anchor="end">{label}</text>')

    # cells
    for c in range(COLS):
        for r in range(ROWS):
            val    = grid[c][r]
            color  = cell_color(val, max_val)
            cx     = grid_x + c * (CELL + GAP)
            cy     = grid_top + r * (CELL + GAP)
            cx_mid = cx + CELL // 2
            cy_mid = cy + CELL // 2 + 4

            if val > 0 and val >= max_val * 0.75:
                L.append(f'<rect x="{cx-2}" y="{cy-2}" width="{CELL+4}" height="{CELL+4}" rx="3" '
                         f'fill="{color}" fill-opacity="0.35" filter="url(#glow)"/>')

            L.append(f'<rect x="{cx}" y="{cy}" width="{CELL}" height="{CELL}" rx="3" fill="{color}"/>')

            if val > 0:
                L.append(f'<rect x="{cx+2}" y="{cy+2}" width="{CELL-4}" height="4" rx="1" '
                         f'fill="white" fill-opacity="0.07"/>')

            nc      = num_color(val, max_val)
            display = str(val) if val <= 99 else "99+"
            L.append(f'<text x="{cx_mid}" y="{cy_mid}" class="num" fill="{nc}">{display}</text>')

    # legend
    legend_y = grid_top + grid_h + 14
    L.append(f'<text x="{grid_x}" y="{legend_y+10}" class="lbl">NONE</text>')
    lx = grid_x + 44
    for color, label in [(CELL_EMPTY,"0"),(CELL_LOW,"1-2"),(CELL_MID,"3-5"),(CELL_HIGH,"6-9"),(CELL_PEAK,"10+")]:
        L.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="3" fill="{color}"/>')
        L.append(f'<text x="{lx+CELL//2}" y="{legend_y+CELL//2+3}" class="num" '
                 f'fill="{num_color(1 if color!=CELL_EMPTY else 0,1)}" style="font-size:8px">{label}</text>')
        lx += CELL + GAP + 2
    L.append(f'<text x="{lx+4}" y="{legend_y+10}" class="lbl">COMMITS/DAY</text>')

    ts = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    L.append(f'<text x="{SVG_W-28}" y="{legend_y+10}" class="sub" text-anchor="end">SYNCED {escape(ts)}</text>')

    L.append("</svg>")
    return "\n".join(L)


def main():
    try:
        data = fetch_contributions()
        grid, dates, max_val, total, streak = build_grid(data)
        print(f"✅ Fetched — max {max_val}/day, {total} total, {streak} day streak")
    except Exception as exc:
        print(f"⚠ API failed ({exc}), using fallback")
        grid, dates, max_val, total, streak = make_fallback_grid()

    svg = build_svg(grid, dates, max_val, total, streak)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Written {OUTPUT_PATH}")


if __name__ == "__main__":
    main()