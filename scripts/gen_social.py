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
    "calculator", "percent", "date", "notes", "picker", "qr", "habit", "subs", "grocery",
    "todo", "invoice", "water", "countdown", "weight", "pack", "fast", "split", "savings", "meds", "baby", "recipe", "voice", "flashcards", "convert",
    "journal", "birthday", "car", "chores", "pantry", "plant", "hours", "timezone", "breathe", "mood", "scan", "sun", "school", "shift", "boxes", "gift", "vitals", "workout", "fuel", "trip", "resume", "metronome",
]


def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def fit_grid(n, avail_w, avail_h, gap=10, max_size=74, min_size=34):
    """Rows, icons per row, tile size and gap that fit `n` icons in the box.

    Fewest rows first, then the largest tile that fits both ways. Raises
    rather than returning something that would be drawn off the canvas -
    the failure this replaced was silent, and silence is the whole problem.
    """
    # Fewest rows first, and for each row count the requested gap first and
    # then tighter ones. Whitespace is the cheapest thing to give up: the tile
    # size is a legibility floor and the box is bounded by the tagline above
    # it, so the gap is the only slack there is. Added 2026-09-09 at 47 icons,
    # when 3 rows of the 34px floor needed 122px of a 120px box.
    for rows in (1, 2, 3, 4):
        per_row = -(-n // rows)                      # ceil
        for g in (gap, 8, 6, 4):
            if g > gap:
                continue
            s_w = (avail_w - g * (per_row - 1)) // per_row
            s_h = (avail_h - g * (rows - 1)) // rows
            size = min(max_size, s_w, s_h)
            if size >= min_size:
                return rows, per_row, int(size), g
    raise SystemExit(
        f"{n} icons will not fit legibly in {avail_w}x{avail_h}; "
        "give the strip more room or start dropping icons on purpose"
    )


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
        "Fifty-one Android utilities that each do one thing.",
        # Spelled out, not "%d" - so it does NOT move when APPS grows,
        # and a regex looking for a digit will miss it. It was four apps
        # behind on 2026-09-06 for exactly that reason.
        font=sub,
        fill=INK,
    )
    d.text(
        (left, py1 + 92),
        "Offline. No accounts. No tracking.",
        font=sub,
        fill=MUTED,
    )

    # The family, as a grid of its own icons.
    present = [n for n in APPS if (ICONS / f"list-{n}.png").exists()]
    avail_w = W - left * 2
    # DERIVED, not guessed. The strip is anchored to the bottom and grows
    # upward as apps are added, so the space it may use is whatever sits
    # between the tagline and the URL line. Hardcoding 120 was right by luck
    # until the 47th icon; raising it to 140 on 2026-09-09 immediately drew the
    # strip over the tagline, and the assertion below caught that on its first
    # run. Computing it cannot drift.
    tagline_bottom = py1 + 92 + sub.size
    avail_h = (H - 74) - (tagline_bottom + 8)
    rows, per_row, size, gap_i = fit_grid(len(present), avail_w, avail_h)
    # The old code only ever drew ONE row: it shrank the gap to 10 and the
    # tile to 48 and then gave up, so from about the nineteenth app onward
    # every further icon was painted past the right edge of the canvas and
    # was simply not in the picture. At 36 apps the row wanted 2078px of a
    # 1028px strip and nineteen icons were invisible - including every app
    # added since. Nothing warned, because drawing off-canvas is legal.
    # fit_grid now picks the row count, and the assertion below is what
    # would have caught it.
    block_h = rows * size + gap_i * (rows - 1)
    y = H - 74 - block_h               # bottom edge stays clear of the URL line
    # The horizontal overflow assertion below has existed since the day icons
    # were found being painted past the right edge. This is its vertical twin:
    # the strip grows UPWARD as apps are added, so the next thing it can run
    # into is the tagline, and drawing over text is just as legal and just as
    # silent as drawing off-canvas.
    assert y > tagline_bottom, (
        "the icon strip (top y=%d) would overlap the tagline (bottom y=%d) - "
        "move the strip, shrink the tiles, or drop icons on purpose"
        % (y, tagline_bottom)
    )
    for r in range(rows):
        x = left
        for name in present[r * per_row:(r + 1) * per_row]:
            f = ICONS / f"list-{name}.png"
            ic = Image.open(f).convert("RGBA").resize((size, size), Image.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, size - 1, size - 1), radius=int(size * 0.235), fill=255
            )
            img.paste(ic, (x, y), mask)
            x += size + gap_i
        assert x - gap_i <= W - left + 1, f"icon row {r} overflows the canvas"
        y += size + gap_i

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
