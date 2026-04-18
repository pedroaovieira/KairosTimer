#!/usr/bin/env python3
"""Generate mock screenshots of PresentationTimer — Temporal Monolith design."""

from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 390, 844
OUT = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "src", "main", "res", "font")

# ── Colour palette ────────────────────────────────────────────────────────────
BG_DARK              = (26,  26,  26)   # #1A1A1A
SURFACE_LOW          = (28,  27,  27)   # #1C1B1B
SURFACE_HIGH         = (42,  42,  42)   # #2A2A2A
SURFACE_HIGHEST      = (53,  53,  52)   # #353534
PRIMARY              = (90,  240, 179)  # #5AF0B3  mint
ON_PRIMARY           = (0,   56,  37)   # #003825
SECONDARY            = (255, 185, 95)   # #FFB95F  amber
TERTIARY             = (255, 202, 197)  # #FFCAC5  coral
ON_SURFACE           = (229, 226, 225)  # #E5E2E1
ON_SURFACE_VAR       = (187, 202, 192)  # #BBCAC0
OUTLINE              = (133, 148, 139)  # #85948B
OUTLINE_VAR          = (60,  74,  66)   # #3C4A42
DARK_INK             = (13,  13,  13)   # #0D0D0D

def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ── Font loader (tries project fonts first, then system fallbacks) ────────────
def font(size, bold=False, family="manrope"):
    proj = {
        ("space_grotesk", True):  os.path.join(FONT_DIR, "space_grotesk_bold.ttf"),
        ("space_grotesk", False): os.path.join(FONT_DIR, "space_grotesk_regular.ttf"),
        ("manrope",        True):  os.path.join(FONT_DIR, "manrope_bold.ttf"),
        ("manrope",        False): os.path.join(FONT_DIR, "manrope_regular.ttf"),
    }
    system = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    candidates = [proj.get((family, bold))] + system
    for path in candidates:
        if path and os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def sg(size):  return font(size, bold=True,  family="space_grotesk")
def mn(size):  return font(size, bold=False, family="manrope")
def mnb(size): return font(size, bold=True,  family="manrope")

# ── Drawing helpers ───────────────────────────────────────────────────────────
def cw(draw, text, y, fnt, color):
    bb = draw.textbbox((0, 0), text, font=fnt)
    draw.text(((W - (bb[2]-bb[0])) // 2, y), text, font=fnt, fill=color)

def at(draw, text, x, y, fnt, color, anchor="la"):
    draw.text((x, y), text, font=fnt, fill=color, anchor=anchor)

def pill(draw, cx, cy, w, h, label, bg, fg, fnt=None):
    fnt = fnt or mnb(16)
    x0, y0 = cx - w//2, cy - h//2
    draw.rounded_rectangle([x0, y0, x0+w, y0+h], radius=h//2, fill=bg)
    bb = draw.textbbox((0, 0), label, font=fnt)
    draw.text((x0 + (w-(bb[2]-bb[0]))//2, y0 + (h-(bb[3]-bb[1]))//2),
              label, font=fnt, fill=fg)

def circle_btn(draw, cx, cy, r, icon, bg, fg, fnt=None):
    fnt = fnt or sg(22)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg)
    bb = draw.textbbox((0, 0), icon, font=fnt)
    draw.text((cx - (bb[2]-bb[0])//2, cy - (bb[3]-bb[1])//2), icon, font=fnt, fill=fg)

def status_bar(draw, bg, text_color):
    draw.rectangle([0, 0, W, 40], fill=bg)
    draw.text((16, 11), "9:41", font=mn(13), fill=text_color)
    draw.text((W-16, 11), "●●●  WiFi  100%", font=mn(13), fill=text_color, anchor="ra")

def aura_bar(draw, color, y=40):
    draw.rectangle([0, y, W, y+4], fill=color)

def progress_bar(draw, y, progress, track_color, indicator_color):
    x0, x1 = 56, W-56
    draw.rounded_rectangle([x0, y, x1, y+4], radius=2, fill=track_color)
    if progress > 0:
        fill_w = int((x1-x0) * progress / 100)
        draw.rounded_rectangle([x0, y, x0+fill_w, y+4], radius=2, fill=indicator_color)

def toolbar(draw, title, has_info=False, has_save=False):
    draw.rectangle([0, 0, W, 72], fill=SURFACE_LOW)
    at(draw, "←", 20, 20, sg(22), ON_SURFACE)
    at(draw, title, 56, 22, mnb(18), ON_SURFACE)
    x = W - 20
    if has_info:
        at(draw, "ℹ", x, 22, mnb(20), PRIMARY, anchor="ra")
        x -= 44
    if has_save:
        at(draw, "Save", x, 22, mnb(16), PRIMARY, anchor="ra")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — Setup
# ═══════════════════════════════════════════════════════════════════════════════
def screen_setup():
    img = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(img)
    status_bar(d, BG_DARK, ON_SURFACE_VAR)
    aura_bar(d, PRIMARY)

    # TEMPORAL brand
    cw(d, "TEMPORAL", 56, sg(13), PRIMARY)
    # Gear icon top-right
    d.ellipse([W-54, 48, W-14, 88], fill=SURFACE_HIGH)
    at(d, "⚙", W-34, 56, mn(20), ON_SURFACE_VAR, anchor="ma")

    # "SET THE\nPACE" headline
    cw(d, "SET THE", 200, sg(52), ON_SURFACE)
    cw(d, "PACE",    252, sg(52), ON_SURFACE)

    # SESSION DURATION label
    cw(d, "SESSION DURATION", 330, mnb(10), OUTLINE)

    # HH:MM:SS card
    card_x, card_y, card_h = 40, 356, 92
    d.rectangle([card_x, card_y, W-card_x, card_y+card_h], fill=SURFACE_LOW)
    # HH
    at(d, "HH", 78, card_y+10, mnb(9), OUTLINE)
    at(d, "00", 76, card_y+24, sg(42), OUTLINE_VAR)
    # :
    at(d, ":", 160, card_y+28, sg(34), OUTLINE_VAR)
    # MM
    at(d, "MM", 174, card_y+10, mnb(9), OUTLINE)
    at(d, "00", 172, card_y+24, sg(42), OUTLINE_VAR)
    # :
    at(d, ":", 258, card_y+28, sg(34), OUTLINE_VAR)
    # SS
    at(d, "SS", 272, card_y+10, mnb(9), OUTLINE)
    at(d, "00", 270, card_y+24, sg(42), OUTLINE_VAR)

    # INITIALIZE button
    pill(d, W//2, 560, 220, 56, "INITIALIZE", PRIMARY, ON_PRIMARY, mnb(14))

    img.save(os.path.join(OUT, "01_setup.png"))
    print("01_setup.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREENS 2-4 — Running phases
# ═══════════════════════════════════════════════════════════════════════════════
def screen_running(bg_color, label, time_str, progress, filename):
    img = Image.new("RGB", (W, H), bg_color)
    d = ImageDraw.Draw(img)
    status_bar(d, bg_color, DARK_INK)
    aura_bar(d, DARK_INK)

    # TEMPORAL brand
    cw(d, "TEMPORAL", 56, sg(13), DARK_INK)

    # Phase label — big, dark
    cw(d, label, 118, mnb(20), DARK_INK)

    # Large countdown
    cw(d, time_str, 195, sg(88), DARK_INK)

    # Linear progress bar + label
    progress_bar(d, 440, progress, (0,0,0,60), DARK_INK)
    cw(d, "REMAINING", 456, mnb(9), DARK_INK)

    # Buttons: reset (small dark circle left) + pause (large dark circle)
    circle_btn(d, W//2 - 72, 580, 32, "■", SURFACE_HIGHEST, ON_SURFACE, mn(18))
    circle_btn(d, W//2,      580, 44, "⏸", DARK_INK,         bg_color,   mn(28))

    img.save(os.path.join(OUT, filename))
    print(filename)

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 5 — Finished
# ═══════════════════════════════════════════════════════════════════════════════
def screen_finished():
    bg = TERTIARY
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    status_bar(d, bg, DARK_INK)
    aura_bar(d, DARK_INK)

    cw(d, "TEMPORAL", 56, sg(13), DARK_INK)
    cw(d, "TIME'S UP", 118, mnb(20), DARK_INK)
    # Timer text (shown bold/bolder to imply flashing)
    cw(d, "00:00", 195, sg(88), DARK_INK)

    progress_bar(d, 440, 0, (0,0,0,60), DARK_INK)
    cw(d, "REMAINING", 456, mnb(9), DARK_INK)

    circle_btn(d, W//2, 580, 32, "■", DARK_INK, bg, mn(18))

    img.save(os.path.join(OUT, "05_finished.png"))
    print("05_finished.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 6 — Settings (phases list)
# ═══════════════════════════════════════════════════════════════════════════════
def screen_settings():
    img = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(img)
    toolbar(d, "Timer Phases", has_info=True, has_save=True)

    phases = [
        ("#5AF0B3", "On track",    "50", "On track"),
        ("#FFB95F", "Hurry up",    "20", "Hurry up!"),
        ("#FFCAC5", "Almost done", "0",  "Almost out of time!"),
    ]

    card_y = 84
    for color_hex, name, threshold, message in phases:
        card_h = 100
        d.rounded_rectangle([14, card_y, W-14, card_y+card_h],
                             radius=12, fill=SURFACE_HIGH)
        ph_rgb = rgb(color_hex)
        # Color dot indicator
        d.ellipse([28, card_y+16, 28+16, card_y+16+16], fill=ph_rgb)
        at(d, name,      56, card_y+14, mnb(15), ON_SURFACE)
        at(d, "🗑",      W-30, card_y+14, mn(16), (239, 83, 80), anchor="ra")
        at(d, f"Active when ≥ {threshold}% remaining",
               28, card_y+42, mn(12), OUTLINE)
        at(d, message,   28, card_y+62, mn(14), ON_SURFACE_VAR)

        # Color swatches (small strip)
        sx = 28
        swatches = ["#5AF0B3","#FFB95F","#FFCAC5","#34D399","#60A5FA","#F87171","#A78BFA"]
        for sc in swatches:
            sr = rgb(sc)
            d.ellipse([sx, card_y+80, sx+16, card_y+96], fill=sr)
            if sc == color_hex:
                d.ellipse([sx-2, card_y+78, sx+18, card_y+98],
                          outline=ON_SURFACE, width=2)
            sx += 22

        card_y += card_h + 8

    # FAB
    d.ellipse([W-64, H-80, W-16, H-32], fill=PRIMARY)
    cw_fab = W - 40
    at(d, "+", cw_fab, H-68, sg(28), ON_PRIMARY, anchor="ma")

    img.save(os.path.join(OUT, "06_settings.png"))
    print("06_settings.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 7 — Settings (adding a phase)
# ═══════════════════════════════════════════════════════════════════════════════
def screen_settings_add():
    img = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(img)
    toolbar(d, "Timer Phases", has_info=True, has_save=True)

    # Existing phase (condensed)
    d.rounded_rectangle([14, 84, W-14, 154], radius=12, fill=SURFACE_HIGH)
    d.ellipse([28, 100, 44, 116], fill=PRIMARY)
    at(d, "On track", 56, 98, mnb(15), ON_SURFACE)
    at(d, "≥ 50% remaining · \"On track\"", 56, 122, mn(12), OUTLINE)

    # New phase card (highlighted with primary border)
    card_y, card_h = 162, 380
    d.rounded_rectangle([14, card_y, W-14, card_y+card_h],
                         radius=12, fill=SURFACE_HIGH, outline=PRIMARY, width=2)

    # Name field
    d.rounded_rectangle([28, card_y+14, W-28, card_y+56],
                         radius=6, fill=SURFACE_LOW, outline=OUTLINE_VAR, width=1)
    at(d, "Phase name", 36, card_y+8, mn(11), OUTLINE)
    at(d, "New phase",  36, card_y+26, mn(15), ON_SURFACE)

    # Threshold field
    d.rounded_rectangle([28, card_y+68, W-28, card_y+110],
                         radius=6, fill=SURFACE_LOW, outline=OUTLINE_VAR, width=1)
    at(d, "Active when ≥ X% remaining (0–100)", 36, card_y+62, mn(11), OUTLINE)
    at(d, "10",  36, card_y+80, mn(15), ON_SURFACE)

    # Message field
    d.rounded_rectangle([28, card_y+122, W-28, card_y+164],
                         radius=6, fill=SURFACE_LOW, outline=OUTLINE_VAR, width=1)
    at(d, "Message shown during this phase", 36, card_y+116, mn(11), OUTLINE)
    at(d, "New phase", 36, card_y+134, mn(15), ON_SURFACE)

    # Color label
    at(d, "BACKGROUND COLOR", 28, card_y+176, mnb(9), OUTLINE)

    # Color swatches
    swatches = ["#5AF0B3","#FFB95F","#FFCAC5","#34D399","#60A5FA",
                "#F87171","#A78BFA","#34D399","#FBBF24","#FB923C"]
    sx, sy = 28, card_y+198
    selected = "#60A5FA"
    for sc in swatches:
        sr = rgb(sc)
        d.ellipse([sx, sy, sx+28, sy+28], fill=sr)
        if sc == selected:
            d.ellipse([sx-3, sy-3, sx+31, sy+31], outline=ON_SURFACE, width=2)
        sx += 36
        if sx + 36 > W - 14:
            sx, sy = 28, sy + 36

    img.save(os.path.join(OUT, "07_settings_add.png"))
    print("07_settings_add.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 8 — About
# ═══════════════════════════════════════════════════════════════════════════════
def screen_about():
    img = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(img)
    toolbar(d, "About")

    # App icon
    ic_cx, ic_cy = W//2, 180
    d.ellipse([ic_cx-40, ic_cy-40, ic_cx+40, ic_cy+40], fill=SURFACE_HIGH)
    d.arc([ic_cx-24, ic_cy-28, ic_cx+24, ic_cy+20], 0, 360, fill=PRIMARY, width=4)
    d.line([ic_cx, ic_cy-4, ic_cx, ic_cy-20], fill=PRIMARY, width=3)
    d.line([ic_cx, ic_cy-4, ic_cx+14, ic_cy+6], fill=PRIMARY, width=3)

    # Brand + version
    cw(d, "TEMPORAL",                        238, sg(28),  PRIMARY)
    cw(d, "Version 1.3.2",                   280, mn(13),  OUTLINE)
    cw(d, "Full-screen countdown for presenters", 304, mn(14), ON_SURFACE_VAR)

    # Divider
    d.rectangle([W//2-24, 336, W//2+24, 338], fill=OUTLINE_VAR)

    cw(d, "DEVELOPED BY", 354, mnb(10), OUTLINE)

    def dev_card(y, initials, name, role, dot_color):
        d.rounded_rectangle([16, y, W-16, y+72], radius=12, fill=SURFACE_HIGH)
        d.ellipse([30, y+14, 74, y+58], fill=dot_color)
        at(d, initials, 52, y+24, sg(15), BG_DARK, anchor="ma")
        at(d, name,  86, y+14, mnb(15), ON_SURFACE)
        at(d, role,  86, y+38, mn(12),  OUTLINE)

    dev_card(376, "PV", "Pedro Vieira", "App Developer",            PRIMARY)
    dev_card(458, "AI", "Claude.ai",    "AI Development Partner · Anthropic", rgb("#CC785C"))

    # Website
    cw(d, "pedrov.org", 548, mnb(14), PRIMARY)

    # License / copyright
    cw(d, "Open Source · MIT License", 580, mn(12), OUTLINE)
    cw(d, "© 2025 Pedro Vieira",       600, mn(12), OUTLINE)

    img.save(os.path.join(OUT, "08_about.png"))
    print("08_about.png")

# ── Run all ───────────────────────────────────────────────────────────────────
screen_setup()
screen_running(PRIMARY,   "ON TRACK",           "18:24", 68, "02_green.png")
screen_running(SECONDARY, "HURRY UP!",           "06:10", 37, "03_yellow.png")
screen_running(TERTIARY,  "ALMOST OUT OF TIME!", "01:42", 12, "04_red.png")
screen_finished()
screen_settings()
screen_settings_add()
screen_about()
print("\nDone — screenshots in docs/screenshots/")
