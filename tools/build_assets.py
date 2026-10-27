#!/usr/bin/env python3
"""Generate the self-contained SVG assets used by the profile README.

Everything is vector, dependency-free at view time, and renders identically on
every OS: the wordmark, the numbers and all Japanese text are converted to
paths at build time, so viewers don't need any particular font installed.

    pip install fonttools
    python3 tools/build_assets.py
"""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

FONT_DISPLAY = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
FONT_JP = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"

# ---- palette -------------------------------------------------------------
INK = "#07070d"
INK2 = "#100a1d"
PANEL = "#0e0b19"
LINE = "#221c36"
AKANE = "#ff2a55"      # 茜 — madder crimson, pushed to neon
AKANE_DEEP = "#9f1232"
CYAN = "#28e6ff"
AMBER = "#ffb547"
MINT = "#5cf2b0"
TEXT = "#f4f2f8"
MUTED = "#8f8ba3"
DIM = "#5d5975"

SANS = "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


class Face:
    def __init__(self, path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]

    def _names(self, text):
        return [self.cmap.get(ord(c), ".notdef") for c in text]

    def width(self, text, size, tracking=0):
        s = size / self.upm
        names = self._names(text)
        return sum(self.hmtx[n][0] * s for n in names) + tracking * (len(names) - 1)

    def path(self, text, size, x, y, tracking=0, align="left"):
        """Return SVG path data for `text` with its baseline at (x, y)."""
        s = size / self.upm
        w = self.width(text, size, tracking)
        if align == "center":
            x -= w / 2
        elif align == "right":
            x -= w
        parts = []
        cx = x
        for name in self._names(text):
            pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.1f}")
            self.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            cmds = pen.getCommands()
            if cmds:
                parts.append(cmds)
            cx += self.hmtx[name][0] * s + tracking
        return " ".join(parts), w


display = Face(FONT_DISPLAY)
mono = Face(FONT_MONO)
jp = Face(FONT_JP)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write(name, svg):
    (OUT / name).write_text(svg.strip() + "\n", encoding="utf-8")
    print(f"wrote assets/{name} ({len(svg) // 1024} KB)")


def grid_defs(pid="grid", step=40):
    return f'''
    <pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">
      <path d="M {step} 0 L 0 0 0 {step}" fill="none" stroke="{LINE}" stroke-width="1"/>
    </pattern>'''


# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
def hero():
    W, H = 1200, 440
    word, word_w = display.path("AKANE", 150, 72, 262, tracking=-7)
    kanji, _ = jp.path("茜", 262, 925, 326, align="center")
    tagline, tag_w = jp.path("速く、でも丁寧に", 19, 96, 403)
    typed = "$ ship fast. stay precise. read the logs."
    typed_w = mono.width(typed, 19)

    # synthwave slices across the lower half of the sun
    slices = "".join(
        f'<rect x="700" y="{y}" width="450" height="{h}" fill="{INK}" opacity="0.92"/>'
        for y, h in [(238, 5), (258, 7), (282, 9), (310, 12), (344, 15)]
    )

    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Akane — backend, infra, devtools, reliability">
  <title>Akane // 茜</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{INK}"/>
      <stop offset="1" stop-color="{INK2}"/>
    </linearGradient>
    <radialGradient id="sun" cx="0.5" cy="0.45" r="0.6">
      <stop offset="0" stop-color="#ff6b8a"/>
      <stop offset="0.55" stop-color="{AKANE}"/>
      <stop offset="1" stop-color="{AKANE_DEEP}"/>
    </radialGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{AKANE}" stop-opacity="0"/>
      <stop offset="0.2" stop-color="{AKANE}"/>
      <stop offset="0.8" stop-color="{CYAN}"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.05"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="28"/>
    </filter>
    <filter id="softglow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    {grid_defs()}
    <clipPath id="sliceA"><rect x="60" y="150" width="620" height="22"/></clipPath>
    <clipPath id="sliceB"><rect x="60" y="205" width="620" height="16"/></clipPath>
    <clipPath id="typeclip">
      <rect x="96" y="340" width="{typed_w + 4:.0f}" height="34">
        <animate attributeName="width" values="0;0;{typed_w + 4:.0f};{typed_w + 4:.0f}" keyTimes="0;0.08;0.6;1" dur="7s" begin="0s" repeatCount="indefinite" calcMode="linear"/>
      </rect>
    </clipPath>
  </defs>

  <!-- background -->
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)" opacity="0.55"/>
  <rect x="0" y="0" width="{W}" height="{H}" fill="none" stroke="{LINE}" stroke-width="2"/>

  <!-- the sun -->
  <circle cx="925" cy="225" r="185" fill="{AKANE}" opacity="0.35" filter="url(#glow)">
    <animate attributeName="opacity" values="0.3;0.5;0.3" dur="6s" repeatCount="indefinite"/>
  </circle>
  <circle cx="925" cy="225" r="168" fill="url(#sun)">
    <animate attributeName="r" values="166;171;166" dur="6s" repeatCount="indefinite"/>
  </circle>
  {slices}
  <!-- 茜 cut into the sun like a seal -->
  <path d="{kanji}" fill="{INK}" opacity="0.88"/>
  <path d="{kanji}" fill="none" stroke="#ffd0da" stroke-width="1" opacity="0.5"/>

  <!-- wordmark with chromatic glitch slices -->
  <path d="{word}" fill="{CYAN}" clip-path="url(#sliceA)" opacity="0">
    <animate attributeName="opacity" values="0;0;0.9;0;0;0;0;0.7;0;0" keyTimes="0;0.30;0.32;0.34;0.5;0.72;0.74;0.76;0.78;1" dur="5s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="-6 0;-6 0;8 0;-6 0" keyTimes="0;0.3;0.74;1" dur="5s" repeatCount="indefinite"/>
  </path>
  <path d="{word}" fill="{AKANE}" clip-path="url(#sliceB)" opacity="0">
    <animate attributeName="opacity" values="0;0;0.9;0;0;0.8;0;0" keyTimes="0;0.31;0.33;0.35;0.73;0.75;0.77;1" dur="5s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="7 0;7 0;-9 0;7 0" keyTimes="0;0.31;0.75;1" dur="5s" repeatCount="indefinite"/>
  </path>
  <path d="{word}" fill="{TEXT}"/>

  <!-- subtitle -->
  <text x="78" y="305" font-family="{SANS}" font-size="24" font-weight="600" fill="#c9c5d8" letter-spacing="0.5">
    Backend <tspan fill="{AKANE}">·</tspan> Infra <tspan fill="{AKANE}">·</tspan> Devtools <tspan fill="{AKANE}">·</tspan> Reliability
  </text>

  <!-- typed line -->
  <g clip-path="url(#typeclip)">
    <text x="96" y="364" font-family="{MONO}" font-size="19" font-weight="700" fill="{MINT}">{typed}</text>
  </g>
  <rect x="{96 + typed_w + 6:.0f}" y="346" width="10" height="22" fill="{MINT}">
    <animate attributeName="x" values="96;96;{96 + typed_w + 6:.0f};{96 + typed_w + 6:.0f}" keyTimes="0;0.08;0.6;1" dur="7s" repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="opacity" values="1;0;1" dur="0.9s" repeatCount="indefinite"/>
  </rect>
  <rect x="78" y="340" width="4" height="34" fill="{AKANE}"/>

  <!-- japanese tagline -->
  <rect x="78" y="391" width="8" height="8" fill="{AKANE}"/>
  <path d="{tagline}" fill="{MUTED}"/>
  <text x="{96 + tag_w + 12:.0f}" y="403" font-family="{MONO}" font-size="13" fill="{DIM}">// fast, but precise</text>

  <!-- HUD corners -->
  <g font-family="{MONO}" font-size="12" font-weight="700" fill="{DIM}" letter-spacing="1.5">
    <text x="78" y="52">PROFILE.v3 — AKANE // 茜</text>
    <text x="{W - 78}" y="52" text-anchor="end">20 Y/O · JAPAN · UTC+9</text>
    <text x="{W - 100}" y="{H - 36}" text-anchor="end" fill="{MUTED}">STATUS: BUILDING</text>
  </g>
  <circle cx="{W - 86}" cy="{H - 40}" r="4" fill="{MINT}" filter="url(#softglow)">
    <animate attributeName="opacity" values="1;0.2;1" dur="1.6s" repeatCount="indefinite"/>
  </circle>
  <rect x="78" y="63" width="180" height="2" fill="url(#rule)"/>
  <rect x="{W - 258}" y="63" width="180" height="2" fill="url(#rule)"/>

  <!-- scanline sweep -->
  <rect x="0" y="-120" width="{W}" height="120" fill="url(#scan)">
    <animateTransform attributeName="transform" type="translate" from="0 0" to="0 {H + 240}" dur="8s" repeatCount="indefinite"/>
  </rect>

  <!-- bottom rule -->
  <rect x="0" y="{H - 3}" width="{W}" height="3" fill="url(#rule)"/>
</svg>'''


# ---------------------------------------------------------------------------
# STACK
# ---------------------------------------------------------------------------
def chip_row(label, items, y, color):
    out = [f'<text x="40" y="{y + 25}" font-family="{MONO}" font-size="12" font-weight="700" fill="{color}" letter-spacing="2">{label}</text>']
    x = 160
    for item in items:
        w = mono.width(item, 16) + 32
        out.append(
            f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="40" rx="8" fill="{PANEL}" stroke="{LINE}"/>'
            f'<rect x="{x:.0f}" y="{y + 11}" width="3" height="18" fill="{color}"/>'
            f'<text x="{x + 18:.0f}" y="{y + 26}" font-family="{MONO}" font-size="16" font-weight="700" fill="{TEXT}">{esc(item)}</text>'
        )
        x += w + 12
    return "\n".join(out)


def stack():
    W, H = 1200, 196
    rows = [
        ("LANG", ["Go", "TypeScript", "JavaScript", "SQL", "Ruby"], AKANE),
        ("RUNTIME", ["Node.js", "Bun", "Docker", "GitHub Actions"], CYAN),
        ("STYLE", ["small PRs", "clear contracts", "strict CI", "ship → measure → improve"], AMBER),
    ]
    body = "\n".join(chip_row(l, i, 22 + k * 56, c) for k, (l, i, c) in enumerate(rows))
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack">
  <defs>{grid_defs("g2")}</defs>
  <rect width="{W}" height="{H}" rx="18" fill="{INK}"/>
  <rect width="{W}" height="{H}" rx="18" fill="url(#g2)" opacity="0.5"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="{LINE}" stroke-width="2"/>
  {body}
</svg>'''


# ---------------------------------------------------------------------------
# PROJECT CARDS
# ---------------------------------------------------------------------------
def card(name, index, title, subtitle, bullets, color, href_label):
    W, H = 580, 232
    subtitle, href_label = esc(subtitle), esc(href_label)
    bullets = [esc(b) for b in bullets]
    t, _ = display.path(title, 40, 32, 72, tracking=-1)
    idx, _ = display.path(index, 150, W - 24, H - 20, align="right")
    lines = "\n".join(
        f'<text x="32" y="{132 + i * 23}" font-family="{MONO}" font-size="15" fill="#c9c5d8"><tspan fill="{color}">▸</tspan> {b}</text>'
        for i, b in enumerate(bullets)
    )
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{color}"/>
      <stop offset="1" stop-color="{color}" stop-opacity="0.1"/>
    </linearGradient>
    <filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
    {grid_defs("gc", 32)}
  </defs>
  <rect width="{W}" height="{H}" rx="18" fill="{INK}"/>
  <rect width="{W}" height="{H}" rx="18" fill="url(#gc)" opacity="0.45"/>
  <circle cx="{W - 60}" cy="40" r="90" fill="{color}" opacity="0.16" filter="url(#g)"/>
  <path d="{idx}" fill="{color}" opacity="0.10"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="{LINE}" stroke-width="2"/>
  <rect x="0" y="40" width="4" height="{H - 80}" fill="url(#edge)"/>
  <path d="{t}" fill="{TEXT}"/>
  <text x="32" y="100" font-family="{SANS}" font-size="15" font-weight="600" fill="{MUTED}">{subtitle}</text>
  {lines}
  <text x="32" y="{H - 16}" font-family="{MONO}" font-size="11" font-weight="700" fill="{color}" letter-spacing="1.5">{href_label}</text>
</svg>'''


# ---------------------------------------------------------------------------
# STATS
# ---------------------------------------------------------------------------
def stats():
    W, H = 1200, 270
    tiles = [
        ("127", "MERGED PRS", AKANE),
        ("1,224", "CONTRIBUTIONS / YR", CYAN),
        ("514", "PR REVIEWS / YR", AMBER),
        ("409", "ISSUES OPENED / YR", MINT),
    ]
    x0, tw, gap = 40, 268, 16
    body = []
    for i, (num, label, color) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        n, _ = display.path(num, 58, x + 24, 108, tracking=-2)
        body.append(f'''
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 12;0 0" dur="0.6s" begin="{0.15 * i:.2f}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
    <rect x="{x}" y="30" width="{tw}" height="128" rx="14" fill="{PANEL}" stroke="{LINE}"/>
    <rect x="{x + 24}" y="46" width="34" height="3" fill="{color}"/>
    <path d="{n}" fill="{TEXT}"/>
    <text x="{x + 24}" y="138" font-family="{MONO}" font-size="12" font-weight="700" fill="{MUTED}" letter-spacing="1.5">{label}</text>
  </g>''')
    bar_x, bar_w = 40, W - 80
    ts = 0.986
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub snapshot">
  <defs>{grid_defs("g3")}
    <linearGradient id="ts" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AKANE}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
  </defs>
  <rect width="{W}" height="{H}" rx="18" fill="{INK}"/>
  <rect width="{W}" height="{H}" rx="18" fill="url(#g3)" opacity="0.5"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="{LINE}" stroke-width="2"/>
  {"".join(body)}
  <text x="{bar_x}" y="200" font-family="{MONO}" font-size="12" font-weight="700" fill="{MUTED}" letter-spacing="1.5">LANGUAGES · OWNED REPOS</text>
  <text x="{W - 40}" y="200" text-anchor="end" font-family="{MONO}" font-size="12" font-weight="700" fill="{DIM}" letter-spacing="1.5">SNAPSHOT 2026-02-27 UTC · NO EXTERNAL WIDGETS</text>
  <rect x="{bar_x}" y="214" width="{bar_w}" height="14" rx="7" fill="{PANEL}" stroke="{LINE}"/>
  <rect x="{bar_x}" y="214" width="{bar_w * ts:.0f}" height="14" rx="7" fill="url(#ts)">
    <animate attributeName="width" from="0" to="{bar_w * ts:.0f}" dur="1.4s" begin="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
  </rect>
  <text x="{bar_x}" y="250" font-family="{MONO}" font-size="13" font-weight="700" fill="{TEXT}">TypeScript <tspan fill="{AKANE}">98.6%</tspan></text>
  <text x="{W - 40}" y="250" text-anchor="end" font-family="{MONO}" font-size="13" font-weight="700" fill="{MUTED}">JavaScript <tspan fill="{CYAN}">1.4%</tspan></text>
</svg>'''


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
def footer():
    W, H = 1200, 150
    yoro, yw = jp.path("よろしくお願いします", 40, W / 2, 72, tracking=2, align="center")
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="よろしくお願いします — see you in the logs">
  <defs>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{AKANE}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{AKANE}"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </linearGradient>
    <filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
    {grid_defs("g4")}
  </defs>
  <rect width="{W}" height="{H}" rx="18" fill="{INK}"/>
  <rect width="{W}" height="{H}" rx="18" fill="url(#g4)" opacity="0.5"/>
  <ellipse cx="{W / 2}" cy="{H}" rx="360" ry="80" fill="{AKANE}" opacity="0.22" filter="url(#g)"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="{LINE}" stroke-width="2"/>
  <path d="{yoro}" fill="{TEXT}"/>
  <rect x="{W / 2 - 220}" y="91" width="440" height="2" fill="url(#rule)">
    <animate attributeName="width" from="0" to="440" dur="1.6s" begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
  </rect>
  <text x="{W / 2}" y="122" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" fill="{MUTED}" letter-spacing="2">SEE YOU IN THE LOGS <tspan fill="{AKANE}">✦</tspan> AKANE // 茜</text>
</svg>'''


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    write("hero.svg", hero())
    write("stack.svg", stack())
    write("stats.svg", stats())
    write("footer.svg", footer())
    write("card-carrier.svg", card(
        "carrier", "01", "carrier", "Cross-platform runtime & workflow tooling",
        ["PR review operations", "CI / workflow quality gates", "release-flow + docs maintenance"],
        AKANE, "GITHUB.COM/KEITH-CY/CARRIER ↗"))
    write("card-fiber-link.svg", card(
        "fiber-link", "02", "fiber-link", "CKB Fiber tipping & payments stack",
        ["milestone closeout reviews", "workflow hardening + smoke validation", "runbooks + acceptance evidence"],
        CYAN, "GITHUB.COM/KEITH-CY/FIBER-LINK ↗"))
    write("card-war.svg", card(
        "war", "03", "war.md", "Replayable coding-battle & eval arena",
        ["deterministic, replayable runs", "text-first agent battles", "practical tooling experiments"],
        AMBER, "WAR.MD ↗"))
    write("card-now.svg", card(
        "now", "04", "now()", "What I'm shipping this quarter",
        ["reliability hardening for runtime systems", "faster PR / review loops via automation", "docs an operator can use at 3 AM"],
        MINT, "STATUS: BUILDING ●"))
