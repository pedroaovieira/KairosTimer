#!/usr/bin/env python3
"""Convert USER_MANUAL.md to USER_MANUAL.pdf via weasyprint."""

import os, re, base64, io
from PIL import Image as PILImage

DOCS = os.path.dirname(os.path.abspath(__file__))

# ── Read markdown ────────────────────────────────────────────────────────────
with open(os.path.join(DOCS, "USER_MANUAL.md"), encoding="utf-8") as f:
    md = f.read()

# ── Image embed helper ───────────────────────────────────────────────────────
# Phone screenshots are portrait (390×844). At 96 dpi, 1cm ≈ 37.8 px.
# We resize to MAX_IMG_PX wide so each image is ≤ ~4 cm — fits 3 side-by-side.
MAX_IMG_PX = 150          # for table cells
MAX_IMG_FLOAT_PX = 140   # for standalone floated screenshots

def embed_img_path(src, alt="", max_px=MAX_IMG_PX, css_class="screenshot"):
    path = os.path.join(DOCS, src)
    if not os.path.exists(path):
        return f'<img alt="{alt}">'
    img = PILImage.open(path).convert("RGB")
    if img.width > max_px:
        h = int(img.height * max_px / img.width)
        img = img.resize((max_px, h), PILImage.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    data = base64.b64encode(buf.getvalue()).decode()
    return (f'<img src="data:image/png;base64,{data}" alt="{alt}" '
            f'class="{css_class}">')

# ── Minimal markdown → HTML converter ────────────────────────────────────────
def md_to_html(text):
    lines = text.split("\n")
    html_lines = []
    in_table = False
    in_code = False
    in_ul = False

    def flush_ul():
        nonlocal in_ul
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code blocks
        if line.strip().startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                flush_ul()
                lang = line.strip()[3:]
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code = True
            i += 1
            continue
        if in_code:
            html_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            i += 1
            continue

        # Table
        if "|" in line and line.strip().startswith("|"):
            flush_ul()
            if not in_table:
                html_lines.append('<table>')
                in_table = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # Separator row — skip, but mark next rows as body
            if all(re.match(r'^[-: ]+$', c) for c in cells):
                i += 1
                continue
            next_is_sep = (i + 1 < len(lines) and "|" in lines[i + 1] and
                           all(re.match(r'^[-: ]+$', c.strip())
                               for c in lines[i + 1].strip().strip("|").split("|")))
            tag = "th" if next_is_sep else "td"
            row = "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells)
            html_lines.append(f"<tr>{row}</tr>")
            i += 1
            continue
        elif in_table:
            html_lines.append("</table>")
            in_table = False

        # Blank line
        if not line.strip():
            flush_ul()
            i += 1
            continue

        # Headings
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            flush_ul()
            level = len(m.group(1))
            slug = re.sub(r'[^a-z0-9-]', '', m.group(2).lower().replace(' ', '-'))
            html_lines.append(f'<h{level} id="{slug}">{inline(m.group(2))}</h{level}>')
            i += 1
            continue

        # HR
        if re.match(r'^---+$', line.strip()):
            flush_ul()
            html_lines.append("<hr>")
            i += 1
            continue

        # Blockquote
        if line.startswith(">"):
            flush_ul()
            html_lines.append(f'<blockquote>{inline(line[1:].strip())}</blockquote>')
            i += 1
            continue

        # Unordered list
        m = re.match(r'^[-*]\s+(.*)', line)
        if m:
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        # Ordered list
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            flush_ul()
            html_lines.append(f"<li>{inline(m.group(2))}</li>")
            i += 1
            continue

        # Paragraph — detect image-only lines → float right
        flush_ul()
        rendered = inline(line)
        stripped = rendered.strip()
        if stripped.startswith('<img ') and stripped.endswith('>') and stripped.count('<img ') == 1:
            # Solo screenshot: wrap in a float figure
            rendered = rendered.replace('class="screenshot"', 'class="screenshot screenshot-float"')
            html_lines.append(f'<figure class="screenshot-figure">{rendered}</figure>')
        else:
            html_lines.append(f"<p>{rendered}</p>")
        i += 1

    if in_table:
        html_lines.append("</table>")
    flush_ul()
    if in_code:
        html_lines.append("</code></pre>")
    return "\n".join(html_lines)


def inline(text):
    # HTML <img> tags  (e.g. from markdown raw HTML)
    def replace_html_img(m):
        src = m.group(1)
        alt = m.group(2) or ""
        if src.startswith("screenshots/"):
            return embed_img_path(src, alt, max_px=MAX_IMG_FLOAT_PX)
        return m.group(0)

    text = re.sub(
        r'<img\s+src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>',
        replace_html_img, text)
    text = re.sub(
        r'<img\s+alt="([^"]*)"[^>]*src="([^"]+)"[^>]*>',
        lambda m: replace_html_img(type('M', (), {
            'group': lambda self, n: [None, m.group(2), m.group(1)][n]
        })()), text)

    # Markdown ![]() images
    def replace_md_img(m):
        alt, src = m.group(1), m.group(2)
        if src.startswith("screenshots/"):
            return embed_img_path(src, alt, max_px=MAX_IMG_FLOAT_PX)
        return m.group(0)

    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_md_img, text)

    # Bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


body = md_to_html(md)

# ── CSS — Temporal Monolith brand ────────────────────────────────────────────
css = """
@page {
    size: A4;
    margin: 2cm 2.2cm 2.4cm 2.2cm;
}
body {
    font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.6;
    color: #1a1a1a;
}
h1 {
    font-size: 22pt; color: #0d0d0d;
    border-bottom: 3px solid #5AF0B3;
    padding-bottom: 6pt; margin-top: 0; margin-bottom: 4pt;
}
h2 {
    font-size: 15pt; color: #0d0d0d;
    border-bottom: 1px solid #5AF0B3;
    padding-bottom: 3pt; margin-top: 20pt; margin-bottom: 6pt;
}
h3 { font-size: 12pt; color: #2a2a2a; margin-top: 14pt; margin-bottom: 4pt; }
h4 { font-size: 11pt; color: #444444; margin-top: 10pt; margin-bottom: 2pt; }
p { margin: 4pt 0; }
code {
    background: #f4f4f4;
    border: 1px solid #ddd;
    border-radius: 3px;
    padding: 1px 5px;
    font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
    font-size: 9pt;
    color: #003825;
}
pre {
    background: #1a1a1a;
    color: #e5e2e1;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 9pt;
    line-height: 1.5;
    margin: 8pt 0;
    border-left: 3px solid #5AF0B3;
}
pre code { background: none; border: none; padding: 0; color: inherit; }

/* ── Tables ── */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 8pt 0;
    font-size: 10pt;
    table-layout: fixed;
}
th {
    background: #1a1a1a;
    color: #5AF0B3;
    padding: 5pt 8pt;
    text-align: left;
    font-weight: bold;
    font-size: 10pt;
    letter-spacing: 0.04em;
}
td {
    padding: 5pt 8pt;
    border-bottom: 1px solid #e8e8e8;
    vertical-align: top;
    word-wrap: break-word;
}
td:first-child { font-weight: 500; }
tr:nth-child(even) td { background: #f7faf8; }

/* ── Screenshots ── */
img.screenshot {
    display: block;
    margin: 4pt auto;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    max-width: 100%;
    height: auto;
}

/* Standalone floated screenshot */
figure.screenshot-figure {
    float: right;
    clear: right;
    margin: 0 0 10pt 16pt;
    padding: 0;
}
figure.screenshot-figure img.screenshot {
    margin: 0;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}

/* Clear floats after each major section */
h2, h3, h4 { clear: both; }
hr { clear: both; border: none; border-top: 1px solid #e0e0e0; margin: 14pt 0; }

blockquote {
    border-left: 4px solid #5AF0B3;
    background: #f4fdf8;
    margin: 8pt 0;
    padding: 6pt 12pt;
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: #2a2a2a;
    clear: both;
}
ul, ol { padding-left: 18pt; margin: 4pt 0; }
li { margin-bottom: 3pt; }
a { color: #003825; }
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>PresentationTimer — User Manual</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>"""

# Write HTML for inspection
with open(os.path.join(DOCS, "USER_MANUAL.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Generate PDF
from weasyprint import HTML as WP
pdf_path = os.path.join(DOCS, "USER_MANUAL.pdf")
WP(string=html, base_url=DOCS).write_pdf(pdf_path)
print(f"PDF written → {pdf_path}  ({os.path.getsize(pdf_path)//1024} KB)")
