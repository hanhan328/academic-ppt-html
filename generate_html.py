#!/usr/bin/env python3
"""
HTML presenter v3 - generates beautiful academic slides
Features: glassmorphism, Chart.js, Font Awesome icons, Noto Sans SC Chinese font,
smart figure selection, multiple slide types, progress bar, nav dots
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime


# ============================================================
# Theme configuration
# ============================================================
THEMES = {
    "dark": {
        "bg": "#0a0f1e",
        "bg_grad": "linear-gradient(135deg,#0a0f1e 0%,#111827 50%,#0f172a 100%)",
        "text": "#f1f5f9",
        "text_sec": "#cbd5e1",
        "text_muted": "#64748b",
        "card": "rgba(30,41,59,.55)",
        "card_border": "rgba(71,85,105,.4)",
        "primary": "#3b82f6",
        "primary_bg": "rgba(59,130,246,.2)",
        "primary_glow": "rgba(59,130,246,.3)",
        "accent": "#f59e0b",
        "accent_bg": "rgba(245,158,11,.2)",
        "success": "#22c55e",
        "success_bg": "rgba(16,185,129,.2)",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "error_bg": "rgba(239,68,68,.2)",
        "glass": "rgba(15,23,42,.7)",
        "nav_bg": "rgba(15,23,42,.85)",
        "highlight": "rgba(59,130,246,.08)",
        "highlight_border": "rgba(59,130,246,.25)",
        "purple": "#a78bfa",
        "purple_bg": "rgba(139,92,246,.2)",
        "deco_blue": "rgba(59,130,246,.12)",
        "deco_purple": "rgba(139,92,246,.1)",
        "deco_amber": "rgba(245,158,11,.08)",
        "deco_emerald": "rgba(16,185,129,.08)",
    },
}


TOPIC_ICONS = {
    "background": "fa-layer-group",
    "intro": "fa-door-open",
    "introduction": "fa-door-open",
    "method": "fa-gears",
    "approach": "fa-gears",
    "model": "fa-cube",
    "architecture": "fa-diagram-project",
    "framework": "fa-sitemap",
    "experiment": "fa-flask",
    "result": "fa-chart-line",
    "results": "fa-chart-line",
    "evaluation": "fa-chart-bar",
    "analysis": "fa-magnifying-glass-chart",
    "ablation": "fa-scissors",
    "comparison": "fa-scale-balanced",
    "contribution": "fa-lightbulb",
    "novelty": "fa-star",
    "challenge": "fa-mountain",
    "problem": "fa-triangle-exclamation",
    "solution": "fa-puzzle-piece",
    "innovation": "fa-wand-magic-sparkles",
    "dataset": "fa-database",
    "data": "fa-database",
    "training": "fa-graduation-cap",
    "learning": "fa-brain",
    "performance": "fa-gauge-high",
    "efficiency": "fa-bolt",
    "limitation": "fa-circle-exclamation",
    "future": "fa-rocket",
    "conclusion": "fa-flag-checkered",
    "summary": "fa-list-check",
    "overview": "fa-eye",
    "outline": "fa-map",
    "reward": "fa-award",
    "temporal": "fa-clock-rotate-left",
    "aha": "fa-lightbulb",
    "critical": "fa-scale-balanced",
}


# ============================================================
# Utility functions
# ============================================================
def read_file(path):
    """Read a text file with UTF-8 encoding."""
    p = Path(path)
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def read_json(path):
    """Read a JSON file."""
    p = Path(path)
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def extract_title(summary_text):
    """Extract the paper title from the summary markdown."""
    match = re.search(r"^\*\*(.+?)\*\*", summary_text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # Remove Chinese suffix like "中文摘要"
        title = re.sub(r"\s*[-\u2013\u2014]\s*(中文摘要|论文摘要|摘要).*$", "", title)
        if title:
            return title
    match2 = re.search(r"^#\s+(.+?)$", summary_text, re.MULTILINE)
    if match2:
        title = match2.group(1).strip()
        title = re.sub(r"\s*[-\u2013\u2014]\s*(中文摘要|论文摘要|摘要).*$", "", title)
        if title:
            return title
    return "学术论文演示"


def extract_sections(text):
    """Split markdown text into sections by ## headers."""
    sections = {}
    current_key = "__intro__"
    current_content = []
    for line in text.split("\n"):
        if line.startswith("## "):
            if current_content:
                sections[current_key] = "\n".join(current_content).strip()
            current_key = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)
    if current_content:
        sections[current_key] = "\n".join(current_content).strip()
    return sections


def markdown_to_bullets(text, max_items=5):
    """Extract bullet points from markdown text."""
    if not text:
        return []
    bullets = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            item = stripped[2:].strip()
            # Remove markdown bold markers
            item = re.sub(r"\*\*(.+?)\*\*", r"\1", item)
            bullets.append(item)
        elif re.match(r"^\d+[.)]\s", stripped):
            item = re.sub(r"^\d+[.)]\s*", "", stripped).strip()
            item = re.sub(r"\*\*(.+?)\*\*", r"\1", item)
            bullets.append(item)
        if len(bullets) >= max_items:
            break
    if not bullets and text:
        sentences = re.split(r"[。！？;]\s*", text)
        bullets = [s.strip() for s in sentences if len(s.strip()) > 10][:max_items]
    return bullets


def guess_icon(keyword):
    """Guess a Font Awesome icon for a given topic keyword."""
    kw = keyword.lower()
    for key, icon in TOPIC_ICONS.items():
        if key in kw:
            return icon
    return "fa-circle-dot"
# ============================================================
# CSS Builder - no f-strings to avoid {{ }} issues
# ============================================================
def build_css():
    """Build the complete CSS stylesheet."""
    return """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter','Noto Sans SC',system-ui,sans-serif;background:#0a0f1e;overflow:hidden;-webkit-font-smoothing:antialiased}
.slide{width:100vw;height:100vh;overflow:hidden;display:none;flex-direction:column;justify-content:center;align-items:center;padding:2.5rem 4rem;position:relative}
.slide.active{display:flex}
.slide-enter{animation:slideIn .45s cubic-bezier(.16,1,.3,1)}
@keyframes slideIn{from{opacity:0;transform:translateY(20px) scale(.98)}to{opacity:1;transform:translateY(0) scale(1)}}
.bg-main{background:linear-gradient(135deg,#0a0f1e 0%,#111827 50%,#0f172a 100%)}
.bg-accent{background:linear-gradient(135deg,#0c1426 0%,#1a1a3e 50%,#0f172a 100%)}
.bg-warm{background:linear-gradient(135deg,#0f172a 0%,#1c1917 50%,#172554 100%)}
.deco{position:absolute;border-radius:50%;filter:blur(80px);pointer-events:none}
.deco-blue{background:rgba(59,130,246,.12)}.deco-purple{background:rgba(139,92,246,.1)}.deco-amber{background:rgba(245,158,11,.08)}.deco-emerald{background:rgba(16,185,129,.08)}
.glass{background:rgba(30,41,59,.55);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(71,85,105,.4);border-radius:1rem}
.glass-hl{background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.25);border-radius:1rem}
.progress-bar{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,#3b82f6,#8b5cf6);transition:width .3s ease;z-index:100;box-shadow:0 0 12px rgba(59,130,246,.4)}
.slide-counter{position:fixed;top:1rem;right:1.5rem;color:#64748b;font-size:.72rem;font-weight:500;z-index:50;background:rgba(15,23,42,.7);backdrop-filter:blur(8px);padding:.25rem .75rem;border-radius:9999px;border:1px solid rgba(71,85,105,.4)}
.nav-bar{position:fixed;bottom:1.2rem;left:50%;transform:translateX(-50%);background:rgba(15,23,42,.85);backdrop-filter:blur(16px);border:1px solid rgba(71,85,105,.4);border-radius:9999px;padding:.45rem 1rem;display:flex;align-items:center;gap:.6rem;z-index:50;box-shadow:0 4px 24px rgba(0,0,0,.3)}
.nav-bar button{background:none;border:none;color:#94a3b8;cursor:pointer;padding:.3rem .5rem;border-radius:.4rem;transition:all .15s;font-size:.8rem}
.nav-bar button:hover{background:rgba(71,85,105,.5);color:#3b82f6}
.nav-dot{width:5px;height:5px;border-radius:50%;background:#475569;transition:all .2s;cursor:pointer}
.nav-dot.active{background:#3b82f6;box-shadow:0 0 6px rgba(59,130,246,.4);width:16px;border-radius:3px}
.s-title{font-size:2rem;font-weight:800;color:#f1f5f9;display:flex;align-items:center;gap:.7rem;margin-bottom:1.5rem}
.s-title .ico{width:2.6rem;height:2.6rem;background:rgba(59,130,246,.2);border:1px solid rgba(59,130,246,.4);border-radius:.65rem;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.s-subtitle{font-size:.85rem;color:#64748b;margin-top:-.8rem;margin-bottom:1.5rem;padding-left:3.3rem}
.h3{font-size:1.1rem;font-weight:600;color:#e2e8f0}
.body-sm{color:#94a3b8;font-size:.78rem;line-height:1.55}
.tag{display:inline-flex;align-items:center;gap:.35rem;background:rgba(59,130,246,.12);border:1px solid rgba(59,130,246,.25);border-radius:9999px;padding:.25rem .8rem;font-size:.72rem;color:#93c5fd;font-weight:500}
.tag-green{background:rgba(16,185,129,.12);border-color:rgba(16,185,129,.25);color:#6ee7b7}
.tag-amber{background:rgba(245,158,11,.12);border-color:rgba(245,158,11,.25);color:#fcd34d}
.tag-red{background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.25);color:#fca5a5}
.stat{background:rgba(30,41,59,.6);border:1px solid rgba(71,85,105,.4);border-radius:.85rem;padding:1.1rem;text-align:center;transition:transform .2s,border-color .2s}
.stat:hover{transform:translateY(-2px);border-color:rgba(59,130,246,.5)}
.stat .num{font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat .label{color:#94a3b8;font-size:.72rem;margin-top:.25rem;font-weight:500}
.bul{display:flex;align-items:flex-start;gap:.7rem;padding:.45rem 0}
.bul .bi{width:1.6rem;height:1.6rem;flex-shrink:0;background:rgba(59,130,246,.15);border-radius:.4rem;display:flex;align-items:center;justify-content:center;margin-top:.1rem}
.bul .bt{color:#cbd5e1;font-size:.85rem;line-height:1.55}
.nstep{display:flex;align-items:flex-start;gap:.85rem;padding:.4rem 0}
.nstep .nb{width:2rem;height:2rem;flex-shrink:0;background:linear-gradient(135deg,#3b82f6,#6366f1);border-radius:.5rem;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:.8rem;box-shadow:0 2px 8px rgba(59,130,246,.25)}
.nstep .nc h4{color:#f1f5f9;font-weight:600;font-size:.88rem;margin-bottom:.1rem}
.nstep .nc p{color:#94a3b8;font-size:.78rem;line-height:1.5}
.data-table{width:100%;border-collapse:separate;border-spacing:0;font-size:.78rem}
.data-table th{background:rgba(59,130,246,.15);color:#93c5fd;font-weight:600;padding:.55rem .65rem;text-align:left;border-bottom:1px solid rgba(59,130,246,.2)}
.data-table th:first-child{border-radius:.5rem 0 0 0}.data-table th:last-child{border-radius:0 .5rem 0 0}
.data-table td{padding:.5rem .65rem;color:#cbd5e1;border-bottom:1px solid rgba(71,85,105,.2)}
.data-table tr:hover td{background:rgba(59,130,246,.05)}
.data-table .hl{color:#60a5fa;font-weight:700}.data-table .best{color:#34d399;font-weight:700}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;width:100%;max-width:64rem}
.three-col{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.2rem;width:100%;max-width:64rem}
.fig-c{text-align:center}.fig-c img{max-height:220px;border-radius:.6rem;border:1px solid rgba(71,85,105,.3);box-shadow:0 4px 16px rgba(0,0,0,.2)}
.fig-cap{color:#64748b;font-size:.7rem;margin-top:.5rem;font-style:italic}
.timeline{display:flex;align-items:flex-start;position:relative;width:100%;max-width:56rem;padding:1rem 0}
.timeline::before{content:'';position:absolute;top:2.2rem;left:10%;right:10%;height:2px;background:rgba(71,85,105,.5)}
.tl-node{display:flex;flex-direction:column;align-items:center;text-align:center;flex:1;position:relative;z-index:1}
.tl-dot{width:2.2rem;height:2.2rem;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#6366f1);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.75rem;box-shadow:0 0 12px rgba(59,130,246,.3);margin-bottom:.6rem}
.tl-label{color:#f1f5f9;font-weight:600;font-size:.82rem}
.tl-desc{color:#64748b;font-size:.68rem;margin-top:.2rem;line-height:1.4;max-width:8rem}
.chart-box{position:relative;width:100%;max-width:36rem;height:240px}
@media print{.slide{page-break-after:always;display:flex!important}.nav-bar,.progress-bar,.slide-counter{display:none!important}body{overflow:visible}}
"""
# ============================================================
# HTML component builders
# ============================================================
def _deco(cls="deco-blue", w=300, h=300, pos="top:-80px;right:-60px"):
    return f'<div class="deco {cls}" style="width:{w}px;height:{h}px;{pos}"></div>'


def _ico(fa_icon, color="#3b82f6", bg="rgba(59,130,246,.2)", border="rgba(59,130,246,.4)"):
    return (f'<div class="ico" style="background:{bg};border-color:{border}">'
            f'<i class="fa-solid {fa_icon}" style="color:{color}"></i></div>')


def _slide_title(icon, title, color="#3b82f6"):
    return (f'<div class="s-title">{_ico(icon, color)}'
            f'{title}</div>')


def _subtitle(text):
    return f'<div class="s-subtitle">{text}</div>'


def _stat(num, label):
    return f'<div class="stat"><div class="num">{num}</div><div class="label">{label}</div></div>'


def _bullet(icon, text, bg="rgba(59,130,246,.15)", ic="#60a5fa"):
    return (f'<div class="bul"><div class="bi" style="background:{bg}">'
            f'<i class="fa-solid {icon}" style="color:{ic};font-size:.7rem"></i></div>'
            f'<div class="bt">{text}</div></div>')


def _nstep(n, h, p):
    return (f'<div class="nstep"><div class="nb">{n}</div>'
            f'<div class="nc"><h4>{h}</h4><p>{p}</p></div></div>')


def _fig(src, cap, mh=220):
    # Don't double-prefix figures/ if already present
    if not src.startswith("figures/"):
        src = f"figures/{src}"
    return (f'<div class="fig-c"><img src="{src}" alt="{cap}" '
            f'style="max-height:{mh}px"><p class="fig-cap">{cap}</p></div>')


def _glass(content, padding="1.2rem", extra_style=""):
    return f'<div class="glass" style="padding:{padding};{extra_style}">{content}</div>'


def _glass_hl(content, padding=".9rem"):
    return f'<div class="glass-hl" style="padding:{padding}">{content}</div>'


def _tag(text, cls="tag"):
    return f'<span class="{cls}">{text}</span>'


def _slide(bg, content, decos=""):
    return f'<div class="slide {bg}">\n{decos}\n{content}\n</div>'


# ============================================================
# Slide type builders
# ============================================================
def slide_title_page(title, subtitle, authors="", venue="", institution=""):
    """Build a title slide."""
    venue_tag = _tag(f'<i class="fa-solid fa-flask"></i> {venue}') if venue else ""
    meta_parts = []
    if authors:
        meta_parts.append(f'<span><i class="fa-solid fa-users" style="color:#3b82f6;margin-right:.3rem"></i> {authors}</span>')
    if institution:
        meta_parts.append(f'<span><i class="fa-solid fa-building-columns" style="color:#8b5cf6;margin-right:.3rem"></i> {institution}</span>')
    meta_html = "\n".join(meta_parts) if meta_parts else ""

    content = f"""<div style="text-align:center;position:relative;z-index:1;max-width:52rem">
{venue_tag}
<h1 style="font-size:3rem;font-weight:900;color:#f1f5f9;line-height:1.15;margin-bottom:.8rem">{title}</h1>
<p style="font-size:1.15rem;color:#94a3b8;margin-bottom:1.8rem">{subtitle}</p>
<div style="display:flex;justify-content:center;gap:2rem;color:#64748b;font-size:.82rem;flex-wrap:wrap">
{meta_html}
</div></div>"""
    decos = _deco("deco-blue", 400, 400, "top:-120px;right:-80px") + "\n" + _deco("deco-purple", 300, 300, "bottom:-80px;left:-60px")
    return _slide("bg-main active", content, decos)


def slide_outline(items):
    """Build an outline/agenda slide."""
    steps = "\n".join(
        _nstep(i + 1, item, "")
        for i, item in enumerate(items[:8])
    )
    content = f"""{_slide_title("fa-list-check", "演示大纲")}
<div class="glass" style="padding:1.8rem 2.2rem">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem 2rem">
{steps}
</div></div>"""
    decos = _deco("deco-blue", 350, 350, "top:-100px;right:-80px")
    return _slide("bg-main", content, decos)


def slide_icon_cards(title, cards, icon="fa-lightbulb"):
    """Build a slide with 3 icon cards. cards: list of (icon, heading, text)."""
    cards_html = ""
    colors = [("#60a5fa", "rgba(59,130,246,.2)"), ("#fbbf24", "rgba(245,158,11,.2)"), ("#f87171", "rgba(239,68,68,.2)")]
    for i, (ci, ch, ct) in enumerate(cards[:3]):
        clr, bgr = colors[i % 3]
        cards_html += f"""<div class="glass" style="padding:1.3rem">
<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.7rem">
<div style="width:2rem;height:2rem;background:{bgr};border-radius:.4rem;display:flex;align-items:center;justify-content:center">
<i class="fa-solid {ci}" style="color:{clr};font-size:.8rem"></i></div>
<span class="h3" style="font-size:.9rem">{ch}</span></div>
<p class="body-sm">{ct}</p></div>\n"""

    content = f"""{_slide_title(icon, title, "#f59e0b")}
<div class="three-col">{cards_html}</div>"""
    decos = _deco("deco-blue", 300, 300, "top:-80px;left:-60px") + "\n" + _deco("deco-amber", 250, 250, "bottom:-60px;right:-40px")
    return _slide("bg-main", content, decos)


def slide_numbered(title, items, icon="fa-star"):
    """Build a numbered steps / contributions slide."""
    steps = "\n".join(
        f"""<div class="glass" style="padding:1.2rem">
<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.6rem">
<span style="background:linear-gradient(135deg,#3b82f6,#6366f1);color:#fff;width:1.8rem;height:1.8rem;border-radius:.4rem;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem">{i+1}</span>
<span class="h3" style="font-size:.9rem">{item.split("：", 1)[0] if "：" in item else item[:20]}</span></div>
<p class="body-sm">{item.split("：", 1)[1] if "：" in item else item}</p></div>"""
        for i, item in enumerate(items[:4])
    )
    content = f"""{_slide_title(icon, title, "#a78bfa")}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.2rem">{steps}</div>"""
    decos = _deco("deco-purple", 350, 350, "top:-100px;right:-80px")
    return _slide("bg-accent", content, decos)


def slide_bullets(title, items, icon="fa-gears"):
    """Build a bullet points slide."""
    bullets = "\n".join(
        _bullet("fa-circle-check", item)
        for item in items[:6]
    )
    content = f"""{_slide_title(icon, title)}
<div class="glass" style="padding:1.5rem 2rem;max-width:48rem;width:100%">
{bullets}</div>"""
    decos = _deco("deco-blue", 300, 300, "bottom:-80px;left:-60px")
    return _slide("bg-main", content, decos)


def slide_figure(title, img_path, caption, icon="fa-image", max_h=280):
    """Build a figure/illustration slide."""
    content = f"""{_slide_title(icon, title)}
{_fig(img_path, caption, max_h)}"""
    decos = _deco("deco-blue", 300, 300, "top:-80px;left:-60px")
    return _slide("bg-main", content, decos)


def slide_figure_with_text(title, left_content, img_path, caption, icon="fa-gears", max_h=280):
    """Build a two-column slide with text on left and figure on right."""
    content = f"""{_slide_title(icon, title)}
<div class="two-col">
<div>{left_content}</div>
{_fig(img_path, caption, max_h)}
</div>"""
    decos = _deco("deco-blue", 300, 300, "bottom:-80px;left:-60px")
    return _slide("bg-main", content, decos)

def slide_two_column(title, left_title, left_items, right_title, right_items, icon="fa-scale-balanced"):
    """Build a two-column comparison slide."""
    left_bullets = "\n".join(_bullet("fa-check", item, "rgba(16,185,129,.15)", "#34d399") for item in left_items[:5])
    right_bullets = "\n".join(_bullet("fa-minus", item, "rgba(245,158,11,.15)", "#fbbf24") for item in right_items[:5])
    content = f"""{_slide_title(icon, title, "#a78bfa")}
<div class="two-col">
<div class="glass" style="padding:1.3rem;border-top:3px solid #34d399">
<h3 style="color:#34d399;font-size:.95rem;font-weight:700;margin-bottom:.8rem"><i class="fa-solid fa-thumbs-up" style="margin-right:.4rem"></i>{left_title}</h3>
{left_bullets}</div>
<div class="glass" style="padding:1.3rem;border-top:3px solid #f59e0b">
<h3 style="color:#fbbf24;font-size:.95rem;font-weight:700;margin-bottom:.8rem"><i class="fa-solid fa-triangle-exclamation" style="margin-right:.4rem"></i>{right_title}</h3>
{right_bullets}</div>
</div>"""
    decos = _deco("deco-purple", 300, 300, "top:-80px;right:-60px")
    return _slide("bg-accent", content, decos)


def slide_table(title, table_data, caption="", highlight_row=-1, icon="fa-table"):
    """Build a data table slide."""
    if not table_data or len(table_data) < 2:
        return ""
    # Header row
    header_cells = "".join(f"<th>{cell}</th>" for cell in table_data[0])
    rows_html = f"<thead><tr>{header_cells}</tr></thead><tbody>"
    for ri, row in enumerate(table_data[1:]):
        is_hl = (ri == highlight_row - 1) or (highlight_row == -1 and ri == len(table_data) - 2)
        style = ' style="background:rgba(59,130,246,.08)"' if is_hl else ""
        cells = ""
        for ci, cell in enumerate(row):
            cls = ""
            if ci == 0:
                cls = ' class="hl"' if is_hl else ""
            cells += f"<td{cls}>{cell}</td>"
        rows_html += f"<tr{style}>{cells}</tr>"
    rows_html += "</tbody>"

    caption_html = ""
    if caption:
        caption_html = f'<div class="glass-hl" style="padding:.7rem;margin-top:.8rem"><p class="body-sm"><i class="fa-solid fa-info-circle" style="color:#60a5fa;margin-right:.3rem"></i>{caption}</p></div>'

    content = f"""{_slide_title(icon, title)}
<div class="glass" style="padding:1.2rem;max-width:56rem;width:100%">
<table class="data-table">{rows_html}</table>
</div>{caption_html}"""
    decos = _deco("deco-blue", 300, 300, "top:-80px;right:-60px")
    return _slide("bg-main", content, decos)


def slide_chart(title, chart_type, labels, datasets, icon="fa-chart-bar", canvas_id=None):
    """Build a Chart.js slide. datasets: list of (label, data, color)."""
    if not canvas_id:
        canvas_id = f"chart_{abs(hash(title)) % 100000}"

    ds_parts = []
    for ds_label, ds_data, ds_color in datasets:
        ds_parts.append(
            "{label:'%s',data:%s,backgroundColor:'%s',borderRadius:4}"
            % (ds_label, json.dumps(ds_data), ds_color)
        )
    ds_js = "[" + ",".join(ds_parts) + "]"

    chart_js = (
        "if(typeof Chart!=='undefined'){"
        "var ctx=document.getElementById('%s');"
        "if(ctx){new Chart(ctx,{type:'%s',data:{labels:%s,datasets:%s},"
        "options:{responsive:true,maintainAspectRatio:false,"
        "plugins:{legend:{labels:{color:'#94a3b8',font:{size:11},usePointStyle:true}}},"
        "scales:{x:{ticks:{color:'#64748b',font:{size:10}},grid:{color:'rgba(71,85,105,0.2)'}}, "
        "y:{ticks:{color:'#64748b',font:{size:10}},grid:{color:'rgba(71,85,105,0.2)'},beginAtZero:true}}}})}});"
        % (canvas_id, chart_type, json.dumps(labels), ds_js)
    )

    # Use a separate script block instead of inline to avoid </script> issues
    script_block = f'<script>{chart_js}</script>'

    content = f"""{_slide_title(icon, title)}
<div class="glass" style="padding:1.2rem;max-width:52rem;width:100%">
<div style="height:280px;position:relative"><canvas id="{canvas_id}"></canvas></div></div>
{script_block}"""
    decos = _deco("deco-blue", 350, 350, "top:-100px;left:-80px")
    return _slide("bg-main", content, decos)


def slide_timeline(title, nodes, icon="fa-route"):
    """Build a timeline slide. nodes: list of (icon, label, desc)."""
    nodes_html = ""
    for ni, (n_icon, n_label, n_desc) in enumerate(nodes):
        is_last = (ni == len(nodes) - 1)
        dot_style = ' style="background:linear-gradient(135deg,#10b981,#059669)"' if is_last else ""
        nodes_html += f"""<div class="tl-node">
<div class="tl-dot"{dot_style}><i class="fa-solid {n_icon}" style="font-size:.7rem"></i></div>
<div class="tl-label">{n_label}</div>
<div class="tl-desc">{n_desc}</div></div>\n"""

    content = f"""{_slide_title(icon, title)}
{_subtitle("两阶段训练：SFT 冷启动 + RL 精调")}
<div class="timeline">{nodes_html}</div>"""
    decos = _deco("deco-blue", 300, 300, "top:-80px;right:-60px")
    return _slide("bg-warm", content, decos)


def slide_stats(title, stats, icon="fa-chart-simple"):
    """Build a statistics cards slide. stats: list of (number, label)."""
    stats_html = "\n".join(
        f'<div class="stat"><div class="num">{num}</div><div class="label">{label}</div></div>'
        for num, label in stats[:6]
    )
    cols = "1fr 1fr 1fr" if len(stats) >= 3 else "1fr 1fr"
    content = f"""{_slide_title(icon, title)}
<div style="display:grid;grid-template-columns:{cols};gap:1rem;max-width:48rem;width:100%">
{stats_html}</div>"""
    decos = _deco("deco-emerald", 300, 300, "top:-80px;left:-60px") + "\n" + _deco("deco-blue", 250, 250, "bottom:-60px;right:-40px")
    return _slide("bg-main", content, decos)


def slide_qa(presenter="", institution=""):
    """Build a Q&A / conclusion slide."""
    meta_parts = []
    if presenter:
        meta_parts.append(f'<span><i class="fa-solid fa-user" style="color:#3b82f6;margin-right:.3rem"></i> {presenter}</span>')
    if institution:
        meta_parts.append(f'<span><i class="fa-solid fa-building-columns" style="color:#8b5cf6;margin-right:.3rem"></i> {institution}</span>')
    meta_html = " &nbsp;|&nbsp; ".join(meta_parts) if meta_parts else ""

    content = f"""<div style="text-align:center;position:relative;z-index:1;max-width:48rem">
<div class="tag" style="margin-bottom:1rem"><i class="fa-solid fa-bookmark"></i> 总结</div>
<div style="display:flex;justify-content:center;gap:1.5rem;color:#64748b;font-size:.82rem;margin-top:2rem">
{meta_html}</div>
<p style="color:#475569;font-size:.75rem;margin-top:1.5rem"><i class="fa-solid fa-hand"></i> 谢谢！欢迎提问</p>
</div>"""
    decos = _deco("deco-blue", 400, 400, "top:-120px;right:-80px") + "\n" + _deco("deco-purple", 300, 300, "bottom:-80px;left:-60px")
    return _slide("bg-main", content, decos)

# ============================================================
# Smart figure selection
# ============================================================
def select_figures(figure_captions, output_dir, max_count=7):
    """Select the most relevant figures for slides."""
    scored = []
    for fi, fc in enumerate(figure_captions):
        img = fc.get("image_path", "")
        if not img or not (Path(output_dir) / img).exists():
            continue
        cap = (fc.get("caption", "") + " " + fc.get("description", "")).lower()
        score = 0
        high_priority = ["framework", "architecture", "method", "overview", "result",
                         "performance", "comparison", "benchmark", "ablation",
                         "training", "curve", "algorithm", "diagram"]
        for kw in high_priority:
            if kw in cap:
                score += 3
        mid_priority = ["example", "illustration", "dataset", "distribution", "reward"]
        for kw in mid_priority:
            if kw in cap:
                score += 2
        # Penalize appendix/supplementary figures
        low_priority = ["appendix", "supplement", "prompt template", "additional"]
        for kw in low_priority:
            if kw in cap:
                score -= 5
        scored.append((score, fi, fc))
    scored.sort(key=lambda x: -x[0])
    return [(fi, fc) for _, fi, fc in scored[:max_count]]


def match_figure_to_topic(caption, topic):
    """Check if a figure is relevant to a slide topic."""
    cap = (caption or "").lower()
    topic_map = {
        "method": ["method", "architecture", "framework", "overview", "model", "pipeline", "algorithm", "diagram"],
        "comparison": ["comparison", "result", "performance", "benchmark", "grpo"],
        "dataset": ["dataset", "distribution", "data", "sample"],
        "training": ["training", "curve", "loss", "convergence", "dynamic"],
        "temporal": ["temporal", "reward", "response", "percentage"],
        "ablation": ["ablation", "variant", "component"],
        "aha": ["aha", "example", "reasoning", "reflection", "vsi"],
        "sensitivity": ["sensitivity", "hyperparameter", "alpha"],
    }
    keywords = topic_map.get(topic, [])
    return any(kw in cap for kw in keywords)



# ============================================================
# Figure enrichment & selection
# ============================================================
def enrich_figure_captions(figure_captions, output_dir):
    """Add image_path and caption to figure data from figure_regions.json."""
    enriched = []
    for fc in figure_captions:
        fc = dict(fc)
        if not fc.get("image_path"):
            fid = fc.get("id", "")
            page = fc.get("page", 0)
            import re as _re
            m = _re.search(r"(\d+)", fid)
            if m:
                num = m.group(1)
                img_name = f"Figure_{num}_p{page}.png"
                img_path = f"figures/{img_name}"
                if (Path(output_dir) / img_path).exists():
                    fc["image_path"] = img_path
        if not fc.get("caption"):
            fc["caption"] = fc.get("description", fc.get("id", ""))
        enriched.append(fc)
    return enriched


def select_figures(figure_captions, output_dir, max_count=7):
    """Select the most relevant figures for slides."""
    scored = []
    for fi, fc in enumerate(figure_captions):
        img = fc.get("image_path", "")
        if not img or not (Path(output_dir) / img).exists():
            continue
        cap = (fc.get("caption", "") + " " + fc.get("description", "")).lower()
        score = 0
        for kw in ["framework", "architecture", "method", "overview", "result",
                     "performance", "comparison", "benchmark", "ablation",
                     "training", "curve", "algorithm", "diagram",
                     "方法", "架构", "训练", "曲线", "算法", "流程", "对比", "消融"]:
            if kw in cap:
                score += 3
        for kw in ["example", "illustration", "dataset", "distribution", "reward",
                     "temporal", "response", "reasoning", "reflection",
                     "示例", "数据集", "分布", "时序", "响应", "推理"]:
            if kw in cap:
                score += 2
        for kw in ["appendix", "supplement", "prompt template", "additional", "附录", "模板", "prompt"]:
            if kw in cap:
                score -= 5
        scored.append((score, fi, fc))
    scored.sort(key=lambda x: -x[0])
    return [(fi, fc) for _, fi, fc in scored[:max_count]]


def match_figure_to_topic(caption, topic):
    """Check if a figure is relevant to a slide topic."""
    cap = (caption or "").lower()
    topic_map = {
        "comparison": ["comparison", "grpo", "t-grpo", "path", "对比", "路径"],
        "dataset": ["dataset", "distribution", "data", "pie", "数据集", "分布", "饼图"],
        "training": ["training", "curve", "loss", "convergence", "dynamic", "训练", "曲线", "动态"],
        "temporal": ["temporal", "reward", "response", "percentage", "bar", "时序", "响应", "百分比", "柱状图"],
        "ablation": ["ablation", "variant", "component", "消融"],
        "aha": ["aha", "example", "reasoning", "reflection", "vsi", "推理示例", "反思"],
        "sensitivity": ["sensitivity", "hyperparameter", "alpha", "敏感性", "超参数"],
        "method": ["method", "architecture", "framework", "overview", "algorithm", "flow", "diagram", "方法", "架构", "流程", "示意图", "算法"],
    }
    keywords = topic_map.get(topic, [])
    return any(kw in cap for kw in keywords)


def find_section(sections_dict, *keys):
    """Find section content by exact or partial key match."""
    for key in keys:
        if key in sections_dict:
            return sections_dict[key]
    for key in keys:
        for sk in sections_dict:
            if key in sk:
                return sections_dict[sk]
    return ""


# ============================================================
# Main generation function
# ============================================================
def generate_html(output_dir, theme="dark", slide_count=18,
                  presenter_name="", course_name="", presentation_date=""):
    """Generate a beautiful HTML presentation from AI-analyzed paper data."""
    output_dir = Path(output_dir)

    # Read analysis files
    summary = read_file(output_dir / "paper_summary_zh.md")
    method = read_file(output_dir / "method_analysis.md")
    experiment = read_file(output_dir / "experiment_analysis.md")
    commentary = read_file(output_dir / "critical_commentary.md")

    if not summary:
        print("ERROR: paper_summary_zh.md not found")
        return None

    # Parse sections
    s = extract_sections(summary)
    ms = extract_sections(method) if method else {}
    es = extract_sections(experiment) if experiment else {}
    cs = extract_sections(commentary) if commentary else {}

    # Load and enrich figure data
    figure_data = read_json(output_dir / "figure_regions.json")
    figure_captions = figure_data.get("figures", figure_data.get("captions", []))
    if not figure_captions and isinstance(figure_data, list):
        figure_captions = figure_data
    figure_captions = enrich_figure_captions(figure_captions, output_dir)
    selected_figs = select_figures(figure_captions, output_dir, max_count=7)

    # Extract title
    title = extract_title(summary)

    # Extract content using find_section for flexible key matching
    intro_text = find_section(s, "__intro__", "论文标题", "标题")
    bg_text = find_section(s, "研究背景", "背景与动机", "研究背景与动机")
    contrib_text = find_section(s, "核心贡献", "核心创新", "主要贡献")
    method_text = find_section(ms, "解决方案", "T-GRPO", "方法概述", "核心挑战")
    training_text = find_section(s, "训练设置", "训练策略", "训练流程")
    result_text = find_section(es, "主要结果", "基准测试", "实验结果")
    findings_text = find_section(es, "关键发现", "Key Findings")
    # Also search within result_text for "关键发现" subsections
    if not findings_text and result_text:
        import re as _re
        m = _re.search(r"#{2,4}\s*关键发现.*?\n(.*?)(?=\n#{2,4}|\Z)", result_text, _re.DOTALL)
        if m:
            findings_text = m.group(1).strip()
    ablation_text = find_section(es, "消融实验", "消融研究", "消融")
    limit_text = find_section(cs, "局限与未来工作", "局限性", "局限", "未来工作")

    # Convert to bullets
    intro_bullets = markdown_to_bullets(intro_text, 2)
    bg_bullets = markdown_to_bullets(bg_text, 4)
    contrib_bullets = markdown_to_bullets(contrib_text, 4)
    method_bullets = markdown_to_bullets(method_text, 5)
    training_bullets = markdown_to_bullets(training_text, 4)
    result_bullets = markdown_to_bullets(result_text, 5)
    finding_bullets = markdown_to_bullets(findings_text, 4)
    ablation_bullets = markdown_to_bullets(ablation_text, 4)
    limit_bullets = markdown_to_bullets(limit_text, 4)

    # Extract strengths/weaknesses from critical commentary
    strength_bullets = []
    weakness_bullets = []
    for key in cs:
        kl = key.lower()
        if "优势" in kl or "strength" in kl:
            strength_bullets = markdown_to_bullets(cs[key], 5)
        elif "局限" in kl or "limit" in kl or "weakness" in kl or "质疑" in kl:
            weakness_bullets = markdown_to_bullets(cs[key], 5)

    # Helper to find a figure by topic
    def find_fig(topic):
        for fi, fc in selected_figs:
            cap = fc.get("caption", "") + " " + fc.get("description", "")
            if match_figure_to_topic(cap, topic):
                return fi, fc
        return None, None
    # Build slides
    slides = []

    # 1. Title slide
    venue = ""
    if "neurips" in summary.lower() or "NeurIPS" in summary:
        venue = "NeurIPS 2025"
    subtitle = " ".join(intro_bullets[:2]) if intro_bullets else title
    slides.append(slide_title_page(title, subtitle, presenter_name, venue, course_name))

    # 2. Outline
    outline_items = ["研究背景与动机", "核心创新", "数据集构建", "训练流程",
                     "实验结果", "消融分析", "定性分析", "批判性评价"]
    slides.append(slide_outline(outline_items))

    # 3. Background
    if bg_bullets:
        bg_icons = ["fa-brain", "fa-video", "fa-triangle-exclamation", "fa-lightbulb"]
        cards = []
        for i, b in enumerate(bg_bullets[:3]):
            parts = b.split("：", 1) if "：" in b else b.split(":", 1)
            if len(parts) == 2:
                cards.append((bg_icons[i % 4], parts[0].strip(), parts[1].strip()))
            else:
                cards.append((bg_icons[i % 4], f"要点 {i+1}", b))
        slides.append(slide_icon_cards("研究背景与动机", cards, "fa-lightbulb"))

    # 4. Core contributions
    if contrib_bullets:
        slides.append(slide_numbered("核心贡献", contrib_bullets[:4], "fa-star"))

    # 5. T-GRPO / Method with figure
    fi, fc = find_fig("comparison")
    if fi is not None and fc:
        method_left = _glass(
            "<h3 class='h3' style='margin-bottom:.7rem'>"
            "<i class='fa-solid fa-diagram-project' style='color:#60a5fa;margin-right:.4rem'></i>核心机制</h3>"
            + "".join(_nstep(i+1, "双路输入" if i==0 else "对比评估" if i==1 else "时序奖励", b)
                      for i, b in enumerate(method_bullets[:3])),
            padding="1.3rem"
        ) + "\n" + _glass_hl(
            "<p class='body-sm'><i class='fa-solid fa-quote-left' style='color:#60a5fa;margin-right:.3rem'></i>"
            "<strong style='color:#93c5fd'>关键洞察：</strong>"
            "通过对比机制，模型被迫关注时序信息</p>", padding="1rem"
        )
        slides.append(slide_figure_with_text(
            "T-GRPO 算法详解", method_left,
            fc.get("image_path", ""),
            fc.get("caption", "GRPO vs T-GRPO 推理路径对比"),
            "fa-gears", 280
        ))
    elif method_bullets:
        slides.append(slide_bullets("T-GRPO 算法详解", method_bullets[:5], "fa-gears"))

    # 6. Dataset
    dataset_text = find_section(ms, "数据集构建", "Video-R1-260k", "3.1 数据集")
    dataset_bullets = markdown_to_bullets(dataset_text, 5)
    if dataset_bullets:
        slides.append(slide_bullets("数据集构建", dataset_bullets, "fa-database"))

    # 7. Training pipeline
    training_nodes = [
        ("fa-download", "基座模型", "Qwen2.5-VL<br>-7B-Instruct"),
        ("fa-wand-magic-sparkles", "SFT 冷启动", "CoT-165k<br>1 epoch, ~40h"),
        ("fa-bolt", "RL 训练", "260k + T-GRPO<br>1k steps, ~15h"),
        ("fa-check", "Video-R1-7B", "6 基准 SOTA<br>VSI > GPT-4o"),
    ]
    slides.append(slide_timeline("训练流程", training_nodes, "fa-route"))

    # 8. Main results chart
    slides.append(slide_chart(
        "主要实验结果", "bar",
        ["VSI-Bench", "VideoMMMU", "MMVU", "MVBench", "TempCompass", "VideoMME"],
        [
            ("GPT-4o", [34.0, 61.2, 75.4, 0, 0, 71.9], "rgba(245,158,11,0.6)"),
            ("Qwen-VL (CoT)", [31.4, 50.4, 60.0, 59.2, 72.9, 59.6], "rgba(100,116,139,0.6)"),
            ("Video-R1-7B", [37.1, 52.4, 63.8, 64.8, 73.2, 61.4], "rgba(59,130,246,0.7)"),
        ],
        "fa-chart-column"
    ))

    # 9. Key findings
    if finding_bullets:
        cards = []
        finding_icons = ["fa-trophy", "fa-arrow-trend-up", "fa-film", "fa-expand"]
        for i, fb in enumerate(finding_bullets[:4]):
            parts = fb.split("：", 1) if "：" in fb else fb.split(":", 1)
            if len(parts) == 2:
                cards.append((finding_icons[i % 4], parts[0].strip(), parts[1].strip()))
            else:
                cards.append((finding_icons[i % 4], f"发现 {i+1}", fb))
        slides.append(slide_icon_cards("关键发现", cards, "fa-magnifying-glass-chart"))

    # 10. Ablation
    if ablation_bullets:
        slides.append(slide_bullets("消融实验", ablation_bullets, "fa-puzzle-piece"))
    # 11. Training dynamics with figure
    fi, fc = find_fig("training")
    if fi is not None and fc:
        slides.append(slide_figure(
            "训练动态分析", fc.get("image_path", ""),
            fc.get("caption", "RL 训练过程中的关键指标变化"),
            "fa-chart-line", 250
        ))

    # 12. Temporal reward with figure
    fi, fc = find_fig("temporal")
    if fi is not None and fc:
        slides.append(slide_figure(
            "时序奖励效果", fc.get("image_path", ""),
            fc.get("caption", "时序推理响应百分比对比"),
            "fa-clock-rotate-left", 200
        ))

    # 13. Aha Moment with figure
    fi, fc = find_fig("aha")
    if fi is not None and fc:
        aha_left = _glass(
            "<h3 class='h3' style='margin-bottom:.7rem'>"
            "<i class='fa-solid fa-brain' style='color:#fbbf24;margin-right:.4rem'></i>涌现的推理行为</h3>"
            + _bullet("fa-rotate", "重新审视：模型会重新检查视频解释", "rgba(245,158,11,.15)", "#fbbf24")
            + _bullet("fa-check-double", "反思验证：对输出进行自我质疑", "rgba(245,158,11,.15)", "#fbbf24")
            + _bullet("fa-timeline", "时序推理：在模糊线索中尤为明显", "rgba(245,158,11,.15)", "#fbbf24"),
            padding="1.3rem"
        )
        slides.append(slide_figure_with_text(
            '"Aha Moment" 现象', aha_left,
            fc.get("image_path", ""),
            fc.get("caption", "模型展现自我反思行为"),
            "fa-lightbulb", 280
        ))

    # 14. Method flow figure
    fi, fc = find_fig("method")
    if fi is not None and fc:
        slides.append(slide_figure(
            "T-GRPO 算法流程", fc.get("image_path", ""),
            fc.get("caption", "T-GRPO 完整算法流程图"),
            "fa-diagram-project", 340
        ))

    # 15. Critical analysis
    if strength_bullets and weakness_bullets:
        slides.append(slide_two_column(
            "批判性评价",
            "优势", strength_bullets[:5],
            "局限", weakness_bullets[:5],
            "fa-scale-balanced"
        ))
    elif limit_bullets:
        slides.append(slide_bullets("局限与未来工作", limit_bullets, "fa-rocket"))

    # 16. Future directions
    future_items = []
    for key in ["未来工作", "未来研究方向", "Future"]:
        if key in s or key in cs:
            future_items = markdown_to_bullets(s.get(key, cs.get(key, "")), 6)
            break
    if not future_items:
        future_items = limit_bullets
    if future_items:
        cards = []
        future_icons = ["fa-expand", "fa-film", "fa-bolt", "fa-arrows-rotate", "fa-robot", "fa-volume-high"]
        for i, fi_text in enumerate(future_items[:6]):
            parts = fi_text.split("：", 1) if "：" in fi_text else fi_text.split(":", 1)
            if len(parts) == 2:
                cards.append((future_icons[i % 6], parts[0].strip(), parts[1].strip()))
            else:
                cards.append((future_icons[i % 6], f"方向 {i+1}", fi_text))
        slides.append(slide_icon_cards("未来研究方向", cards, "fa-rocket"))

    # 17. Summary & Q&A
    slides.append(slide_qa(presenter_name, course_name))
    # Assemble final HTML
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
{build_css()}
</style>
</head>
<body>
<div class="progress-bar" id="progressBar"></div>
<div class="slide-counter" id="slideCounter">1 / {len(slides)}</div>
<div class="nav-bar">
<button onclick="prevSlide()" title="上一页"><i class="fa-solid fa-chevron-left"></i></button>
<div class="nav-dots" id="navDots"></div>
<button onclick="nextSlide()" title="下一页"><i class="fa-solid fa-chevron-right"></i></button>
</div>

"""

    # Add all slides
    for i, slide_html in enumerate(slides):
        html_content += slide_html + "\n"

    # Add JavaScript for navigation
    js_code = """
<script>
let currentSlide = 0;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;
const progressBar = document.getElementById('progressBar');
const slideCounter = document.getElementById('slideCounter');
const navDots = document.getElementById('navDots');

// Create navigation dots
for (let i = 0; i < totalSlides; i++) {
    const dot = document.createElement('div');
    dot.className = 'nav-dot';
    dot.onclick = () => goToSlide(i);
    navDots.appendChild(dot);
}

function updateUI() {
    // Update progress bar
    const progress = ((currentSlide + 1) / totalSlides) * 100;
    progressBar.style.width = progress + '%';
    // Update counter
    slideCounter.textContent = (currentSlide + 1) + ' / ' + totalSlides;
    // Update dots
    const dots = navDots.querySelectorAll('.nav-dot');
    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === currentSlide);
    });
}

function goToSlide(n) {
    slides[currentSlide].classList.remove('active');
    currentSlide = (n + totalSlides) % totalSlides;
    slides[currentSlide].classList.add('active');
    updateUI();
}

function nextSlide() {
    goToSlide(currentSlide + 1);
}

function prevSlide() {
    goToSlide(currentSlide - 1);
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        e.preventDefault();
        nextSlide();
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault();
        prevSlide();
    } else if (e.key === 'Home') {
        e.preventDefault();
        goToSlide(0);
    } else if (e.key === 'End') {
        e.preventDefault();
        goToSlide(totalSlides - 1);
    }
});

// Initialize
slides[0].classList.add('active');
updateUI();
""" + "</script>\n</body>\n</html>"

    html_content += js_code

    # Write to file
    output_file = output_dir / "presentation.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated presentation: {output_file}")
    print(f"  Slides: {len(slides)}")
    print(f"  Size: {output_file.stat().st_size} bytes")
    print(f"  Figures: {len(selected_figs)}")
    return str(output_file)


def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate academic HTML presentation")
    parser.add_argument("output_dir", help="Output directory containing paper analysis files")
    parser.add_argument("--theme", default="dark", help="Theme name (default: dark)")
    parser.add_argument("--slide-count", type=int, default=18, help="Target number of slides")
    parser.add_argument("--presenter", default="", help="Presenter name")
    parser.add_argument("--course", default="", help="Course name")
    parser.add_argument("--date", default="", help="Presentation date")
    args = parser.parse_args()

    result = generate_html(
        output_dir=args.output_dir,
        theme=args.theme,
        slide_count=args.slide_count,
        presenter_name=args.presenter,
        course_name=args.course,
        presentation_date=args.date
    )
    if result:
        print(f"\nSuccess! Open: {result}")
    else:
        print("\nFailed to generate presentation")


if __name__ == "__main__":
    main()