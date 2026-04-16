#!/usr/bin/env python3
"""Generate Google Play Store graphic assets: 512x512 icon and 1024x500 feature graphic."""

import os
from PIL import Image, ImageDraw, ImageFont

DOCS = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(DOCS, "play_store")
os.makedirs(OUT, exist_ok=True)

GREEN_DARK   = (27,  94, 32)    # #1B5E20
GREEN_MID    = (46, 125, 50)    # #2E7D32
GREEN_LIGHT  = (165, 214, 167)  # #A5D6A7
WHITE        = (255, 255, 255)

def try_font(size):
    for name in ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "Arial.ttf", "LiberationSans-Bold.ttf"]:
        for base in ["/usr/share/fonts/truetype/dejavu/",
                     "/usr/share/fonts/truetype/liberation/",
                     "/usr/share/fonts/",
                     "/usr/local/share/fonts/"]:
            path = os.path.join(base, name)
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def draw_timer_icon(draw, cx, cy, r, color=WHITE, stroke=6):
    """Draw a minimal timer/clock icon centred at (cx, cy) with radius r."""
    # Outer circle
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color, width=stroke)
    # Inner tick marks (12, 3, 6, 9 o'clock)
    import math
    for angle_deg in [0, 90, 180, 270]:
        rad = math.radians(angle_deg - 90)
        x0 = cx + (r - stroke*2) * math.cos(rad)
        y0 = cy + (r - stroke*2) * math.sin(rad)
        x1 = cx + (r - stroke*4.5) * math.cos(rad)
        y1 = cy + (r - stroke*4.5) * math.sin(rad)
        draw.line([x0, y0, x1, y1], fill=color, width=stroke)
    # Hands: minute hand pointing to ~10 o'clock
    angle_min = math.radians(-60)
    draw.line([cx, cy,
               cx + (r * 0.55) * math.cos(angle_min),
               cy + (r * 0.55) * math.sin(angle_min)],
              fill=color, width=stroke)
    # Hour hand pointing to ~12 o'clock
    angle_hr = math.radians(-90)
    draw.line([cx, cy,
               cx + (r * 0.38) * math.cos(angle_hr),
               cy + (r * 0.38) * math.sin(angle_hr)],
              fill=color, width=stroke)
    # Centre dot
    dot = stroke // 2 + 1
    draw.ellipse([cx-dot, cy-dot, cx+dot, cy+dot], fill=color)

# ── 512 × 512 App Icon ──────────────────────────────────────────────────────

def make_icon():
    S = 512
    img = Image.new("RGBA", (S, S), GREEN_DARK)
    draw = ImageDraw.Draw(img)

    # Subtle radial gradient feel: lighter inner circle
    r_grad = 210
    cx, cy = S//2, S//2
    draw.ellipse([cx-r_grad, cy-r_grad, cx+r_grad, cy+r_grad],
                 fill=GREEN_MID)

    # Timer icon
    draw_timer_icon(draw, cx, cy-10, r=140, color=WHITE, stroke=14)

    # Bottom label "PT" subtle
    font_small = try_font(52)
    draw.text((cx, cy + 165), "PT", font=font_small, fill=(*GREEN_LIGHT, 200),
              anchor="mm")

    # Save as PNG (RGBA is fine for Play Store icon, but no transparency required
    # on the actual listing — the store overlays a shape mask)
    path = os.path.join(OUT, "icon_512.png")
    img.save(path)
    print(f"Icon      → {path}  ({os.path.getsize(path)//1024} KB)")

# ── 1024 × 500 Feature Graphic ───────────────────────────────────────────────

def make_feature_graphic():
    W, H = 1024, 500
    img = Image.new("RGB", (W, H), GREEN_DARK)
    draw = ImageDraw.Draw(img)

    # Gradient band
    for x in range(W):
        t = x / W
        r = int(GREEN_DARK[0] + (GREEN_MID[0] - GREEN_DARK[0]) * t)
        g = int(GREEN_DARK[1] + (GREEN_MID[1] - GREEN_DARK[1]) * t)
        b = int(GREEN_DARK[2] + (GREEN_MID[2] - GREEN_DARK[2]) * t)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    # Large decorative timer (right side)
    draw_timer_icon(draw, W - 190, H//2, r=160, color=(*WHITE, 30), stroke=18)
    draw_timer_icon(draw, W - 190, H//2 + 5, r=155, color=(*WHITE, 15), stroke=3)

    # App name
    font_title = try_font(72)
    font_sub   = try_font(32)
    font_tag   = try_font(26)

    draw.text((72, 160), "Presentation", font=font_title, fill=WHITE)
    draw.text((72, 240), "Timer",        font=font_title, fill=GREEN_LIGHT)

    # Underline
    draw.rectangle([72, 318, 72 + 320, 321], fill=GREEN_LIGHT)

    draw.text((72, 340), "Full-screen countdown for presenters",
              font=font_tag, fill=(*WHITE, 200))

    path = os.path.join(OUT, "feature_graphic.png")
    img.save(path)
    print(f"Feature   → {path}  ({os.path.getsize(path)//1024} KB)")

make_icon()
make_feature_graphic()
print("Done — assets saved to docs/play_store/")
