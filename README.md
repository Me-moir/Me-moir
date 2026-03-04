<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Me-moir // OPERATOR PROFILE</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg:       #060d0d;
    --panel:    #080f10;
    --border:   #0d2f2f;
    --teal:     #00d9c8;
    --teal2:    #00b5a5;
    --teal3:    #00d9c8;
    --amber:    #ffab00;
    --red:      #ff1744;
    --dim:      #0d3a3a;
    --text:     #a8cece;
    --textdim:  #2a5a5a;
    --white:    #e0f5f5;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
  }

  /* Scanline overlay */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,217,200,0.012) 2px,
      rgba(0,217,200,0.012) 4px
    );
    pointer-events: none;
    z-index: 999;
  }

  /* Grid bg */
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,217,200,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,217,200,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .wrapper {
    position: relative;
    z-index: 1;
    max-width: 980px;
    margin: 0 auto;
    padding: 24px 20px;
  }

  /* ── TOP BAR ── */
  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid var(--border);
    border-bottom: 2px solid var(--teal);
    padding: 10px 20px;
    margin-bottom: 20px;
    background: var(--panel);
    position: relative;
    overflow: hidden;
  }
  .topbar::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--teal), transparent);
    animation: scanH 4s linear infinite;
  }
  @keyframes scanH {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
  .topbar-left {
    display: flex; align-items: center; gap: 14px;
  }
  .status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--teal);
    box-shadow: 0 0 8px var(--teal);
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%,100% { opacity: 1; box-shadow: 0 0 6px var(--teal); }
    50% { opacity: 0.4; box-shadow: 0 0 16px var(--teal); }
  }
  .topbar-label {
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    color: var(--textdim);
  }
  .topbar-id {
    font-family: 'Orbitron', monospace;
    font-size: 13px;
    color: var(--teal);
    letter-spacing: 2px;
  }
  .topbar-right {
    font-size: 11px;
    color: var(--textdim);
    text-align: right;
    line-height: 1.7;
  }
  .topbar-right span { color: var(--teal3); }

  /* ── HEADER HERO ── */
  .hero {
    border: 1px solid var(--border);
    background: var(--panel);
    padding: 32px 36px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
  }
  .hero::after {
    content: 'CLASSIFIED';
    position: absolute;
    top: 50%; right: -30px;
    transform: translateY(-50%) rotate(90deg);
    font-family: 'Orbitron', monospace;
    font-size: 60px;
    font-weight: 900;
    color: rgba(0,217,200,0.03);
    letter-spacing: 8px;
    pointer-events: none;
    user-select: none;
  }
  .corner {
    position: absolute;
    width: 16px; height: 16px;
    border-color: var(--teal);
    border-style: solid;
  }
  .corner-tl { top: 0; left: 0; border-width: 2px 0 0 2px; }
  .corner-tr { top: 0; right: 0; border-width: 2px 2px 0 0; }
  .corner-bl { bottom: 0; left: 0; border-width: 0 0 2px 2px; }
  .corner-br { bottom: 0; right: 0; border-width: 0 2px 2px 0; }

  .hero-top {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 20px;
  }
  .hero-title {
    font-family: 'Orbitron', monospace;
    font-size: 42px;
    font-weight: 900;
    color: var(--teal);
    text-shadow: 0 0 30px rgba(0,217,200,0.4);
    letter-spacing: 4px;
    line-height: 1;
  }
  .hero-subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 16px;
    font-weight: 500;
    color: var(--textdim);
    letter-spacing: 6px;
    margin-top: 6px;
    text-transform: uppercase;
  }
  .badge-row {
    display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px;
  }
  .badge {
    font-family: 'Rajdhani', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 4px 12px;
    border: 1px solid var(--teal);
    color: var(--teal);
    background: rgba(0,217,200,0.06);
    text-transform: uppercase;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
  }
  .badge.amber { border-color: var(--amber); color: var(--amber); background: rgba(255,171,0,0.06); }
  .badge.cyan { border-color: var(--teal3); color: var(--teal3); background: rgba(29,233,182,0.06); }

  .hero-meta {
    text-align: right;
    font-size: 11px;
    line-height: 2;
    color: var(--textdim);
  }
  .hero-meta .val { color: var(--teal3); font-size: 13px; }

  /* Typing line */
  .typing-line {
    display: flex; align-items: center; gap: 10px;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
  }
  .prompt { color: var(--teal); font-size: 14px; }
  .typed-text {
    color: var(--white);
    font-size: 14px;
    overflow: hidden;
    white-space: nowrap;
    border-right: 2px solid var(--teal);
    animation: typing 3.5s steps(42) infinite, blink 0.7s step-end infinite alternate;
    width: 42ch;
  }
  @keyframes typing {
    0%,10% { width: 0; }
    50%,90% { width: 42ch; }
    95%,100% { width: 0; }
  }
  @keyframes blink {
    from { border-color: var(--teal); }
    to { border-color: transparent; }
  }

  /* ── GRID LAYOUT ── */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  .grid-full { margin-bottom: 16px; }

  /* ── PANEL ── */
  .panel {
    border: 1px solid var(--border);
    background: var(--panel);
    padding: 20px;
    position: relative;
  }
  .panel-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
  }
  .panel-icon { color: var(--teal); font-size: 12px; }
  .panel-title {
    font-family: 'Orbitron', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--textdim);
    text-transform: uppercase;
    flex: 1;
  }
  .panel-tag {
    font-size: 9px;
    letter-spacing: 1px;
    color: var(--dim);
    border: 1px solid var(--dim);
    padding: 2px 6px;
  }

  /* ── OPERATOR PROFILE ── */
  .operator {
    display: flex; gap: 20px; align-items: flex-start;
  }
  .avatar-wrap {
    position: relative; flex-shrink: 0;
  }
  .avatar-img {
    width: 80px; height: 80px;
    border: 2px solid var(--teal);
    display: block;
    filter: saturate(0.3) contrast(1.2);
    box-shadow: 0 0 20px rgba(0,217,200,0.2);
  }
  .avatar-scan {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(transparent, var(--teal), transparent);
    opacity: 0.8;
    animation: scan 2.5s linear infinite;
  }
  @keyframes scan {
    0% { top: 0; }
    100% { top: 100%; }
  }
  .op-info { flex: 1; }
  .op-row {
    display: flex; justify-content: space-between;
    font-size: 12px; padding: 4px 0;
    border-bottom: 1px solid rgba(26,47,26,0.5);
  }
  .op-key { color: var(--textdim); }
  .op-val { color: var(--white); }
  .op-val.green { color: var(--teal); }
  .op-val.cyan { color: var(--teal3); }

  /* ── SKILL BARS ── */
  .skill-row { margin-bottom: 12px; }
  .skill-top {
    display: flex; justify-content: space-between;
    font-size: 11px; margin-bottom: 5px;
  }
  .skill-name { color: var(--text); font-family: 'Rajdhani', sans-serif; font-size: 13px; font-weight: 600; letter-spacing: 1px; }
  .skill-pct { color: var(--teal); font-family: 'Orbitron', monospace; font-size: 10px; }
  .skill-bar {
    height: 4px;
    background: rgba(0,217,200,0.08);
    border: 1px solid var(--border);
    position: relative;
    overflow: hidden;
  }
  .skill-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--teal2), var(--teal));
    box-shadow: 0 0 8px var(--teal);
    position: relative;
    animation: fillBar 1.5s cubic-bezier(0.4,0,0.2,1) forwards;
    width: 0;
  }
  .skill-fill::after {
    content: '';
    position: absolute;
    right: 0; top: 0; bottom: 0;
    width: 6px;
    background: white;
    opacity: 0.8;
    box-shadow: 0 0 6px white;
  }
  @keyframes fillBar {
    to { width: var(--w); }
  }

  /* ── STAT BOXES ── */
  .stat-box {
    text-align: center;
    padding: 16px 10px;
    border: 1px solid var(--border);
    background: rgba(0,217,200,0.02);
    position: relative;
    overflow: hidden;
  }
  .stat-box::before {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: var(--teal);
    opacity: 0.3;
  }
  .stat-num {
    font-family: 'Orbitron', monospace;
    font-size: 28px;
    font-weight: 700;
    color: var(--teal);
    text-shadow: 0 0 15px rgba(0,217,200,0.5);
    display: block;
  }
  .stat-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--textdim);
    text-transform: uppercase;
    margin-top: 4px;
    display: block;
  }

  /* ── TECH GRID ── */
  .tech-grid {
    display: flex; flex-wrap: wrap; gap: 8px;
  }
  .tech-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    padding: 5px 10px;
    border: 1px solid var(--border);
    color: var(--text);
    background: rgba(0,217,200,0.03);
    display: flex; align-items: center; gap: 6px;
    transition: all 0.2s;
    cursor: default;
    clip-path: polygon(6px 0%,100% 0%,calc(100% - 6px) 100%,0% 100%);
  }
  .tech-tag:hover {
    border-color: var(--teal);
    color: var(--teal);
    background: rgba(0,217,200,0.08);
    box-shadow: 0 0 10px rgba(0,217,200,0.1);
  }
  .tech-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--teal); flex-shrink: 0; }

  /* ── PROJECTS ── */
  .project-card {
    border: 1px solid var(--border);
    padding: 16px;
    background: rgba(0,217,200,0.02);
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
  }
  .project-card:hover {
    border-color: var(--teal);
    background: rgba(0,217,200,0.05);
    box-shadow: inset 0 0 30px rgba(0,217,200,0.03);
  }
  .project-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(var(--teal2), var(--teal));
  }
  .proj-name {
    font-family: 'Orbitron', monospace;
    font-size: 12px;
    color: var(--teal);
    letter-spacing: 1px;
    margin-bottom: 6px;
  }
  .proj-desc {
    font-family: 'Rajdhani', sans-serif;
    font-size: 13px;
    color: var(--textdim);
    line-height: 1.5;
    margin-bottom: 10px;
  }
  .proj-footer {
    display: flex; align-items: center; gap: 10px;
  }
  .proj-lang {
    font-size: 10px;
    padding: 2px 8px;
    border: 1px solid var(--teal3);
    color: var(--teal3);
    letter-spacing: 1px;
  }
  .proj-stars {
    font-size: 11px;
    color: var(--amber);
  }

  /* ── ACTIVITY ── */
  .activity-grid {
    display: flex; flex-direction: column; gap: 4px;
  }
  .activity-row {
    display: flex; align-items: center; gap: 8px; font-size: 11px;
  }
  .act-time { color: var(--textdim); width: 70px; flex-shrink: 0; }
  .act-bar-wrap { flex: 1; height: 3px; background: var(--border); }
  .act-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--teal2), var(--teal));
    box-shadow: 0 0 4px var(--teal);
  }
  .act-label { color: var(--text); width: 80px; text-align: right; flex-shrink: 0; }

  /* ── FOOTER ── */
  .footer-bar {
    display: flex; align-items: center; justify-content: space-between;
    border: 1px solid var(--border);
    border-top: 2px solid var(--teal);
    padding: 12px 20px;
    margin-top: 20px;
    background: var(--panel);
    font-size: 11px;
    position: relative;
  }
  .footer-bar::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--teal3), transparent);
  }
  .footer-left { color: var(--textdim); }
  .footer-center {
    font-family: 'Orbitron', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--dim);
  }
  .footer-right {
    display: flex; align-items: center; gap: 6px;
  }
  .online-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--teal);
    animation: pulse 1.5s ease-in-out infinite;
  }
  .online-label { color: var(--teal); font-size: 11px; letter-spacing: 1px; }

  /* ── LIVE STATS BAR ── */
  .live-bar {
    display: flex; gap: 2px; margin-bottom: 16px;
  }
  .live-seg {
    flex: 1; height: 3px;
    background: var(--teal);
    opacity: 0.2;
    animation: liveAnim 2s ease-in-out infinite;
  }
  .live-seg:nth-child(odd) { animation-delay: 0.3s; }
  .live-seg:nth-child(3n) { animation-delay: 0.6s; opacity: 0.5; }
  @keyframes liveAnim {
    0%,100% { opacity: 0.15; }
    50% { opacity: 0.7; }
  }

  /* Stagger fade-in */
  .panel { animation: fadeUp 0.5s ease forwards; opacity: 0; }
  .panel:nth-child(1) { animation-delay: 0.1s; }
  .panel:nth-child(2) { animation-delay: 0.2s; }
  .panel:nth-child(3) { animation-delay: 0.3s; }
  .grid-2 .panel:nth-child(1) { animation-delay: 0.15s; }
  .grid-2 .panel:nth-child(2) { animation-delay: 0.25s; }
  .grid-3 .panel:nth-child(1) { animation-delay: 0.1s; }
  .grid-3 .panel:nth-child(2) { animation-delay: 0.2s; }
  .grid-3 .panel:nth-child(3) { animation-delay: 0.3s; }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .hero { animation: fadeUp 0.4s ease forwards; opacity: 0; }
  .topbar { animation: fadeUp 0.3s ease forwards; opacity: 0; }

  /* Img placeholder */
  .avatar-placeholder {
    width: 80px; height: 80px;
    border: 2px solid var(--teal);
    background: linear-gradient(135deg, #0a1a0a, #0d200d);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Orbitron', monospace;
    font-size: 22px;
    color: var(--teal);
    letter-spacing: 0;
    box-shadow: 0 0 20px rgba(0,217,200,0.2);
    flex-shrink: 0;
  }

  .github-img {
    display: block;
    width: 100%;
    border: 0;
    filter: hue-rotate(60deg) saturate(0.5) contrast(1.1) brightness(0.9);
  }
</style>
</head>
<body>
<div class="wrapper">

  <!-- TOP BAR -->
  <div class="topbar">
    <div class="topbar-left">
      <div class="status-dot"></div>
      <div>
        <div class="topbar-label">OPERATOR PROFILE // CLEARANCE LEVEL: PUBLIC</div>
        <div class="topbar-id">ID: ME-MOIR // JEKK</div>
      </div>
    </div>
    <div class="topbar-right">
      SYS: <span>ONLINE</span> &nbsp;|&nbsp; NODE: <span>GH-PROD-01</span><br/>
      LAST SYNC: <span id="time">--:--:--</span> UTC
    </div>
  </div>

  <!-- HERO -->
  <div class="hero">
    <div class="corner corner-tl"></div>
    <div class="corner corner-tr"></div>
    <div class="corner corner-bl"></div>
    <div class="corner corner-br"></div>
    <div class="hero-top">
      <div>
        <div class="hero-title">JEKK</div>
        <div class="hero-subtitle">@Me-moir &nbsp;//&nbsp; GitHub</div>
        <div class="badge-row">
          <div class="badge">Full-Stack</div>
          <div class="badge amber">AI / ML</div>
          <div class="badge cyan">Data Eng</div>
          <div class="badge">Builder</div>
        </div>
      </div>
      <div class="hero-meta">
        <div>REPOS <span class="val">04</span></div>
        <div>STARS <span class="val">01</span></div>
        <div>FOLLOWERS <span class="val">02</span></div>
        <div>STATUS <span class="val" style="color:var(--teal)">ACTIVE</span></div>
      </div>
    </div>
    <div class="live-bar">
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
      <div class="live-seg"></div><div class="live-seg"></div><div class="live-seg"></div>
    </div>
    <div class="typing-line">
      <span class="prompt">root@jekk:~$</span>
      <span class="typed-text">Building intelligent systems. Shipping in the dark.</span>
    </div>
  </div>

  <!-- ROW 1: Profile + Skills -->
  <div class="grid-2">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-icon">◈</span>
        <span class="panel-title">Operator Data</span>
        <span class="panel-tag">PROFILE</span>
      </div>
      <div class="operator">
        <div class="avatar-wrap">
          <div class="avatar-placeholder">JK</div>
          <div class="avatar-scan"></div>
        </div>
        <div class="op-info">
          <div class="op-row"><span class="op-key">HANDLE</span><span class="op-val green">Me-moir</span></div>
          <div class="op-row"><span class="op-key">NAME</span><span class="op-val">Jekk</span></div>
          <div class="op-row"><span class="op-key">CLASS</span><span class="op-val cyan">Full-Stack + AI/ML</span></div>
          <div class="op-row"><span class="op-key">FOCUS</span><span class="op-val">Intelligent Systems</span></div>
          <div class="op-row"><span class="op-key">MODE</span><span class="op-val green">lowkey</span></div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-icon">◈</span>
        <span class="panel-title">Skill Proficiency</span>
        <span class="panel-tag">METRICS</span>
      </div>
      <div class="skill-row"><div class="skill-top"><span class="skill-name">Python</span><span class="skill-pct">92%</span></div><div class="skill-bar"><div class="skill-fill" style="--w:92%"></div></div></div>
      <div class="skill-row"><div class="skill-top"><span class="skill-name">TypeScript</span><span class="skill-pct">85%</span></div><div class="skill-bar"><div class="skill-fill" style="--w:85%"></div></div></div>
      <div class="skill-row"><div class="skill-top"><span class="skill-name">ML / AI</span><span class="skill-pct">88%</span></div><div class="skill-bar"><div class="skill-fill" style="--w:88%"></div></div></div>
      <div class="skill-row"><div class="skill-top"><span class="skill-name">React / Node</span><span class="skill-pct">82%</span></div><div class="skill-bar"><div class="skill-fill" style="--w:82%"></div></div></div>
      <div class="skill-row"><div class="skill-top"><span class="skill-name">Data Engineering</span><span class="skill-pct">78%</span></div><div class="skill-bar"><div class="skill-fill" style="--w:78%"></div></div></div>
    </div>
  </div>

  <!-- ROW 2: Stats -->
  <div class="grid-3">
    <div class="panel" style="padding:0;">
      <img class="github-img" src="https://github-readme-stats.vercel.app/api?username=Me-moir&show_icons=true&theme=chartreuse-dark&hide_border=true&bg_color=0a1018&title_color=00d9c8&icon_color=00d9c8&text_color=a8c8a8" alt="GitHub Stats" onerror="this.style.display='none';this.nextElementSibling.style.display='block'"/>
      <div style="display:none;padding:20px;">
        <div class="panel-header"><span class="panel-icon">◈</span><span class="panel-title">GitHub Stats</span></div>
        <div class="stat-box"><span class="stat-num" id="commits">—</span><span class="stat-label">Total Commits</span></div>
      </div>
    </div>
    <div class="panel" style="padding:0;">
      <img class="github-img" src="https://github-readme-streak-stats.herokuapp.com/?user=Me-moir&theme=chartreuse-dark&hide_border=true&background=0a1018&ring=00d9c8&fire=00d9c8&currStreakLabel=00d9c8&sideLabels=a8c8a8&dates=4a6a4a" alt="Streak" onerror="this.style.display='none'"/>
    </div>
    <div class="panel" style="padding:0;">
      <img class="github-img" src="https://github-readme-stats.vercel.app/api/top-langs/?username=Me-moir&layout=compact&theme=chartreuse-dark&hide_border=true&bg_color=0a1018&title_color=00d9c8&text_color=a8c8a8" alt="Languages" onerror="this.style.display='none'"/>
    </div>
  </div>

  <!-- ROW 3: Tech Arsenal -->
  <div class="grid-full">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-icon">◈</span>
        <span class="panel-title">Tech Arsenal</span>
        <span class="panel-tag">LOADOUT</span>
      </div>
      <div class="tech-grid">
        <div class="tech-tag"><span class="tech-dot"></span>Python</div>
        <div class="tech-tag"><span class="tech-dot"></span>TypeScript</div>
        <div class="tech-tag"><span class="tech-dot"></span>JavaScript</div>
        <div class="tech-tag"><span class="tech-dot" style="background:var(--teal3)"></span>React</div>
        <div class="tech-tag"><span class="tech-dot" style="background:var(--teal3)"></span>Node.js</div>
        <div class="tech-tag"><span class="tech-dot" style="background:var(--teal3)"></span>FastAPI</div>
        <div class="tech-tag"><span class="tech-dot" style="background:var(--amber)"></span>TensorFlow</div>
        <div class="tech-tag"><span class="tech-dot" style="background:var(--amber)"></span>PyTorch</div>
        <div class="tech-tag"><span class="tech-dot" style="background:var(--amber)"></span>scikit-learn</div>
        <div class="tech-tag"><span class="tech-dot"></span>PostgreSQL</div>
        <div class="tech-tag"><span class="tech-dot"></span>Docker</div>
        <div class="tech-tag"><span class="tech-dot"></span>Git</div>
        <div class="tech-tag"><span class="tech-dot" style="background:var(--teal3)"></span>HTML5 / CSS3</div>
        <div class="tech-tag"><span class="tech-dot" style="background:var(--amber)"></span>Pandas / NumPy</div>
      </div>
    </div>
  </div>

  <!-- ROW 4: Projects -->
  <div class="grid-2">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-icon">◈</span>
        <span class="panel-title">Active Deployments</span>
        <span class="panel-tag">PROJECTS</span>
      </div>
      <div style="display:flex;flex-direction:column;gap:10px;">
        <div class="project-card">
          <div class="proj-name">NOTUS-REGALIA</div>
          <div class="proj-desc">Static landing page for a startup. Built for conversion.</div>
          <div class="proj-footer">
            <span class="proj-lang">TypeScript</span>
            <span class="proj-stars">★ 1</span>
          </div>
        </div>
        <div class="project-card">
          <div class="proj-name">PROJECT-CLAIRE.AI</div>
          <div class="proj-desc">AI-powered project. Python backend intelligence layer.</div>
          <div class="proj-footer">
            <span class="proj-lang">Python</span>
            <span class="proj-stars">★ 0</span>
          </div>
        </div>
        <div class="project-card">
          <div class="proj-name">KIZUNA-TREE</div>
          <div class="proj-desc">JavaScript project. Connection and link system.</div>
          <div class="proj-footer">
            <span class="proj-lang">JavaScript</span>
          </div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-icon">◈</span>
        <span class="panel-title">Contribution Map</span>
        <span class="panel-tag">LIVE</span>
      </div>
      <img class="github-img" style="border-radius:0;width:100%" src="https://github-readme-activity-graph.vercel.app/graph?username=Me-moir&bg_color=0a1018&color=00d9c8&line=00d9c8&point=ffffff&area=true&hide_border=true&area_color=00d9c8" alt="Activity Graph" onerror="this.style.display='none'"/>

      <div style="margin-top:16px;">
        <div class="panel-header" style="margin-bottom:10px">
          <span class="panel-icon">◈</span>
          <span class="panel-title">Mission Parameters</span>
        </div>
        <div class="activity-grid">
          <div class="activity-row">
            <span class="act-time">Full-Stack</span>
            <div class="act-bar-wrap"><div class="act-bar" style="width:85%"></div></div>
            <span class="act-label">PRIMARY</span>
          </div>
          <div class="activity-row">
            <span class="act-time">AI / ML</span>
            <div class="act-bar-wrap"><div class="act-bar" style="width:80%;background:linear-gradient(90deg,var(--amber),var(--amber))"></div></div>
            <span class="act-label">SECONDARY</span>
          </div>
          <div class="activity-row">
            <span class="act-time">Data Eng</span>
            <div class="act-bar-wrap"><div class="act-bar" style="width:70%;background:linear-gradient(90deg,var(--teal3),var(--teal3))"></div></div>
            <span class="act-label">SUPPORT</span>
          </div>
          <div class="activity-row">
            <span class="act-time">DevOps</span>
            <div class="act-bar-wrap"><div class="act-bar" style="width:50%"></div></div>
            <span class="act-label">AUXILIARY</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="footer-bar">
    <div class="footer-left">github.com/Me-moir &nbsp;//&nbsp; PRO</div>
    <div class="footer-center">// OPERATOR PROFILE v1.0 //</div>
    <div class="footer-right">
      <div class="online-dot"></div>
      <span class="online-label">ONLINE</span>
    </div>
  </div>

</div>

<script>
  function tick() {
    const now = new Date();
    const h = String(now.getUTCHours()).padStart(2,'0');
    const m = String(now.getUTCMinutes()).padStart(2,'0');
    const s = String(now.getUTCSeconds()).padStart(2,'0');
    document.getElementById('time').textContent = `${h}:${m}:${s}`;
  }
  tick(); setInterval(tick, 1000);
</script>
</body>
</html>
