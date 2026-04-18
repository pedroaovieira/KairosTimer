#!/usr/bin/env python3
"""Generate mock screenshots of PresentationTimer — Temporal Monolith design v1.4.0."""

from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 390, 844
OUT = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "src", "main", "res", "font")

# ── Colour palette ────────────────────────────────────────────────────────────
BG_DARK         = (26,  26,  26)   # #1A1A1A
SURFACE_LOW     = (28,  27,  27)   # #1C1B1B
SURFACE_HIGH    = (42,  42,  42)   # #2A2A2A
SURFACE_HIGHEST = (53,  53,  52)   # #353534
PRIMARY         = (90,  240, 179)  # #5AF0B3  mint
ON_PRIMARY      = (0,   56,  37)   # #003825
SECONDARY       = (255, 185, 95)   # #FFB95F  amber
TERTIARY        = (255, 202, 197)  # #FFCAC5  coral
ON_SURFACE      = (229, 226, 225)  # #E5E2E1
ON_SURFACE_VAR  = (187, 202, 192)  # #BBCAC0
OUTLINE         = (133, 148, 139)  # #85948B
OUTLINE_VAR     = (60,  74,  66)   # #3C4A42
DARK_INK        = (13,  13,  13)   # #0D0D0D

def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def blend(c, alpha):
    """Blend color c onto DARK_INK background at given alpha (0–1)."""
    return tuple(int(DARK_INK[i] + (c[i] - DARK_INK[i]) * alpha) for i in range(3))

# ── Font loader ───────────────────────────────────────────────────────────────
def font(size, bold=False, family="manrope"):
    proj = {
        ("space_grotesk", True):  os.path.join(FONT_DIR, "space_grotesk_bold.ttf"),
        ("space_grotesk", False): os.path.join(FONT_DIR, "space_grotesk_regular.ttf"),
        ("manrope",       True):  os.path.join(FONT_DIR, "manrope_bold.ttf"),
        ("manrope",       False): os.path.join(FONT_DIR, "manrope_regular.ttf"),
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
    fnt = fnt or mnb(14)
    x0, y0 = cx - w//2, cy - h//2
    draw.rounded_rectangle([x0, y0, x0+w, y0+h], radius=h//2, fill=bg)
    bb = draw.textbbox((0, 0), label, font=fnt)
    draw.text((x0 + (w-(bb[2]-bb[0]))//2, y0 + (h-(bb[3]-bb[1]))//2),
              label, font=fnt, fill=fg)

def status_bar(draw, bg, text_color):
    draw.rectangle([0, 0, W, 40], fill=bg)
    draw.text((16, 11), "9:41", font=mn(13), fill=text_color)
    draw.text((W-16, 11), "●●●  WiFi  100%", font=mn(13), fill=text_color, anchor="ra")

def aura_bar(draw, color, y=40):
    draw.rectangle([0, y, W, y+4], fill=color)

def progress_bar(draw, y, progress, pct_text, track_color, indicator_color, label_color):
    """Draw progress row: percentage on left, REMAINING on right, bar below."""
    x0, x1 = 56, W-56
    # Percentage label (left)
    at(draw, pct_text, x0, y, mnb(11), label_color)
    # REMAINING label (right)
    at(draw, "REMAINING", x1, y, mnb(9), label_color, anchor="ra")
    bar_y = y + 18
    draw.rounded_rectangle([x0, bar_y, x1, bar_y+4], radius=2, fill=track_color)
    if progress > 0:
        fill_w = int((x1-x0) * progress / 100)
        draw.rounded_rectangle([x0, bar_y, x0+fill_w, bar_y+4], radius=2, fill=indicator_color)

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
    cw(d, "SET THE", 180, sg(52), ON_SURFACE)
    cw(d, "PACE",    232, sg(52), ON_SURFACE)

    # SESSION DURATION label
    cw(d, "SESSION DURATION", 308, mnb(10), OUTLINE)

    # HH:MM:SS card
    card_x, card_y, card_h = 40, 328, 88
    d.rectangle([card_x, card_y, W-card_x, card_y+card_h], fill=SURFACE_LOW)
    # HH
    at(d, "HH", 78, card_y+8, mnb(9), OUTLINE)
    at(d, "00", 76, card_y+22, sg(40), OUTLINE_VAR)
    # :
    at(d, ":", 158, card_y+26, sg(32), OUTLINE_VAR)
    # MM
    at(d, "MM", 174, card_y+8, mnb(9), OUTLINE)
    at(d, "00", 172, card_y+22, sg(40), OUTLINE_VAR)
    # :
    at(d, ":", 256, card_y+26, sg(32), OUTLINE_VAR)
    # SS
    at(d, "SS", 272, card_y+8, mnb(9), OUTLINE)
    at(d, "00", 270, card_y+22, sg(40), OUTLINE_VAR)

    # QUICK PRESETS label
    cw(d, "QUICK PRESETS", 432, mnb(9), OUTLINE)

    # Preset pills row: 5 / 15 / 25 / 45
    preset_y = 450
    labels = ["5 min", "15 min", "25 min", "45 min"]
    pill_w, pill_h = 72, 34
    total_w = len(labels) * pill_w + (len(labels)-1) * 10
    px = (W - total_w) // 2
    for lbl in labels:
        d.rounded_rectangle([px, preset_y, px+pill_w, preset_y+pill_h],
                             radius=pill_h//2, fill=SURFACE_HIGHEST, outline=OUTLINE_VAR, width=1)
        bb = d.textbbox((0,0), lbl, font=mnb(12))
        tw = bb[2]-bb[0]
        d.text((px + (pill_w-tw)//2, preset_y + 9), lbl, font=mnb(12), fill=ON_SURFACE_VAR)
        px += pill_w + 10

    # INITIALIZE button
    pill(d, W//2, 540, 220, 52, "INITIALIZE", PRIMARY, ON_PRIMARY, mnb(14))

    img.save(os.path.join(OUT, "01_setup.png"))
    print("01_setup.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREENS 2-4 — Running phases
# ═══════════════════════════════════════════════════════════════════════════════
def screen_running(bg_color, label, time_str, progress, filename, paused=False):
    img = Image.new("RGB", (W, H), bg_color)
    d = ImageDraw.Draw(img)
    status_bar(d, bg_color, DARK_INK)
    aura_bar(d, DARK_INK)

    # TEMPORAL brand
    cw(d, "TEMPORAL", 56, sg(13), DARK_INK)

    # Phase label
    cw(d, "PAUSED" if paused else label, 112, mnb(18), DARK_INK)

    # Halo glow (subtle circle behind the timer)
    if not paused:
        halo_r = 145
        cx, cy = W//2, 240
        halo_color = blend(bg_color, 0.35)
        for i in range(4, 0, -1):
            r = halo_r + i * 10
            alpha = int(30 - i*6)
            overlay = Image.new("RGBA", (W, H), (0,0,0,0))
            od = ImageDraw.Draw(overlay)
            od.ellipse([cx-r, cy-r, cx+r, cy+r],
                       fill=(*halo_color, alpha))
            img = img.convert("RGBA")
            img = Image.alpha_composite(img, overlay)
            img = img.convert("RGB")
            d = ImageDraw.Draw(img)

    # Large countdown — fade if paused
    timer_color = blend(DARK_INK, 0.55) if paused else DARK_INK
    cw(d, time_str, 175, sg(88), timer_color)

    # Progress row
    pct_text = f"{progress}%"
    tr_col = blend(bg_color, 0.35) if True else DARK_INK
    progress_bar(d, 390, progress, pct_text,
                 track_color=blend(bg_color, 0.4),
                 indicator_color=DARK_INK,
                 label_color=DARK_INK)

    # Segmented control: PAUSE/RESUME + STOP pills
    seg_cy = 510
    left_w, right_w, pill_h2 = 148, 112, 52
    gap = 10
    total_seg = left_w + gap + right_w
    left_x = (W - total_seg) // 2
    right_x = left_x + left_w + gap

    # Left pill: PAUSE (dark ink) or RESUME (dark ink)
    left_label = "▶  RESUME" if paused else "PAUSE"
    d.rounded_rectangle([left_x, seg_cy - pill_h2//2,
                          left_x+left_w, seg_cy + pill_h2//2],
                         radius=pill_h2//2, fill=DARK_INK)
    bb = d.textbbox((0,0), left_label, font=mnb(14))
    tw = bb[2]-bb[0]
    d.text((left_x + (left_w-tw)//2, seg_cy - (bb[3]-bb[1])//2),
           left_label, font=mnb(14), fill=bg_color)

    # Right pill: STOP (dark surface)
    d.rounded_rectangle([right_x, seg_cy - pill_h2//2,
                          right_x+right_w, seg_cy + pill_h2//2],
                         radius=pill_h2//2, fill=(26, 26, 26))
    at(d, "■  STOP", right_x + right_w//2, seg_cy - 8, mnb(13), ON_SURFACE, anchor="ma")

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

    cw(d, "TEMPORAL",  56,  sg(13), DARK_INK)
    cw(d, "TIME'S UP", 112, mnb(18), DARK_INK)
    cw(d, "00:00",     175, sg(88), blend(DARK_INK, 0.7))

    progress_bar(d, 390, 0, "0%",
                 track_color=blend(TERTIARY, 0.4),
                 indicator_color=DARK_INK,
                 label_color=DARK_INK)

    # Single RESET button (finished state)
    pill(d, W//2, 510, 160, 52, "■  RESET",
         (26, 26, 26), ON_SURFACE, mnb(14))

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
        ("#5AF0B3", "On track",    50, "On track"),
        ("#FFB95F", "Hurry up",    20, "Hurry up!"),
        ("#FFCAC5", "Almost done",  0, "Almost out of time!"),
    ]

    card_y = 84
    for color_hex, name, threshold, message in phases:
        card_h = 148
        d.rounded_rectangle([14, card_y, W-14, card_y+card_h],
                             radius=12, fill=SURFACE_HIGH)
        ph_rgb = rgb(color_hex)

        # Name + delete row
        at(d, name, 28, card_y+14, mnb(15), ON_SURFACE)
        # Red trash icon
        at(d, "🗑", W-28, card_y+14, mn(16), (239, 83, 80), anchor="ra")

        # Threshold slider row
        at(d, "ACTIVE WHEN ≥", 28, card_y+46, mnb(9), OUTLINE)
        at(d, f"{threshold}%",  W-28, card_y+43, sg(14), PRIMARY, anchor="ra")
        # Slider track
        sx0, sx1, sy = 28, W-28, card_y+64
        d.rounded_rectangle([sx0, sy, sx1, sy+4], radius=2, fill=OUTLINE_VAR)
        fill_end = sx0 + int((sx1-sx0) * threshold / 100)
        if threshold > 0:
            d.rounded_rectangle([sx0, sy, fill_end, sy+4], radius=2, fill=PRIMARY)
        # Thumb
        thumb_x = max(sx0, fill_end)
        d.ellipse([thumb_x-8, sy-6, thumb_x+8, sy+10], fill=PRIMARY)

        # Message
        at(d, message, 28, card_y+84, mn(13), ON_SURFACE_VAR)

        # Color swatches
        swatches = ["#5AF0B3","#FFB95F","#FFCAC5","#34D399","#60A5FA","#F87171","#A78BFA"]
        sx2 = 28
        sw_y = card_y+108
        for sc in swatches:
            sr = rgb(sc)
            d.ellipse([sx2, sw_y, sx2+20, sw_y+20], fill=sr)
            if sc == color_hex:
                d.ellipse([sx2-2, sw_y-2, sx2+22, sw_y+22], outline=ON_SURFACE, width=2)
            sx2 += 28

        card_y += card_h + 8

    # FAB
    d.ellipse([W-64, H-80, W-16, H-32], fill=PRIMARY)
    at(d, "+", W-40, H-68, sg(28), ON_PRIMARY, anchor="ma")

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
    d.rounded_rectangle([14, 84, W-14, 146], radius=12, fill=SURFACE_HIGH)
    d.ellipse([28, 100, 44, 116], fill=PRIMARY)
    at(d, "On track", 56, 98, mnb(14), ON_SURFACE)
    at(d, "≥ 50% remaining  ·  \"On track\"", 56, 122, mn(11), OUTLINE)

    # New phase card (highlighted with primary border)
    card_y, card_h = 154, 380
    d.rounded_rectangle([14, card_y, W-14, card_y+card_h],
                         radius=12, fill=SURFACE_HIGH, outline=PRIMARY, width=2)

    # Name field
    at(d, "PHASE NAME", 28, card_y+16, mnb(9), OUTLINE)
    d.rounded_rectangle([28, card_y+32, W-28, card_y+68],
                         radius=6, fill=SURFACE_LOW, outline=OUTLINE_VAR, width=1)
    at(d, "New phase", 36, card_y+42, mn(14), ON_SURFACE)

    # Threshold slider row
    at(d, "ACTIVE WHEN ≥", 28, card_y+84, mnb(9), OUTLINE)
    at(d, "10%", W-28, card_y+81, sg(14), PRIMARY, anchor="ra")
    sx0, sx1, sly = 28, W-28, card_y+100
    d.rounded_rectangle([sx0, sly, sx1, sly+4], radius=2, fill=OUTLINE_VAR)
    fill_end = sx0 + int((sx1-sx0) * 10 / 100)
    d.rounded_rectangle([sx0, sly, fill_end, sly+4], radius=2, fill=PRIMARY)
    d.ellipse([fill_end-8, sly-6, fill_end+8, sly+10], fill=PRIMARY)

    # Message field
    at(d, "MESSAGE", 28, card_y+122, mnb(9), OUTLINE)
    d.rounded_rectangle([28, card_y+138, W-28, card_y+174],
                         radius=6, fill=SURFACE_LOW, outline=OUTLINE_VAR, width=1)
    at(d, "New phase", 36, card_y+148, mn(14), ON_SURFACE)

    # Color label
    at(d, "BACKGROUND COLOR", 28, card_y+188, mnb(9), OUTLINE)

    # Color swatches (two rows)
    swatches = ["#5AF0B3","#FFB95F","#FFCAC5","#34D399","#60A5FA",
                "#F87171","#A78BFA","#FBBF24","#FB923C","#1565C0","#6A1B9A","#37474F"]
    sx2, sw_y = 28, card_y+208
    selected = "#60A5FA"
    for i, sc in enumerate(swatches):
        sr = rgb(sc)
        d.ellipse([sx2, sw_y, sx2+24, sw_y+24], fill=sr)
        if sc == selected:
            d.ellipse([sx2-2, sw_y-2, sx2+26, sw_y+26], outline=ON_SURFACE, width=2)
        sx2 += 30
        if i == 5:
            sx2, sw_y = 28, sw_y + 32

    img.save(os.path.join(OUT, "07_settings_add.png"))
    print("07_settings_add.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN 8 — About
# ═══════════════════════════════════════════════════════════════════════════════
def screen_about():
    img = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(img)
    toolbar(d, "About")

    ic_cx, ic_cy = W//2, 180
    d.ellipse([ic_cx-40, ic_cy-40, ic_cx+40, ic_cy+40], fill=SURFACE_HIGH)
    d.arc([ic_cx-24, ic_cy-28, ic_cx+24, ic_cy+20], 0, 360, fill=PRIMARY, width=4)
    d.line([ic_cx, ic_cy-4, ic_cx, ic_cy-20], fill=PRIMARY, width=3)
    d.line([ic_cx, ic_cy-4, ic_cx+14, ic_cy+6], fill=PRIMARY, width=3)

    cw(d, "TEMPORAL",                              238, sg(28),  PRIMARY)
    cw(d, "Version 1.4.0",                         278, mn(13),  OUTLINE)
    cw(d, "Full-screen countdown for presenters",  302, mn(13),  ON_SURFACE_VAR)

    d.rectangle([W//2-24, 334, W//2+24, 336], fill=OUTLINE_VAR)
    cw(d, "DEVELOPED BY", 352, mnb(10), OUTLINE)

    def dev_card(y, initials, name, role, dot_color):
        d.rounded_rectangle([16, y, W-16, y+72], radius=12, fill=SURFACE_HIGH)
        d.ellipse([30, y+14, 74, y+58], fill=dot_color)
        at(d, initials, 52, y+24, sg(15), BG_DARK, anchor="ma")
        at(d, name,  86, y+14, mnb(15), ON_SURFACE)
        at(d, role,  86, y+38, mn(12),  OUTLINE)

    dev_card(374, "PV", "Pedro Vieira", "App Developer",                        PRIMARY)
    dev_card(456, "AI", "Claude.ai",    "AI Development Partner · Anthropic",   rgb("#CC785C"))

    cw(d, "pedrov.org",              546, mnb(14), PRIMARY)
    cw(d, "Open Source · MIT License", 574, mn(12), OUTLINE)
    cw(d, "© 2025 Pedro Vieira",     596, mn(12), OUTLINE)

    img.save(os.path.join(OUT, "08_about.png"))
    print("08_about.png")

# ── Run all ───────────────────────────────────────────────────────────────────
screen_setup()
screen_running(PRIMARY,   "ON TRACK",             "18:24", 68, "02_green.png")
screen_running(SECONDARY, "HURRY UP!",             "06:10", 37, "03_yellow.png")
screen_running(TERTIARY,  "ALMOST OUT OF TIME!",   "01:42", 12, "04_red.png", paused=False)
screen_running(SECONDARY, "HURRY UP!",             "06:10", 37, "03b_paused.png", paused=True)
screen_finished()
screen_settings()
screen_settings_add()
screen_about()
print("\nDone — screenshots in docs/screenshots/")
