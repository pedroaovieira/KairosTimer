#!/usr/bin/env python3
"""Generate mock screenshots of PresentationTimer for documentation."""

from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 390, 844  # ~iPhone-size portrait (works for Android too)
OUT = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT, exist_ok=True)

# ── colours ─────────────────────────────────────────────────────────────────
BG_GREEN   = (46,  125, 50)
BG_YELLOW  = (249, 168, 37)
BG_RED     = (198, 40,  40)
WHITE      = (255, 255, 255)
DARK_TEXT  = (33,  33,  33)
SEMI_BLACK = (0,   0,   0,  180)

def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ── font helpers ─────────────────────────────────────────────────────────────
def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

def text_center(draw, text, y, fnt, color=WHITE):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=fnt, fill=color)

def text_at(draw, text, x, y, fnt, color=WHITE, anchor="la"):
    draw.text((x, y), text, font=fnt, fill=color, anchor=anchor)

# ── arc helper ───────────────────────────────────────────────────────────────
def draw_arc(draw, cx, cy, r, progress, track_color, indicator_color, thickness=14):
    # Track (full circle)
    bb = [cx - r, cy - r, cx + r, cy + r]
    draw.arc(bb, 0, 360, fill=track_color, width=thickness)
    # Indicator
    if progress > 0:
        angle = 360 * progress / 100
        draw.arc(bb, -90, -90 + angle, fill=indicator_color, width=thickness)

# ── status bar ───────────────────────────────────────────────────────────────
def status_bar(draw, bg):
    draw.rectangle([0, 0, W, 44], fill=bg)
    f = font(14)
    text_at(draw, "9:41", 16, 22, f, WHITE)
    text_at(draw, "●●●●  WiFi  100%", W - 16, 22, f, WHITE, anchor="ra")

# ── gear icon (simplified) ───────────────────────────────────────────────────
def draw_gear(draw, cx, cy, r=12, color=WHITE):
    teeth = 8
    inner_r = r * 0.55
    for i in range(teeth * 2):
        angle = math.radians(i * 360 / (teeth * 2))
        cr = r if i % 2 == 0 else r * 0.80
        x = cx + cr * math.cos(angle)
        y = cy + cr * math.sin(angle)
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=color)
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                 fill=color)
    draw.ellipse([cx - inner_r * 0.5, cy - inner_r * 0.5,
                  cx + inner_r * 0.5, cy + inner_r * 0.5],
                 fill=(0, 0, 0, 0))

# ── rounded rect helper ──────────────────────────────────────────────────────
def rounded_rect(draw, x0, y0, x1, y1, r=24, fill=None, outline=None, width=2):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=outline, width=width)

def pill_button(draw, cx, cy, w, h, label, bg, text_color=WHITE, fnt=None):
    fnt = fnt or font(18, bold=True)
    x0, y0 = cx - w // 2, cy - h // 2
    rounded_rect(draw, x0, y0, x0 + w, y0 + h, r=h // 2, fill=bg)
    bbox = draw.textbbox((0, 0), label, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x0 + (w - tw) // 2, y0 + (h - th) // 2), label, font=fnt, fill=text_color)

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 1: Setup / home screen
# ═══════════════════════════════════════════════════════════════════════════════
def screen_setup():
    img = Image.new("RGB", (W, H), BG_GREEN)
    draw = ImageDraw.Draw(img, "RGBA")
    status_bar(draw, BG_GREEN)

    # Gear icon top-right
    draw.ellipse([W - 54, 52, W - 14, 92], fill=(255, 255, 255, 40))
    draw_gear(draw, W - 34, 72, r=13, color=WHITE)

    # Phase label
    text_center(draw, "Set your time", 110, font(18), WHITE)

    # Arc ring
    cx, cy, arc_r = W // 2, 310, 120
    draw_arc(draw, cx, cy, arc_r, 100,
             (0, 0, 0, 50), (165, 214, 167), thickness=16)
    # Timer text
    text_center(draw, "00:00", cy - 42, font(64), WHITE)

    # Input fields row
    field_y = 470
    field_w, field_h = 84, 56
    labels = ["HH", "MM", "SS"]
    xs = [W // 2 - 144, W // 2 - 42, W // 2 + 60]
    for x, lbl in zip(xs, labels):
        rounded_rect(draw, x, field_y, x + field_w, field_y + field_h,
                     r=8, fill=(255, 255, 255, 30), outline=WHITE, width=2)
        text_center_x(draw, lbl, x, x + field_w, field_y + 14, font(14), (255,255,255,180))
        if lbl != "SS":
            text_at(draw, ":", x + field_w + 4, field_y + 14, font(26), WHITE)

    # Start button
    pill_button(draw, W // 2, 600, 160, 56, "Start",
                (0, 0, 0, 180))

    img.save(os.path.join(OUT, "01_setup.png"))
    print("01_setup.png")

def text_center_x(draw, text, x0, x1, y, fnt, color):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text((x0 + (x1 - x0 - tw) // 2, y), text, font=fnt, fill=color)

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 2: Timer running – green phase (68% remaining)
# ═══════════════════════════════════════════════════════════════════════════════
def screen_running(bg, arc_color, label, time_str, progress, filename):
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img, "RGBA")
    status_bar(draw, bg)

    text_color = WHITE if sum(bg) / 3 < 180 else DARK_TEXT

    text_center(draw, label, 110, font(18), text_color)

    cx, cy, arc_r = W // 2, 340, 130
    draw_arc(draw, cx, cy, arc_r, progress,
             (0, 0, 0, 50), arc_color, thickness=18)
    text_center(draw, time_str, cy - 46, font(68), text_color)

    # Pause + Reset buttons
    pill_button(draw, W // 2 - 88, 560, 150, 56, "Pause",  (0, 0, 0, 180))
    pill_button(draw, W // 2 + 88, 560, 150, 56, "Reset",  (0, 0, 0, 110))

    img.save(os.path.join(OUT, filename))
    print(filename)

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 5: Finished / time's up
# ═══════════════════════════════════════════════════════════════════════════════
def screen_finished():
    img = Image.new("RGB", (W, H), BG_RED)
    draw = ImageDraw.Draw(img, "RGBA")
    status_bar(draw, BG_RED)

    text_center(draw, "Time's up! ⏰", 110, font(22, bold=True), WHITE)

    cx, cy, arc_r = W // 2, 340, 130
    draw_arc(draw, cx, cy, arc_r, 0, (0, 0, 0, 50), (239, 154, 154), thickness=18)
    text_center(draw, "00:00", cy - 46, font(68), WHITE)

    pill_button(draw, W // 2, 560, 160, 56, "Reset", (0, 0, 0, 110))
    img.save(os.path.join(OUT, "05_finished.png"))
    print("05_finished.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 6: Settings – phases list
# ═══════════════════════════════════════════════════════════════════════════════
def screen_settings():
    img = Image.new("RGB", (W, H), (240, 240, 240))
    draw = ImageDraw.Draw(img, "RGBA")

    # Toolbar
    draw.rectangle([0, 0, W, 80], fill=BG_GREEN)
    text_at(draw, "←", 18, 26, font(24, bold=True), WHITE)
    text_at(draw, "Timer Phases", 56, 28, font(20, bold=True), WHITE)
    text_at(draw, "Save", W - 16, 28, font(18, bold=True), WHITE, anchor="ra")

    phases = [
        ("#2E7D32", "On track",    "50", "On track 🟢"),
        ("#F9A825", "Hurry up",    "20", "Hurry up! 🟡"),
        ("#C62828", "Almost done", "0",  "Almost out of time! 🔴"),
    ]

    card_y = 96
    for color_hex, name, threshold, message in phases:
        card_h = 172
        # Card shadow
        draw.rounded_rectangle([12, card_y + 3, W - 12, card_y + card_h + 3],
                                radius=12, fill=(0, 0, 0, 30))
        # Card body
        draw.rounded_rectangle([12, card_y, W - 12, card_y + card_h],
                                radius=12, fill=WHITE)

        # Color bar on left edge
        rgb = hex2rgb(color_hex)
        draw.rounded_rectangle([12, card_y, 24, card_y + card_h],
                                radius=12, fill=rgb)
        draw.rectangle([12, card_y, 20, card_y + card_h], fill=rgb)

        # Name
        text_at(draw, name, 32, card_y + 14, font(17, bold=True), DARK_TEXT)
        # Delete icon
        text_at(draw, "🗑", W - 28, card_y + 14, font(18), (211, 47, 47), anchor="ra")

        # Threshold row
        text_at(draw, f"Active when ≥ {threshold}% remaining", 32, card_y + 46, font(13), (100, 100, 100))

        # Message row
        text_at(draw, message, 32, card_y + 74, font(14), DARK_TEXT)

        # Color swatches (small row)
        text_at(draw, "Color:", 32, card_y + 106, font(12), (100, 100, 100))
        swatch_colors = ["#1B5E20","#2E7D32","#66BB6A","#F9A825","#E65100","#C62828","#EF5350","#1565C0","#6A1B9A"]
        sx = 80
        for sc in swatch_colors:
            sc_rgb = hex2rgb(sc)
            draw.ellipse([sx, card_y + 104, sx + 22, card_y + 126], fill=sc_rgb)
            if sc == color_hex:
                draw.ellipse([sx - 2, card_y + 102, sx + 24, card_y + 128],
                             outline=WHITE, width=2)
            sx += 28

        card_y += card_h + 10

    # FAB
    fab_cx, fab_cy = W - 36, H - 60
    draw.ellipse([fab_cx - 28, fab_cy - 28, fab_cx + 28, fab_cy + 28], fill=BG_GREEN)
    text_at(draw, "+", fab_cx, fab_cy - 14, font(36, bold=True), WHITE, anchor="ma")

    img.save(os.path.join(OUT, "06_settings.png"))
    print("06_settings.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 7: Settings – adding a new phase (color picker focused)
# ═══════════════════════════════════════════════════════════════════════════════
def screen_settings_add():
    img = Image.new("RGB", (W, H), (240, 240, 240))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle([0, 0, W, 80], fill=BG_GREEN)
    text_at(draw, "←", 18, 26, font(24, bold=True), WHITE)
    text_at(draw, "Timer Phases", 56, 28, font(20, bold=True), WHITE)
    text_at(draw, "Save", W - 16, 28, font(18, bold=True), WHITE, anchor="ra")

    # One existing card (abbreviated)
    draw.rounded_rectangle([12, 92, W - 12, 170], radius=12, fill=WHITE)
    rgb = hex2rgb("#2E7D32")
    draw.rounded_rectangle([12, 92, 24, 170], radius=12, fill=rgb)
    draw.rectangle([12, 92, 20, 170], fill=rgb)
    text_at(draw, "On track  ≥ 50%", 32, 106, font(15, bold=True), DARK_TEXT)
    text_at(draw, 'Message: "On track 🟢"', 32, 134, font(13), (100, 100, 100))

    # New phase card (expanded/highlighted)
    card_y = 184
    card_h = 380
    draw.rounded_rectangle([12, card_y + 3, W - 12, card_y + card_h + 3],
                            radius=12, fill=(0, 0, 0, 25))
    draw.rounded_rectangle([12, card_y, W - 12, card_y + card_h],
                            radius=14, fill=WHITE,
                            outline=(25, 118, 210), width=2)

    rgb_blue = hex2rgb("#1565C0")
    draw.rounded_rectangle([12, card_y, 24, card_y + card_h], radius=12, fill=rgb_blue)
    draw.rectangle([12, card_y, 20, card_y + card_h], fill=rgb_blue)

    # Name field
    text_at(draw, "Phase name", 32, card_y + 14, font(12), (100, 100, 100))
    draw.rounded_rectangle([30, card_y + 34, W - 30, card_y + 78],
                            radius=6, outline=(100, 100, 100), width=1)
    text_at(draw, "New phase", 42, card_y + 46, font(16), DARK_TEXT)

    # Threshold field
    text_at(draw, "Active when ≥ X% remaining (0–100)", 32, card_y + 90, font(12), (100, 100, 100))
    draw.rounded_rectangle([30, card_y + 108, W - 30, card_y + 152],
                            radius=6, outline=(100, 100, 100), width=1)
    text_at(draw, "10", 42, card_y + 120, font(16), DARK_TEXT)

    # Message field
    text_at(draw, "Message shown during this phase", 32, card_y + 164, font(12), (100, 100, 100))
    draw.rounded_rectangle([30, card_y + 182, W - 30, card_y + 226],
                            radius=6, outline=(100, 100, 100), width=1)
    text_at(draw, "New phase", 42, card_y + 194, font(16), DARK_TEXT)

    # Color picker label
    text_at(draw, "Background color", 32, card_y + 238, font(12), (100, 100, 100))

    # Color swatches
    swatch_colors = [
        "#1B5E20","#2E7D32","#66BB6A",
        "#F9A825","#E65100","#FF6D00",
        "#B71C1C","#C62828","#EF5350",
        "#1565C0","#0D47A1","#6A1B9A",
        "#37474F","#00695C","#4E342E",
    ]
    sx = 30
    sy = card_y + 258
    selected = "#1565C0"
    for i, sc in enumerate(swatch_colors):
        sc_rgb = hex2rgb(sc)
        draw.ellipse([sx, sy, sx + 30, sy + 30], fill=sc_rgb)
        if sc == selected:
            draw.ellipse([sx - 3, sy - 3, sx + 33, sy + 33],
                         outline=WHITE, width=3)
            draw.ellipse([sx - 5, sy - 5, sx + 35, sy + 35],
                         outline=(25, 118, 210), width=2)
        sx += 38
        if sx + 38 > W - 20:
            sx = 30
            sy += 38

    img.save(os.path.join(OUT, "07_settings_add.png"))
    print("07_settings_add.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 8: About screen
# ═══════════════════════════════════════════════════════════════════════════════
def screen_about():
    img = Image.new("RGB", (W, H), (250, 250, 250))
    draw = ImageDraw.Draw(img, "RGBA")

    # Toolbar
    draw.rectangle([0, 0, W, 80], fill=BG_GREEN)
    text_at(draw, "←", 18, 26, font(24, bold=True), WHITE)
    text_at(draw, "About", 56, 28, font(20, bold=True), WHITE)

    # App icon (circular green background with timer icon)
    ic_cx, ic_cy = W // 2, 190
    ic_r = 46
    draw.ellipse([ic_cx - ic_r, ic_cy - ic_r, ic_cx + ic_r, ic_cy + ic_r],
                 fill=hex2rgb("#1B5E20"))
    # Timer circle inside icon
    tr = 30
    draw.arc([ic_cx - tr, ic_cy - tr - 4, ic_cx + tr, ic_cy + tr - 4],
             0, 360, fill=WHITE, width=4)
    draw.line([ic_cx, ic_cy - 4, ic_cx, ic_cy - 18], fill=WHITE, width=3)
    draw.line([ic_cx, ic_cy - 4, ic_cx + 12, ic_cy + 4], fill=WHITE, width=3)

    # App name
    text_center(draw, "PresentationTimer", 255, font(22, bold=True), hex2rgb("#1B5E20"))
    text_center(draw, "Version 1.2.0", 287, font(14), (117, 117, 117))
    text_center(draw, "Full-screen countdown for presenters", 312, font(13), (55, 71, 79))

    # Divider
    div_x = W // 2
    draw.rectangle([div_x - 36, 342, div_x + 36, 344], fill=hex2rgb("#A5D6A7"))

    # "DEVELOPED BY"
    text_center(draw, "DEVELOPED BY", 360, font(11, bold=True), (158, 158, 158))

    # Pedro card
    def dev_card(y, initials, name, role, circle_color):
        draw.rounded_rectangle([16, y, W - 16, y + 72], radius=12, fill=WHITE)
        draw.rounded_rectangle([16, y + 2, 16 + 3, y + 70], radius=2,
                                fill=hex2rgb(circle_color))
        # Avatar circle
        ax, ay = 52, y + 36
        draw.ellipse([ax - 22, ay - 22, ax + 22, ay + 22],
                     fill=hex2rgb(circle_color))
        text_at(draw, initials, ax, ay - 8, font(14, bold=True), WHITE, anchor="ma")
        # Text
        text_at(draw, name, 84, y + 14, font(16, bold=True), DARK_TEXT)
        text_at(draw, role, 84, y + 40, font(13), (117, 117, 117))

    dev_card(382, "PV", "Pedro Vieira",  "App Developer",              "#2E7D32")
    dev_card(464, "AI", "Claude.ai",     "AI Partner · Anthropic",     "#CC785C")

    # License
    text_center(draw, "Open Source · MIT License", 554, font(13), (158, 158, 158))
    text_center(draw, "© 2025 Pedro Vieira",        576, font(13), (158, 158, 158))

    img.save(os.path.join(OUT, "08_about.png"))
    print("08_about.png")

# ── run all ──────────────────────────────────────────────────────────────────
screen_setup()
screen_running(BG_GREEN, (165, 214, 167), "On track 🟢", "18:24", 68, "02_green.png")
screen_running(BG_YELLOW, (255, 241, 118), "Hurry up! 🟡", "06:10", 37, "03_yellow.png")
screen_running(BG_RED,   (239, 154, 154), "Almost out of time! 🔴", "01:42", 12, "04_red.png")
screen_finished()
screen_settings()
screen_settings_add()
screen_about()
print("Done — all screenshots in docs/screenshots/")
