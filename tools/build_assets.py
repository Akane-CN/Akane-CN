#!/usr/bin/env python3
"""Build the SVG assets for the profile README.

Everything is vector except the portrait, which is embedded into hero.svg as
base64 so the SVG works inside GitHub's <img> sandbox (external hrefs don't
load there). Display type is converted to paths at build time so it renders
identically on every OS.

    pip install fonttools pillow
    python3 tools/build_assets.py
"""
import base64
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
PHOTO = OUT / "akane.jpg"

FONT_SERIF = "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf"
FONT_SERIF_I = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"
FONT_SANS_L = "/usr/share/fonts/opentype/inter/InterDisplay-Light.otf"
FONT_JP = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"

# palette, sampled from the portrait
GREY = "#aaadb7"       # photo background
GREY_D = "#9a9da8"
PAPER = "#eceef1"
INK = "#15161a"
MUTE = "#5c5f6a"
GOLD = "#c9a24a"
WHITE = "#f6f6f8"

MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


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
        s = size / self.upm
        w = self.width(text, size, tracking)
        if align == "center":
            x -= w / 2
        elif align == "right":
            x -= w
        parts, cx = [], x
        for name in self._names(text):
            pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.1f}")
            self.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            if pen.getCommands():
                parts.append(pen.getCommands())
            cx += self.hmtx[name][0] * s + tracking
        return " ".join(parts), w


serif, serif_i, sans_l, jp = Face(FONT_SERIF), Face(FONT_SERIF_I), Face(FONT_SANS_L), Face(FONT_JP)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def P(face, text, size, x, y, fill, align="left", tracking=0, extra=""):
    d, _ = face.path(text, size, x, y, tracking=tracking, align=align)
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def V(face, text, size, x, y, fill, gap=1.12):
    """Vertical Japanese: one glyph per line, centred on x."""
    out = []
    for i, ch in enumerate(text):
        if ch in "ー—":
            out.append(f'<g transform="translate({x},{y + i * size * gap - size * 0.38}) rotate(90)">'
                       f'<path d="{face.path(ch, size, 0, size * 0.38, align="center")[0]}" fill="{fill}"/></g>')
        elif ch in "、。":
            out.append(P(face, ch, size, x + size * 0.55, y + i * size * gap - size * 0.55, fill, "center"))
        else:
            out.append(P(face, ch, size, x, y + i * size * gap, fill, "center"))
    return "".join(out)


def T(text, size, x, y, fill, align="start", fam=MONO, weight=700, ls=0, extra=""):
    return (f'<text x="{x}" y="{y}" text-anchor="{align}" font-family="{fam}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" letter-spacing="{ls}" {extra}>{esc(text)}</text>')


NOISE = ('<filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" '
         'stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>')


def grain(W, H, op, x=0, y=0):
    return f'<rect x="{x}" y="{y}" width="{W}" height="{H}" filter="url(#noise)" opacity="{op}" style="mix-blend-mode:overlay"/>'


def write(name, svg):
    (OUT / name).write_text(svg.strip() + "\n", encoding="utf-8")
    print(f"wrote assets/{name} ({len(svg) // 1024} KB)")


# --------------------------------------------------------------------------- hero
def hero():
    W, H = 1200, 660
    photo = base64.b64encode(PHOTO.read_bytes()).decode()
    pw = 520  # photo column
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Akane — software engineer, Japan">
  <title>Akane / 茜</title>
  <defs>
    {NOISE}
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{GREY}" stop-opacity="0"/>
      <stop offset="1" stop-color="{GREY}" stop-opacity="1"/>
    </linearGradient>
    <linearGradient id="fadeV" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0.75" stop-color="{GREY}" stop-opacity="0"/>
      <stop offset="1" stop-color="{GREY}" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{GOLD}" stop-opacity="0"/>
      <stop offset="0.15" stop-color="{GOLD}"/>
      <stop offset="1" stop-color="{GOLD}" stop-opacity="0.2"/>
    </linearGradient>
    <clipPath id="photo"><rect x="0" y="0" width="{pw + 160}" height="{H}"/></clipPath>
  </defs>

  <rect width="{W}" height="{H}" fill="{GREY}"/>

  <!-- portrait -->
  <g clip-path="url(#photo)">
    <image xlink:href="data:image/jpeg;base64,{photo}" x="-20" y="-40" width="{pw + 180}" height="{(pw + 180) * 1.3333:.0f}" preserveAspectRatio="xMidYMin slice"/>
    <rect x="{pw - 40}" y="0" width="200" height="{H}" fill="url(#fade)"/>
    <rect x="0" y="0" width="{pw + 160}" height="{H}" fill="url(#fadeV)"/>
  </g>

  <!-- top meta -->
  {T("AKANE  —  PROFILE", 11, 600, 62, INK, ls=3)}
  {T("VOL. 20  ·  2026", 11, W - 60, 62, INK, "end", ls=3)}
  <rect x="600" y="76" width="{W - 660}" height="1" fill="{INK}" opacity="0.5"/>

  <!-- name -->
  {P(serif, "Akane", 168, 592, 300, INK, tracking=-5)}
  {P(serif_i, "builds the quiet parts of software.", 34, 600, 352, INK, tracking=-0.3)}
  <rect x="600" y="384" width="440" height="1.5" fill="url(#gold)"/>
  {T("SOFTWARE ENGINEER  ·  JAPAN  ·  UTC+9", 12, 600, 418, INK, ls=2.5)}
  {T("20 Y/O  ·  2006 → NOW  ·  BACKEND, INFRA, TOOLS", 12, 600, 442, MUTE, ls=2.5)}

  <!-- vertical title -->
  {V(jp, "速く、でも丁寧に。", 44, 1128, 140, INK, 1.1)}
  {V(jp, "二十歳のソフトウェアエンジニア", 15, 1082, 128, MUTE, 1.18)}

  <!-- seal -->
  <g transform="translate(1000,560)">
    <circle r="30" fill="none" stroke="{GOLD}" stroke-width="1.5"/>
    <circle r="24" fill="none" stroke="{GOLD}" stroke-width="0.6"/>
    {P(jp, "茜", 28, 0, 10, GOLD, "center")}
  </g>
  {T("AVAILABLE", 11, 616, 598, INK, ls=3)}
  <circle cx="603" cy="594" r="3.5" fill="{GOLD}"><animate attributeName="opacity" values="1;0.25;1" dur="2.4s" repeatCount="indefinite"/></circle>
  {T("github.com/Akane-CN", 11, 716, 598, MUTE, ls=1)}

  {grain(W, H, 0.10)}
</svg>'''


# --------------------------------------------------------------------------- works
def works():
    W, H = 1200, 330
    rows = [
        ("01", "Runtime & workflow tooling", "Go · TypeScript · CI", "2025 —"),
        ("02", "Payments on CKB Fiber", "TypeScript · payment channels", "2025"),
        ("03", "Replayable battle arena", "Web · deterministic runs", "2026"),
    ]
    body = []
    for i, (n, t, s, yr) in enumerate(rows):
        y = 96 + i * 78
        body.append(f'<rect x="60" y="{y + 26}" width="{W - 120}" height="1" fill="{INK}" opacity="0.12"/>')
        body.append(T(n, 11, 60, y, MUTE, ls=3))
        body.append(P(serif, t, 32, 120, y + 8, INK, tracking=-0.5))
        body.append(T(s, 11, 720, y, MUTE, ls=1.5))
        body.append(T(yr, 11, 1000, y, MUTE, ls=1.5))
        body.append(P(sans_l, "↗", 30, W - 60, y + 6, GOLD, "right"))
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Selected work">
  <defs>{NOISE}</defs>
  <rect width="{W}" height="{H}" fill="{PAPER}"/>
  {T("SELECTED WORK", 11, 60, 48, INK, ls=3)}
  {T("( 03 )", 11, W - 60, 48, MUTE, "end", ls=3)}
  <rect x="60" y="60" width="{W - 120}" height="1" fill="{INK}" opacity="0.5"/>
  {"".join(body)}
  {grain(W, H, 0.08)}
</svg>'''


# --------------------------------------------------------------------------- numbers
def numbers():
    W, H = 1200, 220
    tiles = [("1,224", "CONTRIBUTIONS / 12 MO"), ("514", "PR REVIEWS / 12 MO"), ("409", "ISSUES OPENED / 12 MO"), ("127", "PULL REQUESTS MERGED")]
    body = []
    for i, (n, l) in enumerate(tiles):
        x = 60 + i * 275
        body.append(f'<rect x="{x}" y="60" width="28" height="1.5" fill="{GOLD}"/>')
        body.append(P(serif, n, 64, x, 132, INK, tracking=-2))
        body.append(T(l, 10, x, 164, MUTE, ls=2.5))
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub numbers">
  <defs>{NOISE}</defs>
  <rect width="{W}" height="{H}" fill="{PAPER}"/>
  {"".join(body)}
  {T("HAND-KEPT SNAPSHOT · 2026-02-27 UTC · NO THIRD-PARTY WIDGETS", 10, W - 60, 196, MUTE, "end", ls=2)}
  {grain(W, H, 0.08)}
</svg>'''


# --------------------------------------------------------------------------- footer
def footer():
    W, H = 1200, 170
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="よろしくお願いします">
  <defs>{NOISE}
    <linearGradient id="g2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GOLD}" stop-opacity="0"/><stop offset="0.5" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="{GREY}"/>
  {P(jp, "よろしくお願いします", 30, W / 2, 78, INK, "center", tracking=3)}
  <rect x="{W / 2 - 160}" y="98" width="320" height="1.5" fill="url(#g2)">
    <animate attributeName="width" values="0;320" dur="1.6s" begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
    <animate attributeName="x" values="{W / 2};{W / 2 - 160}" dur="1.6s" begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
  </rect>
  {T("AKANE  ·  茜  ·  FAST, BUT PRECISE", 11, W / 2, 128, INK, "middle", ls=3)}
  {grain(W, H, 0.10)}
</svg>'''


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    write("hero.svg", hero())
    write("works.svg", works())
    write("numbers.svg", numbers())
    write("footer.svg", footer())
