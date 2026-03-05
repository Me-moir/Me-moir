#!/usr/bin/env python3
"""
Tech Deployment Map — fetches accurate Natural Earth 110m GeoJSON at runtime.
Projection: Web Mercator. No hand-coded polygons.
"""

import json, os, math, urllib.request
from datetime import datetime, timezone

USERNAME    = "Me-moir"
OUTPUT_PATH = "terrain.svg"
TOKEN       = os.getenv("GITHUB_TOKEN", "")

# Palette
BG       = "#060d2e"
BORDER2  = "#142570"
TEAL     = "#1a6eee"
ACCENT2  = "#0d40aa"
TEXT_DIM = "#6a8abf"
TEXT     = "#c8dcff"
AMBER    = "#ffab00"
LAND     = "#172660"
LAND_S   = "#2a3d80"
GRID_C   = "#0c1845"

W, H   = 860, 360

# Map draw area
MAP_X = 42
MAP_Y = 46
MAP_W = W - 84
MAP_H = H - 70

# Web Mercator bounds — show full world -180..180, -60..75
LAT_N =  75.0
LAT_S = -60.0
LON_W = -180.0
LON_E =  180.0

def merc_y(lat):
    """Web Mercator Y for a latitude."""
    r = math.radians(max(-85.0, min(85.0, lat)))
    return math.log(math.tan(math.pi / 4 + r / 2))

# Precompute top/bottom mercator values for scaling
MERC_TOP = merc_y(LAT_N)
MERC_BOT = merc_y(LAT_S)

def project(lat, lon):
    """Project lat/lon → SVG x,y."""
    x = MAP_X + (lon - LON_W) / (LON_E - LON_W) * MAP_W
    my = merc_y(lat)
    y = MAP_Y + (MERC_TOP - my) / (MERC_TOP - MERC_BOT) * MAP_H
    return x, y


# ── Hub definitions ───────────────────────────────────────────
# (name, lat, lon, tier, label_anchor, label_dx, label_dy)
HUBS = [
    ("San Francisco", 37.77, -122.41, 1, "middle",  0, -8),
    ("New York",      40.71,  -74.00, 1, "start",   6, -6),
    ("Toronto",       43.65,  -79.38, 2, "end",    -6, 11),
    ("Sao Paulo",    -23.55,  -46.63, 2, "middle",  0, 11),
    ("London",        51.50,   -0.12, 1, "end",    -6, -7),
    ("Amsterdam",     52.37,    4.90, 2, "start",   6, -7),
    ("Stockholm",     59.33,   18.06, 2, "middle",  0, -8),
    ("Berlin",        52.52,   13.40, 1, "end",    -6, 11),
    ("Tel Aviv",      32.08,   34.78, 1, "end",    -6, -7),
    ("Dubai",         25.20,   55.27, 1, "start",   6, -7),
    ("Bangalore",     12.97,   77.59, 2, "end",    -6, 11),
    ("Singapore",      1.35,  103.82, 1, "middle",  0, 11),
    ("Seoul",         37.56,  126.97, 2, "start",   6, -7),
    ("Tokyo",         35.68,  139.69, 2, "start",   6, 11),
    ("Sydney",       -33.86,  151.20, 2, "middle",  0, 11),
    ("Manila",        14.60,  121.00, 1, "start",   8, -8),  # home
]


def fetch_land_paths() -> list:
    """
    Fetch Natural Earth 110m land GeoJSON and convert every ring
    to an SVG path string using proper Web Mercator projection.
    """
    url = ("https://raw.githubusercontent.com/nvkelso/"
           "natural-earth-vector/master/geojson/ne_110m_land.geojson")
    req = urllib.request.Request(url, headers={"User-Agent": "map-svg-bot"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        gj = json.loads(resp.read())

    paths = []
    for feature in gj["features"]:
        geom = feature["geometry"]
        polys = (
            [geom["coordinates"]]
            if geom["type"] == "Polygon"
            else geom["coordinates"]
        )
        for poly in polys:
            for ring in poly:
                if len(ring) < 3:
                    continue
                pts = []
                for coord in ring:
                    lon, lat = coord[0], coord[1]
                    x, y = project(lat, lon)
                    pts.append(f"{x:.2f},{y:.2f}")
                paths.append("M" + " L".join(pts) + " Z")

    print(f"  → {len(paths)} land polygons")
    return paths


def fetch_total() -> int:
    q = ("query($l:String!){user(login:$l){contributionsCollection"
         "{contributionCalendar{totalContributions}}}}")
    payload = json.dumps({"query": q, "variables": {"l": USERNAME}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {TOKEN}",
                 "User-Agent": "map-svg-bot"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    if "errors" in data or not data.get("data"):
        raise RuntimeError(data)
    return (data["data"]["user"]["contributionsCollection"]
            ["contributionCalendar"]["totalContributions"])


def build_svg(land_paths: list, total: int) -> str:
    L = []
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">')

    # ── defs ──────────────────────────────────────────────────
    L.append('<defs>')
    L.append(f'''  <style>
    .title {{ font-family:"Courier New",Courier,monospace; font-weight:600;
              font-size:11px; fill:{TEAL}; letter-spacing:3px; text-transform:uppercase; }}
    .sub   {{ font-family:"Courier New",Courier,monospace; font-size:8px;
              fill:{TEXT_DIM}; letter-spacing:2px; }}
    .hub1  {{ font-family:"Courier New",Courier,monospace; font-size:7px;
              fill:{AMBER}; letter-spacing:0.5px; font-weight:700; }}
    .hub2  {{ font-family:"Courier New",Courier,monospace; font-size:6.5px;
              fill:{TEXT}; letter-spacing:0.5px; }}
    .home  {{ font-family:"Courier New",Courier,monospace; font-size:7.5px;
              fill:{AMBER}; letter-spacing:1px; font-weight:700; }}
  </style>
  <filter id="g1" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="g2" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="2.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="g3" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="1.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="ocean" cx="40%" cy="40%" r="65%">
    <stop offset="0%"   stop-color="#081848"/>
    <stop offset="100%" stop-color="{BG}"/>
  </radialGradient>
  <radialGradient id="ga" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{AMBER}" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="{AMBER}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="gb" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{TEAL}" stop-opacity="0.8"/>
    <stop offset="100%" stop-color="{TEAL}" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="mc">
    <rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}"/>
  </clipPath>''')
    L.append('</defs>')

    # ── background ────────────────────────────────────────────
    L.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    L.append(f'<rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" '
             f'fill="url(#ocean)" rx="1"/>')

    # ── grid lines ────────────────────────────────────────────
    for lat in range(-60, 76, 30):
        x1, y1 = project(lat, LON_W)
        x2, y2 = project(lat, LON_E)
        L.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" '
                 f'x2="{x2:.0f}" y2="{y2:.0f}" '
                 f'stroke="{GRID_C}" stroke-width="0.5" clip-path="url(#mc)"/>')
    for lon in range(-180, 181, 30):
        x1, y1 = project(LAT_S, lon)
        x2, y2 = project(LAT_N, lon)
        L.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" '
                 f'x2="{x2:.0f}" y2="{y2:.0f}" '
                 f'stroke="{GRID_C}" stroke-width="0.5" clip-path="url(#mc)"/>')

    # equator
    ex1, ey = project(0, LON_W)
    ex2, _  = project(0, LON_E)
    L.append(f'<line x1="{ex1:.0f}" y1="{ey:.0f}" x2="{ex2:.0f}" y2="{ey:.0f}" '
             f'stroke="#1a2e6e" stroke-width="0.8" stroke-dasharray="4,4" '
             f'clip-path="url(#mc)"/>')

    # ── landmasses (accurate GeoJSON paths) ───────────────────
    for d in land_paths:
        L.append(f'<path d="{d}" fill="{LAND}" stroke="{LAND_S}" '
                 f'stroke-width="0.5" clip-path="url(#mc)"/>')

    # map border
    L.append(f'<rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" '
             f'fill="none" stroke="{BORDER2}" stroke-width="1" rx="1"/>')

    # ── arcs from Manila to every other hub ───────────────────
    home_lat, home_lon = 14.60, 121.00
    hx0, hy0 = project(home_lat, home_lon)

    for name, lat, lon, tier, anc, dx, dy in HUBS:
        if name == "Manila":
            continue
        tx, ty = project(lat, lon)
        mx = (hx0 + tx) / 2
        dist = math.hypot(tx - hx0, ty - hy0)
        my = min(hy0, ty) - dist * 0.28
        color = AMBER if tier == 1 else TEAL
        op    = "0.38" if tier == 1 else "0.20"
        sw    = "1.1"  if tier == 1 else "0.7"
        L.append(f'<path d="M{hx0:.1f},{hy0:.1f} Q{mx:.1f},{my:.1f} {tx:.1f},{ty:.1f}" '
                 f'fill="none" stroke="{color}" stroke-width="{sw}" '
                 f'opacity="{op}" stroke-dasharray="3,5" clip-path="url(#mc)"/>')

    # ── hub dots + labels ─────────────────────────────────────
    for i, (name, lat, lon, tier, anc, ldx, ldy) in enumerate(HUBS):
        hx, hy   = project(lat, lon)
        is_home  = (name == "Manila")
        color    = AMBER if (tier == 1 or is_home) else TEAL
        grad     = "ga"  if (tier == 1 or is_home) else "gb"
        r_dot    = 5.0   if is_home else (3.5 if tier == 1 else 2.5)
        filt     = 'filter="url(#g1)"' if (tier == 1 or is_home) else 'filter="url(#g2)"'
        delay    = f"{i * 0.22:.2f}s"
        cls      = "home" if is_home else ("hub1" if tier == 1 else "hub2")
        r_pulse  = 18 if is_home else (13 if tier == 1 else 9)
        dur      = "1.6s" if is_home else "3s"

        # pulse ring
        L.append(
            f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{r_dot}" '
            f'fill="url(#{grad})" opacity="0">'
            f'<animate attributeName="r" '
            f'values="{r_dot};{r_pulse};{r_dot}" '
            f'dur="{dur}" begin="{delay}" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" '
            f'values="0.55;0;0.55" '
            f'dur="{dur}" begin="{delay}" repeatCount="indefinite"/>'
            f'</circle>'
        )
        # core dot
        L.append(
            f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{r_dot}" '
            f'fill="{color}" {filt}>'
            f'<animate attributeName="opacity" '
            f'values="1;0.5;1" dur="2.4s" begin="{delay}" '
            f'repeatCount="indefinite"/>'
            f'</circle>'
        )
        # label
        label = "@ME-MOIR" if is_home else name.upper()
        L.append(f'<text x="{hx+ldx:.1f}" y="{hy+ldy:.1f}" '
                 f'class="{cls}" text-anchor="{anc}">{label}</text>')

    # ── card chrome ───────────────────────────────────────────
    L.append(f'<rect width="{W}" height="{H}" fill="none" '
             f'stroke="{BORDER2}" stroke-width="1" rx="2"/>')
    for cx, cy, dx2, dy2 in [
            (0,0,1,1),(W,0,-1,1),(0,H,1,-1),(W,H,-1,-1)]:
        L.append(f'<line x1="{cx}" y1="{cy}" '
                 f'x2="{cx+dx2*14}" y2="{cy}" '
                 f'stroke="{TEAL}" stroke-width="1.5"/>')
        L.append(f'<line x1="{cx}" y1="{cy}" '
                 f'x2="{cx}" y2="{cy+dy2*14}" '
                 f'stroke="{TEAL}" stroke-width="1.5"/>')
    L.append(f'<line x1="60" y1="1" x2="{W-60}" y2="1" '
             f'stroke="rgba(100,160,255,0.3)" stroke-width="0.5"/>')

    # header bar
    L.append(f'<rect x="0" y="0" width="{W}" height="34" '
             f'fill="{TEAL}" fill-opacity="0.05"/>')
    L.append(f'<rect x="0" y="34" width="{W}" height="1" '
             f'fill="#0d2460"/>')

    # pulse dot
    L.append(f'<circle cx="20" cy="17" r="4" fill="{TEAL}">'
             f'<animate attributeName="opacity" values="1;0.2;1" '
             f'dur="2s" repeatCount="indefinite"/></circle>')
    L.append(f'<circle cx="20" cy="17" r="10" fill="{TEAL}" fill-opacity="0">'
             f'<animate attributeName="r" values="5;13;5" '
             f'dur="2s" repeatCount="indefinite"/>'
             f'<animate attributeName="fill-opacity" values="0.12;0;0.12" '
             f'dur="2s" repeatCount="indefinite"/></circle>')

    L.append(f'<text x="32" y="12" class="title">Tech Deployment Map</text>')
    L.append(f'<text x="32" y="26" class="sub">'
             f'@ME-MOIR · STACK INFLUENCE ZONES · '
             f'AMBER = PRIMARY · BLUE = SECONDARY</text>')
    L.append(f'<text x="{W-20}" y="12" class="sub" text-anchor="end">'
             f'NEXT.JS · REACT · TS · THREE.JS · PALANTIR</text>')
    L.append(f'<text x="{W-20}" y="26" class="sub" text-anchor="end">'
             f'AWS · GCP · VERCEL · POSTGRESQL · PRISMA</text>')

    # legend + sync
    LX, LY = MAP_X, H - 12
    L.append(f'<circle cx="{LX+5}" cy="{LY}" r="3" '
             f'fill="{AMBER}" filter="url(#g3)"/>')
    L.append(f'<text x="{LX+13}" y="{LY+4}" class="sub">PRIMARY HUB</text>')
    L.append(f'<circle cx="{LX+105}" cy="{LY}" r="2.5" '
             f'fill="{TEAL}" filter="url(#g3)"/>')
    L.append(f'<text x="{LX+113}" y="{LY+4}" class="sub">SECONDARY HUB</text>')
    L.append(f'<circle cx="{LX+222}" cy="{LY}" r="4" '
             f'fill="{AMBER}" filter="url(#g3)"/>')
    L.append(f'<text x="{LX+231}" y="{LY+4}" class="sub">'
             f'HOME BASE · MANILA PH</text>')
    ts = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    L.append(f'<text x="{W-20}" y="{LY+4}" class="sub" text-anchor="end">'
             f'SYNCED {ts}</text>')

    L.append('</svg>')
    return "\n".join(L)


def main():
    print("Fetching Natural Earth 110m land GeoJSON...")
    try:
        land_paths = fetch_land_paths()
    except Exception as exc:
        print(f"⚠  GeoJSON fetch failed: {exc}")
        land_paths = []

    total = 0
    try:
        total = fetch_total()
        print(f"✅ Contributions: {total}")
    except Exception as exc:
        print(f"⚠  Contributions fetch failed: {exc}")

    svg = build_svg(land_paths, total)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Written → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()