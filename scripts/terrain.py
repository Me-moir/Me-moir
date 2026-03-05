#!/usr/bin/env python3
"""
Tech Deployment Map — world map with stack influence zones.
Uses Natural Earth 110m GeoJSON for accurate continent outlines.
GitHub Actions safe: stdlib only.
"""

import json, os, math, urllib.request
from datetime import datetime, timezone

USERNAME    = "Me-moir"
OUTPUT_PATH = "terrain.svg"
TOKEN       = os.getenv("GITHUB_TOKEN", "")

# Palette
BG       = "#060d2e"
BORDER   = "#0d2460"
BORDER2  = "#142570"
TEAL     = "#1a6eee"
TEAL_DIM = "#0d2460"
TEXT_DIM = "#6a8abf"
TEXT     = "#c8dcff"
AMBER    = "#ffab00"
LAND     = "#0a1640"
LAND2    = "#0d1e55"
GRID_C   = "#0a1535"

W, H   = 860, 380
MAP_X  = 40
MAP_Y  = 55
MAP_W  = W - 80
MAP_H  = H - 90

HUBS = [
    ("San Francisco", 37.77, -122.41, 1),
    ("New York",      40.71,  -74.00, 1),
    ("London",        51.50,   -0.12, 1),
    ("Berlin",        52.52,   13.40, 1),
    ("Singapore",      1.35,  103.82, 1),
    ("Dubai",         25.20,   55.27, 1),
    ("Tel Aviv",      32.08,   34.78, 1),
    ("Tokyo",         35.68,  139.69, 2),
    ("Sydney",       -33.86,  151.20, 2),
    ("Toronto",       43.65,  -79.38, 2),
    ("Amsterdam",     52.37,    4.90, 2),
    ("Sao Paulo",    -23.55,  -46.63, 2),
    ("Seoul",         37.56,  126.97, 2),
    ("Bangalore",     12.97,   77.59, 2),
    ("Stockholm",     59.33,   18.06, 2),
]

# ── Mercator projection ───────────────────────────────────────
def mercator(lat, lon):
    x = MAP_X + (lon + 180) / 360 * MAP_W
    r = math.radians(max(-85, min(85, lat)))
    m = math.log(math.tan(math.pi / 4 + r / 2))
    y = MAP_Y + MAP_H / 2 - (m / math.pi) * MAP_H
    return x, y

# ── Fetch accurate GeoJSON landmass data ──────────────────────
GEOJSON_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector"
    "/master/geojson/ne_110m_land.geojson"
)

def fetch_geojson() -> dict:
    req = urllib.request.Request(
        GEOJSON_URL,
        headers={"User-Agent": "map-svg-bot"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

def geojson_to_svg_paths(geojson: dict) -> list[str]:
    """Convert GeoJSON features → list of SVG <path d="..."> strings."""
    paths = []
    for feature in geojson["features"]:
        geom = feature["geometry"]
        polys = []
        if geom["type"] == "Polygon":
            polys = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            polys = geom["coordinates"]

        for poly in polys:
            for ring in poly:
                if len(ring) < 3:
                    continue
                pts = []
                for lon, lat in ring:
                    x, y = mercator(lat, lon)
                    pts.append(f"{x:.1f},{y:.1f}")
                paths.append("M" + " L".join(pts) + " Z")
    return paths


# ── Fallback: coarse but continent-accurate simplified coords ─
# Sourced from Natural Earth 110m, manually decimated to ~40pts each
FALLBACK_PATHS = [
    # North America
    "M158.2,50.9 L164.7,51.4 L168.2,54.1 L171.6,57.0 L173.3,60.6 L171.4,63.3 L167.5,65.8 L163.2,67.4 L158.0,69.2 L151.7,70.8 L143.5,70.3 L136.8,69.3 L131.8,67.4 L128.6,64.5 L124.8,60.1 L122.3,56.5 L120.9,53.7 L117.0,49.0 L111.5,48.7 L104.0,48.9 L97.5,48.9 L91.8,48.0 L88.0,46.8 L84.8,45.9 L83.0,43.6 L79.8,43.4 L76.0,43.7 L72.5,45.0 L70.1,46.8 L67.8,47.1 L66.0,44.8 L64.6,43.4 L66.8,41.8 L70.8,41.4 L73.8,40.6 L75.5,38.8 L77.0,34.8 L81.0,30.4 L85.5,29.8 L88.6,29.9 L90.3,29.2 L93.9,29.5 L97.5,25.8 L104.5,19.4 L110.4,23.5 L116.8,31.8 L120.5,34.4 L122.4,37.8 L124.2,40.6 L124.2,46.2 L127.8,50.4 L131.8,54.2 L135.6,57.8 L140.1,59.6 L143.9,60.1 L148.5,60.8 L152.8,58.4 L156.2,56.0 L158.2,50.9 Z",
    # Greenland
    "M286.2,82.5 L296.8,83.1 L307.4,82.6 L317.2,80.2 L322.8,76.8 L324.0,73.4 L319.6,70.2 L313.2,67.8 L306.0,65.8 L298.0,63.4 L290.2,62.6 L284.0,64.2 L280.2,67.8 L279.0,72.0 L280.8,76.4 L283.6,80.2 L286.2,82.5 Z",
    # South America
    "M203.8,11.6 L207.2,9.8 L210.8,7.4 L215.6,3.4 L219.8,0.0 L222.6,-3.8 L223.4,-8.2 L222.0,-12.4 L218.6,-17.0 L214.8,-22.4 L211.8,-27.6 L210.2,-33.0 L210.8,-38.4 L212.6,-42.6 L215.4,-46.2 L218.0,-49.8 L220.2,-53.4 L218.8,-55.6 L214.0,-53.2 L209.4,-50.0 L205.6,-46.4 L202.8,-42.0 L201.2,-37.8 L200.4,-32.4 L199.6,-27.2 L198.2,-22.0 L196.8,-16.8 L196.0,-11.4 L196.8,-6.0 L197.6,-1.2 L196.4,3.8 L193.8,7.8 L192.0,10.4 L194.8,12.4 L198.4,12.8 L203.8,11.6 Z",
    # Europe (mainland)
    "M381.0,36.2 L387.4,37.6 L392.8,37.0 L398.4,36.6 L404.8,38.4 L408.4,40.8 L411.6,41.8 L415.2,40.6 L419.2,38.2 L422.4,37.8 L425.6,38.4 L428.2,40.2 L429.8,43.4 L432.6,45.0 L436.4,44.8 L438.6,42.6 L440.4,40.2 L443.6,40.4 L446.2,42.0 L447.8,44.8 L448.6,48.0 L447.6,51.2 L445.8,53.8 L443.4,55.6 L441.8,58.2 L441.0,60.8 L440.4,63.4 L438.2,65.0 L434.8,65.4 L431.6,64.2 L428.4,62.8 L425.2,63.4 L422.4,65.0 L419.8,66.2 L417.2,65.6 L415.4,63.8 L413.4,61.6 L410.8,60.4 L407.8,61.2 L405.2,63.0 L403.0,60.8 L401.4,58.2 L400.2,55.4 L399.6,52.4 L399.8,49.0 L400.8,46.0 L400.0,43.4 L397.8,41.4 L394.8,40.4 L391.6,40.2 L388.6,39.4 L385.4,37.6 L381.0,36.2 Z",
    # Scandinavia
    "M433.6,57.4 L435.8,56.0 L438.4,56.2 L440.6,57.4 L443.0,59.4 L445.0,62.0 L447.4,64.4 L449.6,66.8 L451.4,69.4 L452.8,72.2 L452.4,74.8 L450.0,76.2 L447.2,75.6 L444.6,73.8 L442.0,71.4 L439.8,68.8 L438.0,66.0 L436.4,63.2 L435.0,60.4 L433.6,57.4 Z",
    # Africa
    "M390.4,36.8 L395.2,37.4 L400.0,37.0 L406.4,37.2 L412.4,36.4 L418.0,36.0 L422.4,37.2 L426.0,38.8 L429.2,41.4 L432.4,44.4 L433.8,47.6 L434.2,51.0 L433.0,53.8 L430.6,55.4 L429.2,57.6 L430.0,60.4 L430.8,63.4 L430.0,66.8 L428.4,69.8 L425.8,72.0 L423.2,73.6 L421.0,76.4 L420.2,79.8 L418.8,83.2 L416.6,86.2 L413.6,88.6 L410.2,90.4 L406.4,91.8 L402.4,92.6 L398.4,92.0 L394.8,90.2 L391.8,87.6 L389.8,84.4 L388.6,80.8 L387.4,77.0 L387.0,73.2 L387.4,69.4 L387.8,65.4 L387.0,61.4 L386.2,57.6 L386.0,53.6 L386.2,49.6 L386.8,45.8 L387.6,42.4 L388.8,39.4 L390.4,36.8 Z",
    # Asia (mainland)
    "M440.4,40.2 L445.8,39.4 L451.4,38.8 L457.2,38.4 L463.2,37.8 L469.4,37.4 L475.6,37.6 L481.4,38.4 L487.0,39.8 L492.4,41.6 L497.2,43.6 L501.8,44.8 L506.2,44.4 L510.2,43.0 L514.4,42.4 L518.6,43.0 L522.6,44.4 L526.4,46.2 L529.8,48.2 L533.0,50.4 L536.4,51.6 L540.2,51.4 L543.8,50.4 L547.2,50.0 L550.6,50.6 L554.0,52.0 L557.2,53.8 L559.8,56.0 L561.4,58.6 L561.8,61.6 L561.0,64.6 L559.4,67.4 L556.8,69.6 L553.4,71.0 L549.6,71.8 L545.4,72.0 L541.4,71.4 L537.4,70.2 L533.4,69.0 L529.4,68.2 L525.2,68.0 L521.0,68.4 L516.8,69.2 L512.6,70.0 L508.4,70.6 L504.0,70.4 L499.6,69.6 L495.4,68.4 L491.4,67.0 L487.6,65.4 L484.0,63.6 L480.6,61.6 L477.4,59.4 L474.4,57.2 L471.4,55.2 L468.2,53.6 L464.6,52.6 L460.8,52.4 L457.0,52.8 L453.2,53.6 L449.6,54.6 L446.6,56.0 L444.2,57.8 L442.4,60.0 L441.4,62.6 L441.0,65.4 L440.8,68.2 L440.4,71.0 L439.4,73.8 L437.6,76.0 L435.2,77.6 L432.4,78.2 L429.6,78.0 L427.2,77.0 L425.6,75.2 L424.8,73.0 L424.8,70.6 L425.4,68.2 L426.2,65.8 L426.8,63.4 L426.8,60.8 L426.0,58.4 L424.6,56.2 L422.8,54.4 L420.8,53.0 L418.8,52.2 L416.8,52.4 L414.8,53.4 L413.0,55.2 L411.6,57.4 L410.8,60.0 L410.8,62.6 L411.6,65.2 L412.6,67.8 L413.2,70.4 L413.0,73.0 L412.0,75.4 L410.4,77.4 L408.4,79.0 L406.4,80.2 L404.6,81.2 L403.2,82.4 L402.4,84.0 L402.2,86.0 L402.2,88.0 L401.8,90.0 L400.8,92.0 L399.2,93.4 L397.2,94.2 L395.0,94.4 L392.8,94.0 L391.0,93.0 L389.8,91.6 L389.4,89.8 L389.8,88.0 L391.0,86.4 L440.4,40.2 Z",
    # India
    "M488.8,55.2 L492.2,54.4 L495.8,54.6 L499.0,55.8 L501.6,57.8 L503.4,60.4 L504.4,63.2 L504.6,66.2 L504.0,69.0 L502.6,71.6 L500.6,74.0 L498.2,76.0 L496.0,77.6 L494.2,79.2 L493.2,81.2 L492.8,83.4 L491.6,81.4 L490.0,79.4 L488.4,77.2 L487.0,74.8 L486.0,72.2 L485.4,69.4 L485.4,66.6 L485.8,63.8 L486.6,61.2 L487.4,58.6 L488.0,56.6 L488.8,55.2 Z",
    # SE Asia
    "M540.8,63.4 L544.2,62.8 L547.8,62.4 L551.4,62.6 L554.6,64.0 L557.2,66.2 L558.6,69.0 L558.8,72.0 L557.8,74.8 L555.8,77.0 L553.2,78.4 L550.4,78.8 L547.6,78.2 L545.2,76.8 L543.0,74.8 L541.6,72.4 L540.8,69.8 L540.4,67.0 L540.8,63.4 Z",
    # Japan
    "M564.6,52.6 L567.4,51.8 L570.2,52.2 L572.4,53.8 L573.6,56.2 L573.4,58.8 L572.0,61.0 L569.8,62.6 L567.4,63.2 L565.0,62.6 L563.0,61.0 L562.0,58.8 L562.0,56.2 L563.0,54.2 L564.6,52.6 Z",
    # Australia
    "M543.0,91.8 L547.8,90.8 L552.8,90.2 L557.8,90.0 L562.8,90.4 L567.4,91.4 L571.6,93.2 L574.8,95.8 L577.0,99.0 L578.2,102.6 L578.4,106.4 L577.6,110.0 L575.8,113.2 L573.2,115.8 L570.0,117.8 L566.4,119.2 L562.4,119.8 L558.4,119.6 L554.6,118.4 L551.0,116.4 L547.8,113.8 L545.0,110.8 L542.8,107.4 L541.2,103.8 L540.4,100.0 L540.4,96.2 L541.2,92.8 L543.0,91.8 Z",
    # New Zealand
    "M594.2,111.6 L596.2,110.4 L598.2,110.6 L599.8,112.0 L600.4,114.0 L599.6,116.0 L597.8,117.2 L595.8,117.0 L594.2,115.6 L593.6,113.6 L594.2,111.6 Z",
]


def fetch_geojson_paths() -> list[str]:
    """Fetch Natural Earth 110m land GeoJSON and convert to SVG path strings."""
    print("Fetching Natural Earth GeoJSON...")
    req = urllib.request.Request(
        "https://raw.githubusercontent.com/nvkelso/natural-earth-vector"
        "/master/geojson/ne_110m_land.geojson",
        headers={"User-Agent": "map-svg-bot"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        gj = json.loads(resp.read())

    paths = []
    for feature in gj["features"]:
        geom = feature["geometry"]
        polys = []
        if geom["type"] == "Polygon":
            polys = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            polys = geom["coordinates"]
        for poly in polys:
            for ring in poly:
                if len(ring) < 3:
                    continue
                pts = []
                for coord in ring:
                    lon, lat = coord[0], coord[1]
                    x, y = mercator(lat, lon)
                    pts.append(f"{x:.1f},{y:.1f}")
                paths.append("M" + " L".join(pts) + " Z")
    print(f"  → {len(paths)} landmass polygons loaded")
    return paths


def fetch_total() -> int:
    query = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions}}}}"""
    payload = json.dumps({"query": query, "variables": {"login": USERNAME}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {TOKEN}",
                 "User-Agent": "map-svg-bot"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    if "errors" in data or not data.get("data"):
        raise RuntimeError(data)
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]


def build_svg(land_paths: list[str], total: int) -> str:
    L = []
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    L.append('<defs>')
    L.append(f'''  <style>
    .title {{ font-family:"Courier New",Courier,monospace; font-weight:600; font-size:11px; fill:{TEAL}; letter-spacing:3px; text-transform:uppercase; }}
    .sub   {{ font-family:"Courier New",Courier,monospace; font-size:8px; fill:{TEXT_DIM}; letter-spacing:2px; }}
    .hub1  {{ font-family:"Courier New",Courier,monospace; font-size:7.5px; fill:{AMBER}; letter-spacing:0.5px; font-weight:700; }}
    .hub2  {{ font-family:"Courier New",Courier,monospace; font-size:7px; fill:{TEXT}; letter-spacing:0.5px; }}
  </style>
  <filter id="g1" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="g2" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="2.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="g3" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="1.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="ocean" cx="35%" cy="45%" r="65%">
    <stop offset="0%"   stop-color="#081440"/>
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
  <clipPath id="mapclip">
    <rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}"/>
  </clipPath>''')
    L.append('</defs>')

    # bg + ocean
    L.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    L.append(f'<rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" fill="url(#ocean)" rx="1"/>')

    # lat/lon grid
    for lat in range(-60, 91, 30):
        x1, y1 = mercator(lat, -180)
        x2, y2 = mercator(lat,  180)
        L.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{GRID_C}" stroke-width="0.5" clip-path="url(#mapclip)"/>')
    for lon in range(-180, 181, 30):
        x1, y1 = mercator(-75, lon)
        x2, y2 = mercator(82,  lon)
        L.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{GRID_C}" stroke-width="0.5" clip-path="url(#mapclip)"/>')
    # equator
    ex1, ey1 = mercator(0, -180)
    ex2, ey2 = mercator(0,  180)
    L.append(f'<line x1="{ex1:.0f}" y1="{ey1:.0f}" x2="{ex2:.0f}" y2="{ey2:.0f}" stroke="#0d2460" stroke-width="1" stroke-dasharray="4,4" opacity="0.8" clip-path="url(#mapclip)"/>')

    # landmasses — clipped to map rect
    for d in land_paths:
        L.append(f'<path d="{d}" fill="{LAND}" stroke="{LAND2}" stroke-width="0.5" clip-path="url(#mapclip)"/>')

    # map border
    L.append(f'<rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" fill="none" stroke="{BORDER2}" stroke-width="1" rx="1"/>')

    # arcs from Manila
    hx0, hy0 = mercator(14.60, 121.0)
    for name, lat, lon, tier in HUBS:
        tx, ty = mercator(lat, lon)
        mx = (hx0 + tx) / 2
        my = min(hy0, ty) - 32
        color = AMBER if tier == 1 else TEAL
        op    = "0.3"  if tier == 1 else "0.15"
        sw    = "1.0"  if tier == 1 else "0.7"
        L.append(f'<path d="M{hx0:.1f},{hy0:.1f} Q{mx:.1f},{my:.1f} {tx:.1f},{ty:.1f}" '
                 f'fill="none" stroke="{color}" stroke-width="{sw}" opacity="{op}" '
                 f'stroke-dasharray="3,5" clip-path="url(#mapclip)"/>')

    # hub markers
    for i, (name, lat, lon, tier) in enumerate(HUBS):
        hx2, hy2 = mercator(lat, lon)
        color  = AMBER if tier == 1 else TEAL
        grad   = "ga"  if tier == 1 else "gb"
        r_dot  = 3.5   if tier == 1 else 2.5
        filt   = 'filter="url(#g1)"' if tier == 1 else 'filter="url(#g2)"'
        delay  = f"{i * 0.25:.2f}s"
        cls    = "hub1" if tier == 1 else "hub2"
        r_p    = 14    if tier == 1 else 10

        L.append(f'<circle cx="{hx2:.1f}" cy="{hy2:.1f}" r="{r_dot}" fill="url(#{grad})" opacity="0">'
                 f'<animate attributeName="r" values="{r_dot};{r_p};{r_dot}" dur="3s" begin="{delay}" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0.5;0;0.5" dur="3s" begin="{delay}" repeatCount="indefinite"/>'
                 f'</circle>')
        L.append(f'<circle cx="{hx2:.1f}" cy="{hy2:.1f}" r="{r_dot}" fill="{color}" {filt}>'
                 f'<animate attributeName="opacity" values="1;0.6;1" dur="2.5s" begin="{delay}" repeatCount="indefinite"/>'
                 f'</circle>')
        dy = -6 if lat > 15 else 11
        L.append(f'<text x="{hx2:.1f}" y="{hy2+dy:.1f}" class="{cls}" text-anchor="middle">{name.upper()}</text>')

    # home — Manila
    L.append(f'<circle cx="{hx0:.1f}" cy="{hy0:.1f}" r="5" fill="{AMBER}" filter="url(#g1)">'
             f'<animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/>'
             f'</circle>')
    L.append(f'<circle cx="{hx0:.1f}" cy="{hy0:.1f}" r="5" fill="url(#ga)">'
             f'<animate attributeName="r" values="6;20;6" dur="1.5s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0.6;0;0.6" dur="1.5s" repeatCount="indefinite"/>'
             f'</circle>')
    L.append(f'<text x="{hx0:.1f}" y="{hy0-9:.1f}" class="hub1" text-anchor="middle">@ME-MOIR</text>')
    L.append(f'<text x="{hx0:.1f}" y="{hy0+14:.1f}" class="sub" text-anchor="middle">MANILA · PH</text>')

    # card chrome
    L.append(f'<rect width="{W}" height="{H}" fill="none" stroke="{BORDER2}" stroke-width="1" rx="2"/>')
    for cx, cy, dx, dy in [(0,0,1,1),(W,0,-1,1),(0,H,1,-1),(W,H,-1,-1)]:
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+dx*14}" y2="{cy}" stroke="{TEAL}" stroke-width="1.5"/>')
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy+dy*14}" stroke="{TEAL}" stroke-width="1.5"/>')
    L.append(f'<line x1="60" y1="1" x2="{W-60}" y2="1" stroke="rgba(100,160,255,0.3)" stroke-width="0.5"/>')
    L.append(f'<rect x="0" y="0" width="{W}" height="42" fill="{TEAL}" fill-opacity="0.05"/>')
    L.append(f'<rect x="0" y="42" width="{W}" height="1" fill="{BORDER}"/>')
    L.append(f'<circle cx="22" cy="21" r="4" fill="{TEAL}"><animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/></circle>')
    L.append(f'<circle cx="22" cy="21" r="10" fill="{TEAL}" fill-opacity="0">'
             f'<animate attributeName="r" values="5;13;5" dur="2s" repeatCount="indefinite"/>'
             f'<animate attributeName="fill-opacity" values="0.12;0;0.12" dur="2s" repeatCount="indefinite"/>'
             f'</circle>')
    L.append(f'<text x="34" y="16" class="title">Tech Deployment Map</text>')
    L.append(f'<text x="34" y="30" class="sub">@ME-MOIR · STACK INFLUENCE ZONES · AMBER = PRIMARY · BLUE = SECONDARY</text>')
    L.append(f'<text x="{W-22}" y="16" class="sub" text-anchor="end">NEXT.JS · REACT · TS · THREE.JS · PALANTIR</text>')
    L.append(f'<text x="{W-22}" y="30" class="sub" text-anchor="end">AWS · GCP · VERCEL · POSTGRESQL · PRISMA</text>')

    # legend + sync
    LX, LY = MAP_X, H - 16
    L.append(f'<circle cx="{LX+6}" cy="{LY}" r="3" fill="{AMBER}" filter="url(#g3)"/>')
    L.append(f'<text x="{LX+14}" y="{LY+4}" class="sub">PRIMARY HUB</text>')
    L.append(f'<circle cx="{LX+108}" cy="{LY}" r="2.5" fill="{TEAL}" filter="url(#g3)"/>')
    L.append(f'<text x="{LX+116}" y="{LY+4}" class="sub">SECONDARY HUB</text>')
    L.append(f'<circle cx="{LX+226}" cy="{LY}" r="4" fill="{AMBER}" filter="url(#g3)"/>')
    L.append(f'<text x="{LX+235}" y="{LY+4}" class="sub">HOME BASE ( MANILA · PH )</text>')
    ts = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    L.append(f'<text x="{W-22}" y="{LY+4}" class="sub" text-anchor="end">SYNCED {ts}</text>')

    L.append('</svg>')
    return "\n".join(L)


def main():
    # 1. Load accurate landmass paths
    try:
        land_paths = fetch_geojson_paths()
    except Exception as exc:
        print(f"⚠ GeoJSON fetch failed ({exc}), using fallback outlines")
        land_paths = FALLBACK_PATHS

    # 2. Fetch contribution total
    total = 0
    try:
        total = fetch_total()
        print(f"✅ Contributions: {total}")
    except Exception as exc:
        print(f"⚠ Contributions fetch failed ({exc})")

    # 3. Build & write SVG
    svg = build_svg(land_paths, total)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Written {OUTPUT_PATH}")


if __name__ == "__main__":
    main()