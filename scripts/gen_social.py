"""Regenerate og.png and apple-touch-icon.png for the Dash Fusion landing page.

Run from the repo root:  python scripts/gen_social.py

Both images reuse the landing page's motif: the "List ___" wordmark where the
blank is the highlighted row lifted from the app icons.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "icons"

PAPER = "#FBFBFD"
INK = "#14151C"
MUTED = "#5F6270"
BRAND = "#3F51B5"

BOLD = "C:/Windows/Fonts/segoeuib.ttf"
REGULAR = "C:/Windows/Fonts/segoeui.ttf"

# Shipping order, matching the page.
APPS = [
    "counter", "score", "timer", "budget", "debt",
    "calculator", "percent", "date", "notes", "picker",
]


def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def build_og(path):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    head = ImageFont.truetype(BOLD, 108)
    sub = ImageFont.truetype(REGULAR, 31)
    tag = ImageFont.truetype(REGULAR, 24)

    left, top = 86, 150

    # "List" + the highlighted pill holding "anything".
    word = "List"
    d.text((left, top), word, font=head, fill=INK)
    wl = d.textlength(word, font=head)

    pill_text = "anything"
    pad_x, gap = 34, 26
    tw = d.textlength(pill_text, font=head)
    asc, desc = head.getmetrics()
    line_h = asc + desc
    px0 = left + wl + gap
    py0 = top - 10
    px1 = px0 + tw + pad_x * 2
    py1 = py0 + line_h + 20
    rounded(d, (px0, py0, px1, py1), radius=(py1 - py0) // 2, fill=BRAND)
    d.text((px0 + pad_x, top), pill_text, font=head, fill="#FFFFFF")

    d.text(
        (left, py1 + 46),
        "Ten Android utilities that each do one thing.",
        font=sub,
        fill=INK,
    )
    d.text(
        (left, py1 + 92),
        "Offline. No accounts. No tracking.",
        font=sub,
        fill=MUTED,
    )

    # The family, as a row of its own icons.
    size, gap_i = 74, 22
    x, y = left, H - 74 - size
    for name in APPS:
        f = ICONS / f"list-{name}.png"
        if not f.exists():
            continue
        ic = Image.open(f).convert("RGBA").resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, size - 1, size - 1), radius=int(size * 0.235), fill=255
        )
        img.paste(ic, (x, y), mask)
        x += size + gap_i

    d.text((left, H - 52), "dash-fusion.github.io", font=tag, fill=MUTED)

    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


def build_touch_icon(path, size=180):
    """The favicon motif: three rows, the middle one picked."""
    s = size * 4  # supersample, then downscale for clean edges
    img = Image.new("RGB", (s, s), BRAND)
    d = ImageDraw.Draw(img)
    u = s / 64.0

    faint = (255, 255, 255)
    top = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    dt = ImageDraw.Draw(top)
    dt.rounded_rectangle((15 * u, 17 * u, 49 * u, 26 * u), radius=4.5 * u,
                         fill=faint + (115,))
    dt.rounded_rectangle((15 * u, 43 * u, 49 * u, 52 * u), radius=4.5 * u,
                         fill=faint + (115,))
    img.paste(Image.alpha_composite(img.convert("RGBA"), top).convert("RGB"))

    d.rounded_rectangle((11 * u, 29.5 * u, 53 * u, 39.5 * u), radius=5 * u,
                        fill="#FFFFFF")
    d.ellipse((15 * u, 31.5 * u, 21 * u, 37.5 * u), fill=BRAND)

    img = img.resize((size, size), Image.LANCZOS)
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build_og(ROOT / "og.png")
    build_touch_icon(ROOT / "apple-touch-icon.png")
