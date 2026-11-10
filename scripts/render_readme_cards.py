#!/usr/bin/env python3
"""
Render the profile README's cards as animated SVGs into cards/.

Theme: "Retro 8-Bit Arcade / Game Boy Universe"
- Pixel fonts: Silkscreen, embedded base64 WOFF2
- Arcade HUD: 1UP, HIGH SCORE, INSERT COIN / PRESS START
- 8-bit Health & Mana: [♥♥♥♥♡], EXP Gauge, RPG Attributes
- Retro Green Phosphor CRT Terminal with animated ASCII face portrait
- Stage Clear Quest Log & Combo Multipliers
- Game Cartridge Repository Cards

Run locally or by .github/workflows/update-profile-art.yml.
"""
import base64
import datetime
import html
import json
import os
import random
import re
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")

os.makedirs(OUT, exist_ok=True)

# ---- Configuration ----------------------------------------------------------
USERNAME = "JoyTheSloth"
DISPLAY_NAME_FIRST = "Joydeep"
DISPLAY_NAME_LAST = "Das"
ROLE = "FRONTEND & CREATIVE ENGINEER"
TAGLINE_LINE1 = "I build creative web apps, interactive interfaces,"
TAGLINE_LINE2 = "and high-performance digital experiences."
PROFILE_URL = "github.com/JoyTheSloth"

# Retro Arcade Color Palette
ARCADE_BG = "#0d1117"        # Dark arcade obsidian
ARCADE_CARD = "#121720"      # Card interior
ARCADE_FRAME = "#30363d"     # Pixel border
ARCADE_CRT = "#0b1510"       # Green CRT monitor frame
NEON_GREEN = "#00ff66"       # 1UP / Phosphor green
NEON_CYAN = "#00e5ff"        # Mana / EXP
ARCADE_GOLD = "#ffd700"      # Coin / High Score
HEART_RED = "#ff2a5f"        # 8-bit health
PURPLE = "#a855f7"           # Relic / Special
INK_LIGHT = "#f0f6fc"        # Primary pixel text
MUTED_PIXEL = "#8b949e"      # Subtext

W = 880                      # Full column width
BOTTOM = 14                  # Vertical transparent gap

PIXEL = "'Silkscreen', monospace"
MONO = "'Geist Mono', ui-monospace, monospace"
SANS = "Geist, system-ui, sans-serif"
SERIF = "'Instrument Serif', Georgia, serif"

FONT_FILES = {
    "pixel": ("Silkscreen", "normal", 400, "silkscreen.woff2"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
}

STATIC = bool(os.environ.get("STATIC"))

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes sheen{0%{transform:translateX(-300px) skewX(-20deg)}30%,100%{transform:translateX(650px) skewX(-20deg)}}
@keyframes ring{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.4)}}
@keyframes flash{0%{filter:brightness(2.4)}45%{filter:brightness(2.4)}100%{filter:brightness(1)}}
@keyframes flame{0%,100%{transform:scale(1) rotate(-2deg);filter:drop-shadow(0 0 3px rgba(255,42,95,0.5))}50%{transform:scale(1.18) rotate(3deg);filter:drop-shadow(0 0 8px rgba(255,215,0,0.9))}}
@keyframes flamecore{0%,100%{transform:scale(0.88);opacity:.85}50%{transform:scale(1.22);opacity:1}}
@keyframes glowpulse{0%,100%{opacity:0.35}50%{opacity:0.8}}
@keyframes starTwinkle1{0%,100%{opacity:.2}50%{opacity:1}}
@keyframes starTwinkle2{0%,100%{opacity:.95}50%{opacity:.15}}
@keyframes alienMarch{0%,100%{transform:translateY(0) translateX(0)}25%{transform:translateY(-4px) translateX(3px)}50%{transform:translateY(0) translateX(6px)}75%{transform:translateY(-4px) translateX(3px)}}
@keyframes bossHover{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-6px) scale(1.04)}}
@keyframes bossShield{0%,100%{transform:scale(1);filter:drop-shadow(0 0 3px #ff2a5f)}50%{transform:scale(1.18);filter:drop-shadow(0 0 14px #ff2a5f)}}
@keyframes beamStream{0%{stroke-dashoffset:28}100%{stroke-dashoffset:0}}
@keyframes beamSurge{0%,100%{opacity:0.25;transform:scaleX(0.92)}50%{opacity:0.62;transform:scaleX(1.35)}}
@keyframes corePulse{0%,100%{opacity:0.85;filter:brightness(1)}50%{opacity:1;filter:brightness(1.4)}}
@keyframes shipPatrol{0%{transform:translateX(-190px)}35%{transform:translateX(190px)}65%{transform:translateX(-100px)}100%{transform:translateX(-190px)}}
@keyframes hitBurst{0%,100%{transform:scale(0.65) rotate(0deg);opacity:0.45}50%{transform:scale(1.45) rotate(45deg);opacity:1}}
@keyframes sparkRing{0%,100%{transform:scale(0.7);opacity:0.6}50%{transform:scale(1.8);opacity:0.1}}
@keyframes fireLaser{0%{transform:translateY(0);opacity:1}80%{opacity:1}100%{transform:translateY(-125px);opacity:0}}
@keyframes thruster{0%,100%{transform:scaleY(.8);opacity:.75}50%{transform:scaleY(1.35);opacity:1}}
@keyframes radarSweep{0%{transform:translateY(0);opacity:0}15%{opacity:0.35}85%{opacity:0.35}100%{transform:translateY(165px);opacity:0}}
@keyframes shipSweep{0%{transform:translateX(74px)}50%{transform:translateX(784px)}100%{transform:translateX(74px)}}
@keyframes blasterBolt{0%{transform:translateY(0);opacity:1}80%{opacity:1}100%{transform:translateY(-130px);opacity:0}}
@keyframes blockBlast{0%,1%{opacity:1;transform:scale(1);filter:none}3%{opacity:1;transform:scale(1.35);filter:brightness(3.5)}6%,28%{opacity:0;transform:scale(0.1)}33%{opacity:0.8;transform:scale(1.2);filter:brightness(1.8)}37%,100%{opacity:1;transform:scale(1);filter:none}}
@keyframes blockBlastDim{0%,1%{opacity:1;transform:scale(1)}3%{opacity:0.8;transform:scale(1.15);filter:brightness(2.0)}6%,28%{opacity:0.08;transform:scale(0.2)}33%{opacity:0.7;transform:scale(1.1)}37%,100%{opacity:1;transform:scale(1)}}
@keyframes sparkFlash{0%,2%{opacity:0;transform:scale(0)}3%{opacity:1;transform:scale(1.6) rotate(45deg)}5%{opacity:0;transform:scale(2.2) rotate(90deg)}6%,100%{opacity:0}}

.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.blk{animation:blink 1.0s step-end infinite}
.live{animation:pulse 1.6s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.sh{animation:sheen 4.5s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1s ease-out both}
.pf{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s ease-out both, flash .65s ease-out both}
.flame{transform-box:fill-box;transform-origin:center bottom;animation:flame 1.3s ease-in-out infinite}
.flamecore{transform-box:fill-box;transform-origin:center bottom;animation:flamecore 0.85s ease-in-out infinite}
.gp{animation:glowpulse 2s ease-in-out infinite}
.st1{animation:starTwinkle1 2.2s ease-in-out infinite}
.st2{animation:starTwinkle2 1.7s ease-in-out infinite}
.abob{transform-box:fill-box;transform-origin:center;animation:alienMarch 2.2s ease-in-out infinite}
.bbob{transform-box:fill-box;transform-origin:center;animation:bossHover 2.2s ease-in-out infinite}
.bshield{transform-box:fill-box;transform-origin:center;animation:bossShield 1.6s ease-in-out infinite}
.bsurge{transform-box:fill-box;transform-origin:center;animation:beamSurge 1.3s ease-in-out infinite}
.cpulse{animation:corePulse 1.0s ease-in-out infinite}
.stream{animation:beamStream 0.42s linear infinite}
.spatrol{transform-box:fill-box;animation:shipPatrol 8.5s ease-in-out infinite}
.burst{transform-box:fill-box;transform-origin:center;animation:hitBurst 0.9s ease-in-out infinite}
.sring{transform-box:fill-box;transform-origin:center;animation:sparkRing 0.9s ease-in-out infinite}
.flaser{transform-box:fill-box;animation:fireLaser 0.65s linear infinite}
.thrust{transform-box:fill-box;transform-origin:top center;animation:thruster 0.25s ease-in-out infinite}
.radar{transform-box:fill-box;animation:radarSweep 3.6s ease-in-out infinite}
.ssweep{animation:shipSweep 8.0s linear infinite}
.bbolt{transform-box:fill-box;animation:blasterBolt .35s linear infinite}
.bhit{transform-box:fill-box;transform-origin:center;animation:blockBlast 8.0s ease-out infinite}
.bhit-dim{transform-box:fill-box;transform-origin:center;animation:blockBlastDim 8.0s ease-out infinite}
.sflash{transform-box:fill-box;transform-origin:center;animation:sparkFlash 8.0s ease-out infinite}

@media (prefers-reduced-motion: reduce){
  .r,.f,.g,.p,.pf,.live,.n,.rg,.flame,.flamecore,.gp,.blk,.st1,.st2,.abob,.bbob,.bshield,.bsurge,.cpulse,.stream,.spatrol,.burst,.sring,.flaser,.thrust,.radar,.ssweep,.bbolt,.bhit,.bhit-dim,.sflash{animation:none!important;opacity:1!important;transform:none!important}
  .sh,.rg,.flaser,.stream,.radar,.bbolt,.sflash{display:none}
}
"""

def font_face(keys):
    out = []
    for k in keys:
        if k not in FONT_FILES:
            continue
        fam, style, weight, fn = FONT_FILES[k]
        path = os.path.join(FONTS, fn)
        if os.path.exists(path):
            b64 = base64.b64encode(open(path, "rb").read()).decode()
            fmt = "woff2" if fn.endswith(".woff2") else "woff"
            out.append(
                f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                f"font-display:swap;src:url(data:font/{fmt};base64,{b64}) format('{fmt}');}}"
            )
    return "".join(out)

def d(delay):
    if STATIC:
        return 'style="opacity:1!important;transform:none!important;animation:none!important"'
    return f'style="animation-delay:{delay:.2f}s"'

def svg(w, h, body, fonts, title, left=0, right=0, top=0, bottom=BOTTOM, defs=""):
    vb_w, vb_h = w + left + right, h + top + bottom
    css = font_face(fonts) + BASE_CSS
    content = f'<g transform="translate({left} {top})">{body}</g>' if (left or top) else body
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb_w:.3f}" height="{vb_h}" '
        f'viewBox="0 0 {vb_w:.3f} {vb_h}" role="img" aria-label="{escape(title)}">\n'
        f'<title>{escape(title)}</title>\n'
        f'<style>{css}</style>\n'
        f'{defs}\n'
        f'{content}\n</svg>'
    )

def write(name, content):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {name}: {len(content)//1024} KB")

# ---- 1 · Hero Card (Editorial Light Paper Card with Floating ASCII Portrait) --
def load_light_portrait_lines():
    portrait_file = os.path.join(ROOT, "portrait.svg")
    if not os.path.exists(portrait_file):
        portrait_file = os.path.join(ROOT, "portrait-face.svg")
    if not os.path.exists(portrait_file):
        return []

    src = open(portrait_file, encoding="utf-8").read()
    rows = re.findall(r'<text [^>]*\bxml:space="preserve"[^>]*\by="([\d.]+)"[^>]*>(.*?)</text>', src, re.S)
    if not rows:
        rows = re.findall(r'<text [^>]*\by="([\d.]+)"[^>]*>(.*?)</text>', src, re.S)

    portrait_lines = []
    for i, (y, txt) in enumerate(rows):
        delay = 0.15 + i * 0.010
        portrait_lines.append(
            f'<text class="f" {d(delay)} xml:space="preserve" x="20" y="{y}" '
            f'fill="#1c1b18" font-size="7.3" textLength="800" lengthAdjust="spacing">{txt}</text>'
        )
    return portrait_lines

def hero(data):
    portrait_lines = load_light_portrait_lines()
    s = 0.48
    portrait_markup = f"""
<!-- High-Resolution Floating Monochrome ASCII Portrait -->
<g transform="translate(460, 16) scale({s})" font-family="{MONO}">
  {''.join(portrait_lines)}
</g>"""

    body = f"""
<!-- Clean Ivory / Off-White Paper Background -->
<rect width="{W}" height="430" rx="16" fill="#f8f8f7" stroke="#e6e6e1"/>

<!-- Role Header Pill -->
<g class="r" {d(0.05)}>
  <rect x="50" y="50" width="8" height="8" rx="2" fill="#2563eb"/>
  <text x="68" y="58" font-family="{MONO}" font-size="11.5" font-weight="600" letter-spacing="2" fill="#64748b">{escape(ROLE)}</text>
</g>

<!-- Name Typography: Instrument Serif Large Display -->
<text class="r" {d(0.14)} x="50" y="158" font-family="{SERIF}" font-size="80" fill="#18181b">{escape(DISPLAY_NAME_FIRST)}</text>
<text class="r" {d(0.24)} x="50" y="238" font-family="{SERIF}" font-style="italic" font-size="80" fill="#18181b">{escape(DISPLAY_NAME_LAST)}</text>

<!-- Tagline & Bio -->
<g class="r" {d(0.34)}>
  <text x="50" y="304" font-family="{SANS}" font-size="16" fill="#475569">{escape(TAGLINE_LINE1)}</text>
  <text x="50" y="332" font-family="{SANS}" font-size="16" fill="#475569">{escape(TAGLINE_LINE2)}</text>
</g>

<!-- Profile Link with Arrow -->
<g class="r" {d(0.44)}>
  <text x="50" y="384" font-family="{MONO}" font-size="13" fill="#64748b">{PROFILE_URL} <tspan fill="#2563eb">↗</tspan></text>
</g>

{portrait_markup}
"""
    write("hero.svg", svg(W, 430, body, ["serif", "serif-i", "sans", "mono"],
                          f"{DISPLAY_NAME_FIRST} {DISPLAY_NAME_LAST} - {ROLE}"))

# ---- 2 · Blue/Green Arcade Contribution Heatmap ("Quest Map") ----------------
ARCADE_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", NEON_GREEN]

def level_for(c):
    return 0 if c == 0 else 1 if c <= 3 else 2 if c <= 8 else 3 if c <= 15 else 4

def make_heatmap_player_ship():
    return (
        '<g>'
        '<!-- Fuselage & Wings (8-bit arcade starfighter) -->'
        '<path d="M-1 -12 h2 v4 h-2z M-2 -8 h4 v4 h-4z M-4 -4 h8 v4 h-8z M-8 0 h16 v4 h-16z M-14 4 h28 v4 h-28z M-14 8 h4 v3 h-4z M10 8 h4 v3 h-4z M-6 4 h12 v5 h-12z" fill="#f0f6fc"/>'
        '<!-- Cockpit Visor -->'
        f'<rect x="-1" y="-6" width="2" height="4" fill="{NEON_CYAN}"/>'
        '<!-- Wing Blasters -->'
        f'<rect x="-12" y="-1" width="2" height="5" fill="{NEON_GREEN}"/>'
        f'<rect x="10" y="-1" width="2" height="5" fill="{NEON_GREEN}"/>'
        '<!-- Twin Plasma Thrusters (Flickering) -->'
        '<g class="thrust">'
        '<polygon points="-5,12 -3,17 -1,12" fill="#ff9900"/>'
        '<polygon points="-4,12 -3,15 -2,12" fill="#ffff00"/>'
        '<polygon points="1,12 3,17 5,12" fill="#ff9900"/>'
        '<polygon points="2,12 3,15 4,12" fill="#ffff00"/>'
        '</g>'
        '<!-- Continuous Dual Laser Salvos (Alternating High-Speed Bolts Firing Upward) -->'
        '<g class="bbolt">'
        f'<rect x="-12" y="-12" width="2.5" height="14" rx="1" fill="{NEON_GREEN}"/>'
        f'<rect x="9.5" y="-12" width="2.5" height="14" rx="1" fill="{NEON_GREEN}"/>'
        '</g>'
        '<g class="bbolt" style="animation-delay:-0.175s">'
        f'<rect x="-12" y="-12" width="2.5" height="14" rx="1" fill="{NEON_CYAN}"/>'
        f'<rect x="9.5" y="-12" width="2.5" height="14" rx="1" fill="{NEON_CYAN}"/>'
        '</g>'
        '</g>'
    )

def heatmap(data):
    days = data.get("days", [])
    if not days:
        return
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7
    cell, step, gx, gy = 12, 15, 44, 102
    cells, months, seen, sparks = [], [], set(), []

    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        date = datetime.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen and row == 0:
            seen.add((date.year, date.month))
            months.append((col, date.strftime("%b").upper()))
        c = day["count"]

        # Space shooter hit & disappearing/reappearing animation synchronized with player ship sweep
        if 2 <= col <= 50:
            t_delay = (col - 2) / 11.833
            cell_cls = "bhit" if c > 0 else "bhit-dim"
            cell_anim = f'animation-delay:{t_delay:.2f}s'
            if c > 0:
                sparks.append(
                    f'<polygon class="sflash" style="animation-delay:{t_delay:.2f}s" '
                    f'transform="translate({gx + col * step + 6}, {gy + row * step + 6})" '
                    f'points="0,-6 1.8,-1.8 6,0 1.8,1.8 0,6 -1.8,1.8 -6,0 -1.8,-1.8" fill="#ffffff"/>'
                )
        else:
            delay = 1.0 + col * 0.022 + row * 0.014
            cell_cls = "pf" if c > 0 else "p"
            cell_anim = f'animation-delay:{delay:.2f}s'

        cells.append(
            f'<rect class="{cell_cls}" style="{cell_anim}" x="{gx + col * step}" y="{gy + row * step}" '
            f'width="{cell}" height="{cell}" rx="2" fill="{ARCADE_COLORS[level_for(c)]}">'
            f'<title>{day["date"]}: {c} blocks cleared</title></rect>'
        )

    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    sheen_w = ncols * step
    ship_y = gy + 7 * step + 20
    labels_y = ship_y + 24
    h = labels_y + 24

    labels = "".join(
        f'<text x="{gx + col * step}" y="{labels_y + 4}" font-family="{PIXEL}" font-size="9" fill="{MUTED_PIXEL}">{m}</text>'
        for col, m in months if col < ncols - 12
    )
    legend_x = right - len(ARCADE_COLORS) * 14
    legend = "".join(
        f'<rect x="{legend_x + i * 14}" y="{labels_y - 6}" width="11" height="11" rx="2" fill="{c}"/>'
        for i, c in enumerate(ARCADE_COLORS)
    )

    sheen_defs = f"""
<linearGradient id="grid-sheen" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
  <stop offset="50%" stop-color="#ffffff" stop-opacity="0.09"/>
  <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
</linearGradient>
<clipPath id="grid-clip">
  <rect x="{gx}" y="{gy}" width="{sheen_w}" height="{7 * step}" rx="4"/>
</clipPath>
"""
    body = f"""
<rect width="{W}" height="{h}" rx="12" fill="{ARCADE_BG}" stroke="{ARCADE_FRAME}"/>
<text class="r" {d(0.8)} x="42" y="55" font-family="{PIXEL}" font-size="16" fill="{ARCADE_GOLD}">WORLD 1-1: <tspan fill="{NEON_GREEN}">COMMIT VALLEY</tspan></text>
<text class="f" {d(0.8)} x="{right}" y="52" text-anchor="end" font-family="{PIXEL}" font-size="10" fill="{ARCADE_GOLD}">★ COIN × {data['total_contributions']}</text>
<text class="f" {d(1.0)} x="42" y="80" font-family="{MONO}" font-size="11" fill="{MUTED_PIXEL}">SPACE SHOOTER // BLASTING &amp; CLEARING 368 BLOCKS ACROSS COMMIT VALLEY</text>

<!-- Contribution Blocks Matrix (Disappearing when shot & respawning in infinite loop) -->
{''.join(cells)}

<!-- Impact Sparks when Blocks are Blasted -->
{''.join(sparks)}

<!-- Ambient Scanning Grid Sheen Wave -->
<rect class="sh" clip-path="url(#grid-clip)" x="{gx}" y="{gy}" width="220" height="{7 * step}" fill="url(#grid-sheen)"/>

<!-- Space Shooter Starfighter Patrolling & Blasting Blocks -->
<g class="ssweep" transform="translate(0, {ship_y})">
  {make_heatmap_player_ship()}
</g>

<!-- Timeline Labels & Legend -->
<g class="f" {d(2.2)}>{labels}
<text x="{legend_x - 8}" y="{labels_y + 4}" text-anchor="end" font-family="{PIXEL}" font-size="8" fill="{MUTED_PIXEL}">MIN</text>
{legend}
<text x="{legend_x + len(ARCADE_COLORS) * 14 + 4}" y="{labels_y + 4}" font-family="{PIXEL}" font-size="8" fill="{MUTED_PIXEL}">MAX</text></g>
"""
    write("heatmap.svg", svg(W, h, body, ["pixel", "mono"],
                             f'World Map: {data["total_contributions"]:,} blocks cleared', defs=sheen_defs))

# ---- 3 · Activity & Stage Clear ("Quest Log & Attributes") --------------------
def short_date(d_str):
    if not d_str:
        return "—"
    dt = datetime.date.fromisoformat(d_str)
    return f"{dt.strftime('%b').upper()} {dt.day}"

def make_count_up(x, y, target_val, suffix, fg_color, delay, font_family, font_size=28, frames=14, dur=1.0):
    val_clean = re.sub(r"[^\d.]", "", str(target_val))
    try:
        val_target = float(val_clean) if val_clean else 0.0
    except:
        val_target = 0.0

    if val_target == 0:
        return (f'<text x="{x}" y="{y}" font-family="{font_family}" font-size="{font_size}" fill="{fg_color}">'
                f'0<tspan font-size="{int(font_size*0.45)}" font-family="{PIXEL}" fill="{MUTED_PIXEL}">{suffix}</tspan></text>')

    count_start = delay
    count_elems = []
    for k in range(1, frames + 1):
        p = k / frames
        cur_val = val_target * (1 - (1 - p) ** 3)
        formatted = f"{int(round(cur_val))}" if val_target >= 1 else f"{cur_val:.1f}"
        t_on = count_start + dur * (k - 1) / frames
        t_off = count_start + dur * k / frames
        anim = f'<set attributeName="opacity" to="1" begin="{t_on:.3f}s"/>'
        if k < frames:
            anim += f'<set attributeName="opacity" to="0" begin="{t_off:.3f}s"/>'
        count_elems.append(
            f'<text x="{x}" y="{y}" opacity="{1 if STATIC and k == frames else 0}" font-family="{font_family}" '
            f'font-size="{font_size}" fill="{fg_color}">{formatted}'
            f'<tspan font-size="{int(font_size*0.45)}" font-family="{PIXEL}" fill="{MUTED_PIXEL}">{suffix}</tspan>{anim}</text>'
        )
    return "".join(count_elems)

def make_space_invader(cx, cy, color, variant=0, scale=1.0):
    delay_s = (cx % 7) * 0.2
    if variant == 0:  # Crab invader
        return (
            f'<g class="abob" style="animation-delay:{delay_s:.2f}s" '
            f'transform="translate({cx - 9*scale:.1f}, {cy - 6*scale:.1f}) scale({scale})">'
            f'<path d="M6 0h6v2h-6z M2 2h14v2h-14z M0 4h18v4h-2v2h-2v2h-2v-2h-6v2h-2v-2h-2v-2h-2z '
            f'M4 6h2v2h-2z M12 6h2v2h-2z M0 2h2v4h-2z M16 2h2v4h-2z" fill="{color}"/>'
            f'</g>'
        )
    elif variant == 1:  # Squid invader
        return (
            f'<g class="abob" style="animation-delay:{delay_s:.2f}s" '
            f'transform="translate({cx - 8*scale:.1f}, {cy - 7*scale:.1f}) scale({scale})">'
            f'<path d="M6 0h4v2h-4z M4 2h8v2h-8z M2 4h12v4h-2v4h-2v-2h-4v2h-2v-4h-2z '
            f'M4 6h2v2h-2z M10 6h2v2h-2z M0 8h2v5h-2z M14 8h2v5h-2z" fill="{color}"/>'
            f'</g>'
        )
    else:  # Scout / Drone
        return (
            f'<g class="abob" style="animation-delay:{delay_s:.2f}s" '
            f'transform="translate({cx - 6*scale:.1f}, {cy - 5*scale:.1f}) scale({scale})">'
            f'<path d="M4 0h4v2h-4z M2 2h8v2h-8z M0 4h12v3h-2v2h-2v-2h-4v2h-2v-2h-2z M3 5h2v1h-2z M7 5h2v1h-2z" fill="{color}"/>'
            f'</g>'
        )

def make_boss_mothership(cx, cy, scale=1.0):
    return (
        f'<g class="bbob" transform="translate({cx - 20*scale:.1f}, {cy - 10*scale:.1f}) scale({scale})">'
        f'<!-- Boss Energy Shield (Infinite Loop) -->'
        f'<ellipse cx="{20*scale:.1f}" cy="{10*scale:.1f}" rx="{26*scale:.1f}" ry="{14*scale:.1f}" fill="{HEART_RED}" opacity="0.22" class="bshield"/>'
        f'<!-- Mothership Core Hull -->'
        f'<path d="M12 0h16v2h-16z M8 2h24v2h-24z M4 4h32v4h-32z M0 8h40v4h-4v3h-4v2h-6v-2h-12v2h-6v-2h-4v-3h-4z" fill="{HEART_RED}"/>'
        f'<path d="M14 5h12v3h-12z" fill="{ARCADE_GOLD}"/>'
        f'<circle cx="{20*scale:.1f}" cy="6.5" r="2.5" fill="#ffffff"/>'
        f'<rect x="6" y="8" width="4" height="2" fill="{NEON_CYAN}"/>'
        f'<rect x="30" y="8" width="4" height="2" fill="{NEON_CYAN}"/>'
        f'</g>'
    )

def make_player_ship(cx, cy, scale=0.85):
    return (
        f'<g transform="translate({cx - 14*scale:.1f}, {cy - 12*scale:.1f}) scale({scale})">'
        f'<!-- Fuselage & Wings -->'
        f'<path d="M13 0h2v4h-2z M12 4h4v3h-4z M11 7h6v4h-6z M6 11h16v3h-16z M0 14h28v4h-28z M0 18h4v3h-4z M24 18h4v3h-4z M10 14h8v5h-8z" fill="#f0f6fc"/>'
        f'<!-- Cockpit Visor -->'
        f'<rect x="13" y="6" width="2" height="4" fill="{NEON_CYAN}"/>'
        f'<!-- Wing Blasters -->'
        f'<rect x="1" y="9" width="2" height="5" fill="{NEON_GREEN}"/>'
        f'<rect x="25" y="9" width="2" height="5" fill="{NEON_GREEN}"/>'
        f'<!-- Thrusters (Infinite Loop) -->'
        f'<g class="thrust">'
        f'<polygon points="12,21 14,27 16,21" fill="#ff9900"/>'
        f'<polygon points="13,21 14,25 15,21" fill="#ffff00"/>'
        f'</g>'
        f'<!-- Continuous Dual Blaster Volleys (Infinite Loop) -->'
        f'<g class="flaser">'
        f'<rect x="1" y="-14" width="2" height="12" rx="1" fill="{NEON_GREEN}"/>'
        f'<rect x="25" y="-14" width="2" height="12" rx="1" fill="{NEON_GREEN}"/>'
        f'</g>'
        f'</g>'
    )

def activity(data):
    monthly = data.get("monthly", [])
    cur, lng, best = data["current_streak"], data["longest_streak"], data["best_day"]
    n_days = len(data.get("days", [])) or 365

    stats = [
        ("DEX • STREAK", cur['length'], " d", "BUFF READY" if cur['length'] == 0 else "COMBO ACTIVE", NEON_GREEN, True, 0.45),
        ("VIT • RECORD", lng['length'], " d", f"BEST: {short_date(lng.get('start'))}–{short_date(lng.get('end'))}", ARCADE_GOLD, False, min(1.0, lng['length'] / 30)),
        ("AGI • STAMINA", data['active_days'], " d", f"{data['active_days'] / n_days:.0%} ACTIVE RATE", NEON_CYAN, False, data['active_days'] / n_days),
        ("CRIT • DAMAGE", best['count'], " hits", f"CRIT HIT ({short_date(best.get('date'))})", HEART_RED, False, min(1.0, best['count'] / 30)),
    ]

    stat_parts = []
    card_w = (W - 88 - 3 * 16) / 4
    for i, (lbl, val, sfx, sub, col, is_streak, progress_ratio) in enumerate(stats):
        sx = 44 + i * (card_w + 16)
        delay = 1.2 + i * 0.12
        count_markup = make_count_up(sx + 14, 142, val, sfx, col, delay + 0.2, PIXEL, 26)

        flame_icon = ""
        if is_streak:
            flame_icon = f"""
<g class="r" {d(delay + 0.1)} transform="translate({sx + card_w - 28}, 95)">
  <circle cx="8" cy="8" r="10" fill="#201115" class="gp"/>
  <path class="flame" d="M8 2C8 2 4 6 4 10C4 12.5 6 14.5 8.5 14.5C11 14.5 13 12.5 13 10C13 7.5 10.5 5 10.5 5C10.5 5 9.5 6.5 8 6.5C6.5 6.5 6 5 8 2Z" fill="{HEART_RED}"/>
</g>"""

        bar_fill_w = max(6.0, (card_w - 28) * max(0.08, min(1.0, progress_ratio)))

        stat_parts.append(f"""
<g class="r" {d(delay)}>
  <rect x="{sx}" y="86" width="{card_w}" height="106" rx="8" fill="{ARCADE_CARD}" stroke="{ARCADE_FRAME}"/>
  <text x="{sx + 14}" y="106" font-family="{PIXEL}" font-size="8.5" fill="{MUTED_PIXEL}">{lbl}</text>
  {flame_icon}
  {count_markup}
  <text x="{sx + 14}" y="165" font-family="{MONO}" font-size="10" fill="{MUTED_PIXEL}">{sub}</text>
  <!-- Mini Pixel Gauge -->
  <rect x="{sx + 14}" y="178" width="{card_w - 28}" height="4" rx="2" fill="#1b2431"/>
  <rect class="g" {d(delay + 0.3)} x="{sx + 14}" y="178" width="{bar_fill_w:.1f}" height="4" rx="2" fill="{col}"/>
</g>
""")

    # Space Shooter Commit Valley Arena
    arena_x = 44
    arena_y = 246
    arena_w = W - 88
    arena_h = 168
    peak = max((m["total"] for m in monthly), default=1) or 1
    slot = arena_w / max(len(monthly), 1)

    # 1. Deterministic Twinkling Starfield
    rng = random.Random(42)
    star_elements = []
    for _ in range(36):
        sx = rng.randint(int(arena_x + 8), int(arena_x + arena_w - 8))
        sy = rng.randint(int(arena_y + 8), int(arena_y + arena_h - 12))
        cls = "st1" if rng.random() > 0.5 else "st2"
        rad = 1.0 if rng.random() > 0.3 else 1.5
        scol = "#ffffff" if rng.random() > 0.35 else ("#00e5ff" if rng.random() > 0.5 else "#ffd700")
        star_elements.append(f'<circle cx="{sx}" cy="{sy}" r="{rad}" fill="{scol}" class="{cls}"/>')

    # 2. Monthly Invaders & Commit Valley Laser Cannons (Continuous Infinite Loop)
    shooter_elements = []
    alien_y = arena_y + 30
    launch_y = arena_y + 138

    for i, m in enumerate(monthly):
        cnt = m["total"]
        cx = arena_x + i * slot + slot / 2
        delay = 1.7 + i * 0.04
        is_boss = (cnt == peak)

        # Alien Invader Sprite (with continuous swaying & marching)
        if is_boss:
            alien_markup = make_boss_mothership(cx, alien_y, scale=1.0)
            tag_color = HEART_RED
            tag_txt = f"BOSS:{cnt}"
        elif cnt > 20:
            alien_markup = make_space_invader(cx, alien_y, NEON_CYAN, variant=0, scale=0.9)
            tag_color = NEON_CYAN
            tag_txt = f"{cnt}"
        elif cnt > 0:
            alien_markup = make_space_invader(cx, alien_y, "#a78bfa", variant=1, scale=0.85)
            tag_color = MUTED_PIXEL
            tag_txt = f"{cnt}"
        else:
            alien_markup = make_space_invader(cx, alien_y, "#30363d", variant=2, scale=0.7)
            tag_color = "#30363d"
            tag_txt = "0"

        # Alien HP Tag
        alien_tag = (
            f'<text class="f" {d(delay + 0.2)} x="{cx:.1f}" y="{alien_y - 12}" '
            f'font-family="{PIXEL}" font-size="7.5" text-anchor="middle" fill="{tag_color}">{tag_txt}</text>'
        )

        # Commit Laser Cannon Beam (The Commit Valley - CONSTANT LOOP ANIMATION)
        span = launch_y - (alien_y + 10)
        beam_h = max(8.0, span * (cnt / peak)) if cnt > 0 else 0
        beam_top = launch_y - beam_h

        laser_markup = ""
        if cnt > 0:
            glow_color = NEON_CYAN if is_boss else ("#00ffcc" if cnt > 20 else "#58a6ff")
            core_color = "#ffffff" if is_boss else glow_color
            beam_glow_w = 12 if is_boss else 8
            beam_core_w = 4.5 if is_boss else 3.0
            delay_stream = (i * 0.07) % 0.42
            delay_pulse = (i * 0.14) % 1.3

            # Continuous High-Velocity Tracer Laser Streams & Sparking Explosions
            laser_markup = f"""
<!-- Outer pulsating plasma energy column (Infinite Loop) -->
<rect class="bsurge" style="animation-delay:{delay_pulse:.2f}s" x="{cx - beam_glow_w/2:.1f}" y="{beam_top:.1f}" width="{beam_glow_w}" height="{beam_h:.1f}" rx="2" fill="{glow_color}"/>
<!-- Inner bright ion core (Infinite Loop) -->
<rect class="cpulse" style="animation-delay:{delay_pulse:.2f}s" x="{cx - beam_core_w/2:.1f}" y="{beam_top:.1f}" width="{beam_core_w}" height="{beam_h:.1f}" rx="1.5" fill="{core_color}"/>
<!-- Continuous High-Speed Tracer Laser Stream (Infinite Loop) -->
<line class="stream" style="animation-delay:{delay_stream:.2f}s" x1="{cx:.1f}" y1="{launch_y:.1f}" x2="{cx:.1f}" y2="{beam_top:.1f}" stroke="{core_color}" stroke-width="{beam_core_w * 0.8:.1f}" stroke-linecap="round" stroke-dasharray="6 8"/>
<!-- Impact Sparks & Rotating Plasma Burst at Target (Infinite Loop) -->
<g class="burst" style="animation-delay:{delay_pulse:.2f}s" transform="translate({cx:.1f}, {beam_top:.1f})">
  <circle class="sring" cx="0" cy="0" r="{6 if is_boss else 4}" fill="{glow_color}"/>
  <polygon points="0,-7 2,-2 7,0 2,2 0,7 -2,2 -7,0 -2,-2" fill="#ffffff"/>
</g>
"""

        # Defense Turret Launch Pad
        turret_led = NEON_GREEN if cnt > 0 else "#30363d"
        turret = (
            f'<polygon points="{cx - 5:.1f},{launch_y + 3} {cx:.1f},{launch_y - 2} {cx + 5:.1f},{launch_y + 3}" fill="#1b2431" stroke="#30363d"/>'
            f'<circle cx="{cx:.1f}" cy="{launch_y - 2}" r="1" fill="{turret_led}"/>'
        )

        # Month Sector Tag
        mon = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b").upper()
        mon_color = NEON_CYAN if is_boss else (INK_LIGHT if cnt > 0 else MUTED_PIXEL)
        mon_label = (
            f'<text class="f" {d(2.3)} x="{cx:.1f}" y="{arena_y + arena_h - 8}" '
            f'font-family="{PIXEL}" font-size="8" text-anchor="middle" fill="{mon_color}">{mon}</text>'
        )

        shooter_elements.append(f"""
<g>
  {alien_tag}
  {alien_markup}
  {laser_markup}
  {turret}
  {mon_label}
</g>
""")

    # 3. Patrolling Player Starfighter Ship (Infinite Loop)
    patrolling_ship = f"""
<g class="spatrol" transform="translate({W / 2:.1f}, {launch_y - 2})">
  {make_player_ship(0, 0, scale=0.9)}
</g>
"""

    body = f"""
<rect width="{W}" height="430" rx="12" fill="{ARCADE_BG}" stroke="{ARCADE_FRAME}"/>

<!-- Arcade Header -->
<g class="r" {d(1.0)}>
  <text x="42" y="55" font-family="{PIXEL}" font-size="16" fill="{NEON_GREEN}">★ MISSION // COMMIT VALLEY DEFENSE ★</text>
  <rect class="live" x="{W - 220}" y="44" width="7" height="7" rx="1.5" fill="{HEART_RED}"/>
  <text x="{W - 204}" y="52" font-family="{PIXEL}" font-size="9" fill="{HEART_RED}">COMBO x{data['active_days']} ACTIVE</text>
</g>
<line x1="44" y1="72" x2="{W-44}" y2="72" stroke="{ARCADE_FRAME}"/>

<!-- Stat HUD Boxes -->
{''.join(stat_parts)}

<line x1="44" y1="208" x2="{W-44}" y2="208" stroke="{ARCADE_FRAME}"/>

<!-- Space Shooter Valley Header -->
<g class="f" {d(1.6)}>
  <text x="44" y="228" font-family="{PIXEL}" font-size="8.5" fill="{ARCADE_GOLD}">SPACE DEFENDER // MONTHLY INVASION  •  {data['total_contributions']} TOTAL BLASTS</text>
  <text x="{W - 44}" y="228" text-anchor="end" font-family="{PIXEL}" font-size="8.5" fill="{NEON_CYAN}">SECTOR TARGET: APRIL MOTHERSHIP [{peak} HITS]</text>
</g>

<!-- Space Cockpit Arena -->
<rect x="{arena_x}" y="{arena_y}" width="{arena_w}" height="{arena_h}" rx="8" fill="#050811" stroke="#1d2e47"/>
<!-- Moving Arcade Radar Beam (Infinite Loop) -->
<line class="radar" x1="{arena_x + 2}" y1="{arena_y}" x2="{arena_x + arena_w - 2}" y2="{arena_y}" stroke="{NEON_CYAN}" stroke-width="1.2"/>
<!-- Subtle Grid Lines -->
<line x1="{arena_x}" y1="{alien_y + 12}" x2="{arena_x + arena_w}" y2="{alien_y + 12}" stroke="#132338" stroke-dasharray="3,3"/>
<line x1="{arena_x}" y1="{launch_y + 4}" x2="{arena_x + arena_w}" y2="{launch_y + 4}" stroke="#132338"/>

<!-- Starfield (36 Continuously Twinkling Stars) -->
{''.join(star_elements)}

<!-- Valley Laser Cannons & Alien Invaders (Continuous Looping Battle) -->
{''.join(shooter_elements)}

<!-- Player Mobile Starfighter (Patrolling & Rapid Blaster Fire) -->
{patrolling_ship}
"""
    write("activity.svg", svg(W, 430, body, ["pixel", "mono"],
                             f"Commit Valley Space Shooter for {USERNAME}"))

# ---- 4 · Three Super Mario Power-Up Blocks (BUILD, CRAFT, LEARN) -------------
TILE_W = 880 / 3 - 8
TILE_H = 260

def make_mario_mushroom(x, y, color="#ff2a5f", scale=1.1):
    return f"""<g transform="translate({x:.1f}, {y:.1f}) scale({scale})">
  <!-- Cap -->
  <path d="M5 0h8v2h-8z M2 2h14v3h-14z M0 5h18v4h-18z M2 9h14v2h-14z" fill="{color}"/>
  <!-- Spots -->
  <rect x="3" y="3" width="3" height="4" fill="#ffffff"/>
  <rect x="12" y="3" width="3" height="4" fill="#ffffff"/>
  <rect x="7" y="1" width="4" height="3" fill="#ffffff"/>
  <!-- Stem & Eyes -->
  <path d="M4 11h10v5h-10z" fill="#ffe0b2"/>
  <rect x="6" y="12" width="1.5" height="3" fill="#000000"/>
  <rect x="10.5" y="12" width="1.5" height="3" fill="#000000"/>
</g>"""

def make_mario_star(x, y, scale=1.0):
    return f"""<g transform="translate({x:.1f}, {y:.1f}) scale({scale})">
  <!-- Star -->
  <polygon points="9,0 12,6 18,7 14,12 15,18 9,14 3,18 4,12 0,7 6,6" fill="{ARCADE_GOLD}" stroke="#d35400" stroke-width="0.5"/>
  <!-- Eyes -->
  <rect x="7" y="7" width="1.2" height="3.5" rx="0.5" fill="#000000"/>
  <rect x="9.8" y="7" width="1.2" height="3.5" rx="0.5" fill="#000000"/>
</g>"""

def make_mario_qblock(x, y, scale=1.0):
    return f"""<g class="n" transform="translate({x:.1f}, {y:.1f}) scale({scale})">
  <rect width="20" height="20" rx="2" fill="#d35400"/>
  <rect x="2" y="2" width="16" height="16" fill="#f39c12"/>
  <rect x="3" y="3" width="2" height="2" fill="#ffeaa7"/>
  <rect x="15" y="3" width="2" height="2" fill="#e67e22"/>
  <text x="10" y="14" font-family="{PIXEL}" font-size="11" fill="#ffffff" text-anchor="middle">?</text>
</g>"""

def make_warp_pipe(x, y, scale=1.0):
    return f"""<g transform="translate({x:.1f}, {y:.1f}) scale({scale})">
  <rect x="0" y="0" width="18" height="6" rx="1" fill="#00e55b" stroke="#008037" stroke-width="0.8"/>
  <rect x="2" y="6" width="14" height="9" fill="#00cc44" stroke="#008037" stroke-width="0.8"/>
  <rect x="4" y="6" width="3" height="9" fill="#55ff88"/>
</g>"""

def tile(name, label, item_name, color, fg, num, suffix, caption, delay, index, icon_type="mushroom"):
    try:
        val_clean = re.sub(r"[^\d.]", "", str(num))
        val_target = float(val_clean) if val_clean else 100.0
    except:
        val_target = 100.0

    frames = 14
    count_elems = []
    count_start = delay + 0.4
    for k in range(1, frames + 1):
        p = k / frames
        cur_val = val_target * (1 - (1 - p) ** 3)
        formatted = f"{int(round(cur_val))}" if val_target >= 1 else f"{cur_val:.1f}"
        t_on = count_start + 0.9 * (k - 1) / frames
        t_off = count_start + 0.9 * k / frames
        anim = f'<set attributeName="opacity" to="1" begin="{t_on:.3f}s"/>'
        if k < frames:
            anim += f'<set attributeName="opacity" to="0" begin="{t_off:.3f}s"/>'
        count_elems.append(
            f'<text x="24" y="145" opacity="{1 if STATIC and k == frames else 0}" font-family="{PIXEL}" '
            f'font-size="34" fill="{color}">{formatted}'
            f'<tspan font-size="14" font-family="{PIXEL}" fill="{INK_LIGHT}"> {suffix}</tspan>{anim}</text>'
        )

    defs = f"""<defs>
  <clipPath id="tile-clip-{name}"><rect width="{TILE_W}" height="{TILE_H}" rx="10"/></clipPath>
</defs>"""

    # Choose powerup sprite
    if icon_type == "star":
        powerup_sprite = make_mario_star(TILE_W - 40, 56, scale=1.3)
    elif icon_type == "1up":
        powerup_sprite = make_mario_mushroom(TILE_W - 40, 56, color=NEON_GREEN, scale=1.2)
    else:
        powerup_sprite = make_mario_mushroom(TILE_W - 40, 56, color=HEART_RED, scale=1.2)

    body = f"""
<g clip-path="url(#tile-clip-{name})">
  <rect width="{TILE_W}" height="{TILE_H}" rx="10" fill="{ARCADE_CARD}" stroke="{ARCADE_FRAME}"/>
  <!-- Mario Brick Top Header -->
  <rect x="0" y="0" width="{TILE_W}" height="32" fill="#1b2431"/>
  <line x1="0" y1="32" x2="{TILE_W}" y2="32" stroke="{ARCADE_FRAME}"/>
  
  <g class="ti" {d(delay)}>
    <text x="18" y="21" font-family="{PIXEL}" font-size="8.5" fill="{color}">► {label}</text>
    {make_mario_qblock(TILE_W - 32, 6, scale=0.9)}
    
    <text x="24" y="70" font-family="{PIXEL}" font-size="11" fill="{INK_LIGHT}">[{item_name}]</text>
    {powerup_sprite}
    {''.join(count_elems)}
    <text x="24" y="195" font-family="{SANS}" font-size="13" fill="{MUTED_PIXEL}">{caption[:38]}</text>
    <text x="24" y="218" font-family="{SANS}" font-size="13" fill="{MUTED_PIXEL}">{caption[38:80]}</text>
  </g>
</g>
"""
    write(f"{name}.svg", svg(TILE_W, TILE_H, body, ["pixel", "sans"],
                             f"{label}: {num} {suffix}", left=4 * index, right=8 - 4 * index, bottom=BOTTOM, defs=defs))

# ---- 5 · Featured Projects (Warp Zone Stages) --------------------------------
REPO_W = 880 / 3 - 8
REPO_H = 175

PROJECTS = [
    {
        "id": "pandale",
        "stage": "WORLD 1-1 // OVERWORLD",
        "name": "PANDALE",
        "desc": "Interactive event discovery and cultural festival navigation platform.",
        "tag": "PIPE 1 • TS ARCADE",
        "color": NEON_GREEN,
        "url": "https://github.com/JoyTheSloth/pandale"
    },
    {
        "id": "mabbele-studios",
        "stage": "WORLD 1-2 // COIN VAULT",
        "name": "MABBELE STUDIOS",
        "desc": "Creative digital production studio delivering high-craft web experiences.",
        "tag": "PIPE 2 • LIVE RUN",
        "color": ARCADE_GOLD,
        "url": "https://mabbele-studios.vercel.app"
    },
    {
        "id": "job-dalal",
        "stage": "WORLD 8-4 // BOWSER CASTLE",
        "name": "JOB DALAL",
        "desc": "Modern recruitment portal and smart job discovery platform.",
        "tag": "STAGE CLEAR • NEXTJS",
        "color": HEART_RED,
        "url": "https://github.com/JoyTheSloth/job-dalal"
    },
]

def wrap_desc(text, max_chars=34):
    words = text.split()
    lines = []
    cur = []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + (1 if cur else 0) <= max_chars:
            cur.append(w)
            cur_len += len(w) + (1 if len(cur) > 1 else 0)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
    if cur:
        lines.append(" ".join(cur))
    return lines[:2]

def repo_card(i, proj):
    delay = 3.2 + i * 0.15
    name = proj["name"]
    stage = proj["stage"]
    desc = proj["desc"]
    tag = proj["tag"]
    color = proj["color"]
    file_id = proj["id"]

    lines = wrap_desc(desc, 34)
    line1 = lines[0] if len(lines) > 0 else ""
    line2 = lines[1] if len(lines) > 1 else ""

    body = f"""
<rect width="{REPO_W}" height="{REPO_H}" rx="10" fill="{ARCADE_CARD}" stroke="{ARCADE_FRAME}"/>
<!-- Warp Zone Header -->
<rect x="0" y="0" width="{REPO_W}" height="26" fill="#18202c"/>
<text x="14" y="17" font-family="{PIXEL}" font-size="8" fill="{color}">{stage}</text>
{make_warp_pipe(REPO_W - 28, 5, scale=0.85)}

<g class="r" {d(delay)}>
  <text x="16" y="52" font-family="{PIXEL}" font-size="12" fill="{INK_LIGHT}">{escape(name)}</text>
  <text x="16" y="86" font-family="{SANS}" font-size="13" fill="{MUTED_PIXEL}">{escape(line1)}</text>
  <text x="16" y="108" font-family="{SANS}" font-size="13" fill="{MUTED_PIXEL}">{escape(line2)}</text>
  
  <text x="16" y="{REPO_H - 18}" font-family="{PIXEL}" font-size="8" fill="{color}">► {escape(tag)}</text>
  <text class="n" x="{REPO_W - 24}" y="{REPO_H - 18}" text-anchor="end" font-family="{PIXEL}" font-size="9" fill="{color}">WARP ►</text>
</g>
"""
    write(f"repo-{file_id}.svg", svg(REPO_W, REPO_H, body, ["pixel", "sans"],
                                    f"{name}: {desc}", left=4 * i, right=8 - 4 * i, bottom=BOTTOM))

# ---- 6 · Section Title (Super Mario Warp Zone) --------------------------------
def section_title(text, italic, theme):
    fg = NEON_GREEN if theme == "dark" else INK_LIGHT
    body = (
        f'<text class="r" {d(3.0)} x="2" y="38" font-family="{PIXEL}" font-size="13.5" fill="{fg}">★ {escape(text)} '
        f'<tspan fill="{ARCADE_GOLD}">[{escape(italic).upper()}]</tspan> ★</text>'
    )
    write(f"title-coding-{theme}.svg", svg(W, 54, body, ["pixel"], f"{text} {italic}", bottom=6))

# ---- Main Execution ----------------------------------------------------------
if __name__ == "__main__":
    data = {}
    if os.path.exists(DATA):
        try:
            data = json.load(open(DATA, encoding="utf-8"))
        except Exception as e:
            print("Notice loading DATA:", e)

    total_contrib = data.get("total_contributions", 368)
    active_days = data.get("active_days", 84)

    hero(data)
    heatmap(data)
    activity(data)

    tile("build", "WORLD 1-1 // ? BLOCK", "SUPER MUSHROOM", HEART_RED, "#ffffff", "60+", "APPS",
         "Full-stack apps, interactive engines, UI kits, and creative experiments.", 2.5, 0, icon_type="mushroom")
    tile("brand", "WORLD 1-2 // STAR POWER", "SUPER STAR", ARCADE_GOLD, "#ffffff", f"{active_days}", "DAYS",
         "Precision CSS, interactive micro-animations, and TypeScript architectures.", 2.7, 1, icon_type="star")
    tile("learn", "WORLD 1-3 // 1-UP VAULT", "1-UP MUSHROOM", NEON_GREEN, INK_LIGHT, f"{total_contrib}", "COMMITS",
         "Daily curiosity exploring modern frontend paradigms and open source leveling.", 2.9, 2, icon_type="1up")

    section_title("WELCOME TO WARP ZONE", "select stage", "dark")
    section_title("WELCOME TO WARP ZONE", "select stage", "light")

    for i, proj in enumerate(PROJECTS):
        repo_card(i, proj)

    print("All Super Mario Arcade cards rendered successfully into cards/!")
