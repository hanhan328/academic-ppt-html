#!/usr/bin/env python3
"""
Academic PPT HTML - 主运行脚本
完整流程: PDF 解析 -> 章节检测 -> HTML 演示

注意: 分析内容（摘要、评论、大纲等）由 AI 代理根据 SKILL.md 指引生成。
本脚本处理机械任务（PDF 解析、章节检测、HTML 渲染）。
"""

import sys
import json
from pathlib import Path
from datetime import datetime

from parse_pdf import parse_pdf
from detect_sections import detect_sections
from generate_html import generate_html


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("""
Academic PPT HTML - 学术论文 HTML 演示生成器

用法:
    python run.py <pdf_path> [选项]

选项:
    --output_dir DIR    输出目录 (默认: outputs/{paper_name}/)
    --theme THEME       主题: dark, light, tech, warm (默认: dark)
    --slides N          幻灯片数量 (默认: 14)
    --presenter NAME    汇报人姓名
    --course NAME       课程名称
    --date DATE         汇报日期

注意:
    本脚本完成 PDF 解析和 HTML 生成。分析内容（摘要、评论、大纲等）
    需要 AI 代理根据 SKILL.md 指引来完成。
    完整的端到端流程应在 AI 代理中通过触发 academic-ppt-html skill 来实现。

示例:
    python run.py paper.pdf --theme dark --slides 14
""")
        sys.exit(0)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"错误: PDF 文件不存在: {pdf_path}")
        sys.exit(1)

    output_dir = None
    theme = "dark"
    slide_count = 14
    presenter_name = ""
    course_name = ""
    presentation_date = ""

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output_dir":
            output_dir = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--theme":
            theme = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--slides":
            slide_count = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--presenter":
            presenter_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--course":
            course_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--date":
            presentation_date = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if not output_dir:
        paper_name = pdf_path.stem.replace(" ", "_").replace(".", "_")
        output_dir = Path("outputs") / paper_name

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Academic PPT HTML - 论文处理")
    print(f"PDF: {pdf_path.name}")
    print(f"输出: {output_dir}")
    print("=" * 60)

    # 阶段 1: PDF 解析
    print("\n[1/3] PDF 解析...")
    parsed = parse_pdf(str(pdf_path), str(output_dir / "parsed_paper.json"))
    title = parsed["metadata"]["title"]
    print(f"  标题: {title[:80]}")
    print(f"  页数: {parsed['extraction_report']['page_count']}")
    print(f"  [OK] parsed_paper.json")

    # 阶段 2: 章节检测
    print("\n[2/3] 章节检测...")
    structure = detect_sections(
        str(output_dir / "parsed_paper.json"),
        str(output_dir / "paper_structure.json")
    )
    for sec in structure["sections"]:
        print(f"  - {sec['normalized_type']} ({sec['confidence']})")
    print(f"  [OK] paper_structure.json")

    # 阶段 3: HTML 生成
    print("\n[3/3] HTML 演示生成...")
    html_path = generate_html(
        str(output_dir), theme, slide_count,
        presenter_name, course_name, presentation_date
    )
    print(f"  [OK] presentation.html")

    # 工作流清单
    manifest = {
        "paper_pdf_path": str(pdf_path),
        "output_dir": str(output_dir),
        "theme": theme,
        "slide_count": slide_count,
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "steps": {
            "pdf_parse": {"status": "completed", "output": "parsed_paper.json"},
            "section_detect": {"status": "completed", "output": "paper_structure.json"},
            "html_generate": {"status": "completed", "output": "presentation.html"}
        },
        "note": "分析内容（摘要、评论、大纲等）需由 AI 代理根据 SKILL.md 完成。"
    }

    with open(output_dir / "workflow_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"  [OK] workflow_manifest.json")

    print("\n" + "=" * 60)
    print("处理完成!")
    print(f"HTML 演示: {html_path}")
    print("\n提示: 分析文件（摘要、评论等）需通过 AI 代理生成。")
    print("在 AI 代理中使用 academic-ppt-html skill 可获得完整体验。")
    print("=" * 60)


if __name__ == "__main__":
    main()
