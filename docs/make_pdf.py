#!/usr/bin/env python3
"""Convert USER_MANUAL.md to USER_MANUAL.pdf via weasyprint."""

import os, re, base64

DOCS = os.path.dirname(os.path.abspath(__file__))

# ── Read markdown ────────────────────────────────────────────────────────────
with open(os.path.join(DOCS, "USER_MANUAL.md"), encoding="utf-8") as f:
    md = f.read()

# ── Minimal markdown → HTML converter ────────────────────────────────────────
def md_to_html(text):
    lines = text.split("\n")
    html_lines = []
    in_table = False
    in_code = False
    in_ul = False
    ol_counter = {}

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
            # Separator row
            if all(re.match(r'^[-: ]+$', c) for c in cells):
                i += 1
                continue
            # Header vs body: check if next line is separator
            next_is_sep = (i + 1 < len(lines) and "|" in lines[i+1] and
                           all(re.match(r'^[-: ]+$', c.strip())
                               for c in lines[i+1].strip().strip("|").split("|")))
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
            html_lines.append("<p></p>")
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

        # Paragraph
        flush_ul()
        html_lines.append(f"<p>{inline(line)}</p>")
        i += 1

    if in_table:
        html_lines.append("</table>")
    flush_ul()
    if in_code:
        html_lines.append("</code></pre>")
    return "\n".join(html_lines)

def inline(text):
    # Images with local path → embed as base64
    def embed_img(m):
        alt, src, w = m.group(1), m.group(2), m.group(3) or "200"
        path = os.path.join(DOCS, src)
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{data}" width="{w}" alt="{alt}" style="border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.2);">'
        return m.group(0)

    text = re.sub(r'<img src="(screenshots/[^"]+)" width="(\d+)" alt="([^"]*)">',
                  lambda m: embed_img(type('M', (), {'group': lambda self, n: [None, m.group(3), m.group(1), m.group(2)][n]})()),
                  text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)(?:\{width=(\d+)\})?',
                  lambda m: embed_img(m), text)

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

# ── CSS ─────────────────────────────────────────────────────────────────────
css = """
@page {
    size: A4;
    margin: 2cm 2.2cm 2.4cm 2.2cm;
}
body {
    font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.65;
    color: #212121;
}
h1 { font-size: 22pt; color: #1b5e20; border-bottom: 3px solid #2e7d32; padding-bottom: 6pt; margin-top: 0; }
h2 { font-size: 15pt; color: #2e7d32; border-bottom: 1px solid #a5d6a7; padding-bottom: 3pt; margin-top: 24pt; }
h3 { font-size: 12pt; color: #37474f; margin-top: 18pt; }
h4 { font-size: 11pt; color: #546e7a; }
code {
    background: #f5f5f5;
    border: 1px solid #e0e0e0;
    border-radius: 3px;
    padding: 1px 5px;
    font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
    font-size: 9pt;
}
pre {
    background: #263238;
    color: #cfd8dc;
    border-radius: 6px;
    padding: 12px 16px;
    overflow: auto;
    font-size: 9pt;
    line-height: 1.5;
}
pre code {
    background: none;
    border: none;
    padding: 0;
    color: inherit;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 12pt 0;
    font-size: 10pt;
}
th {
    background: #2e7d32;
    color: white;
    padding: 7pt 10pt;
    text-align: left;
    font-weight: bold;
}
td {
    padding: 6pt 10pt;
    border-bottom: 1px solid #e0e0e0;
    vertical-align: top;
}
tr:nth-child(even) td { background: #f9fbe7; }
blockquote {
    border-left: 4px solid #a5d6a7;
    background: #f1f8e9;
    margin: 12pt 0;
    padding: 8pt 14pt;
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: #37474f;
}
hr { border: none; border-top: 1px solid #e0e0e0; margin: 18pt 0; }
ul, ol { padding-left: 20pt; }
li { margin-bottom: 4pt; }
img { display: block; margin: 12pt auto; }
a { color: #2e7d32; }
p { margin: 6pt 0; }
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

# Write HTML (useful for debugging)
html_path = os.path.join(DOCS, "USER_MANUAL.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

# Generate PDF
from weasyprint import HTML as WP
pdf_path = os.path.join(DOCS, "USER_MANUAL.pdf")
WP(string=html, base_url=DOCS).write_pdf(pdf_path)
print(f"PDF written to {pdf_path}")
