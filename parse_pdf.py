#!/usr/bin/env python3
"""
PDF Parser - 学术论文 PDF 解析
提取文本、元数据、完整Figure渲染图、表格、参考文献
"""

import fitz  # PyMuPDF
import json
import re
from pathlib import Path
from datetime import datetime


def merge_nearby_rects(rects, x_gap=30, y_gap=20):
    """
    合并相邻/重叠的矩形区域，将属于同一张Figure的多个碎片合并。
    
    Args:
        rects: [(x0,y0,x1,y1), ...] 每个图片区域的bbox
        x_gap: 水平方向允许的最大间距
        y_gap: 垂直方向允许的最大间距
    
    Returns:
        合并后的矩形列表
    """
    if not rects:
        return []
    
    # 按 y 坐标排序，再按 x 坐标
    sorted_rects = sorted(rects, key=lambda r: (r[1], r[0]))
    
    merged = []
    current = list(sorted_rects[0])
    
    for rect in sorted_rects[1:]:
        rx0, ry0, rx1, ry1 = rect
        
        # 检查是否与当前合并区域重叠或相邻
        overlap_x = not (rx0 > current[2] + x_gap or rx1 < current[0] - x_gap)
        overlap_y = not (ry0 > current[3] + y_gap or ry1 < current[1] - y_gap)
        
        if overlap_x and overlap_y:
            # 合并
            current[0] = min(current[0], rx0)
            current[1] = min(current[1], ry0)
            current[2] = max(current[2], rx1)
            current[3] = max(current[3], ry1)
        else:
            merged.append(tuple(current))
            current = [rx0, ry0, rx1, ry1]
    
    merged.append(tuple(current))
    return merged


def parse_pdf(pdf_path: str, output_path: str = None, render_dpi: int = 250):
    """
    解析学术论文 PDF
    
    Args:
        pdf_path: PDF 文件路径
        output_path: 输出 JSON 路径
        render_dpi: 渲染Figure图片的DPI（默认200，越高越清晰）
    
    Returns:
        dict: 解析结果
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

    doc = fitz.open(pdf_path)
    page_count = len(doc)

    # 输出目录
    if output_path:
        base_dir = Path(output_path).parent
        figures_dir = base_dir / "figures"
    else:
        figures_dir = None

    if figures_dir:
        figures_dir.mkdir(parents=True, exist_ok=True)
        pages_dir = figures_dir / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)
    else:
        pages_dir = None

    # 提取元数据
    metadata = doc.metadata
    title = metadata.get("title", "")
    authors = metadata.get("author", "")

    # 收集数据
    pages = []
    full_text = ""
    figure_captions = []
    table_captions = []
    references = []
    extracted_figures = []  # 渲染后的完整Figure图

    figure_pattern = re.compile(
        r"(?:Figure|Fig\.|图)\s*(\d+|[A-Z])[:\.\s]*(.+?)(?=\n(?:Figure|Fig\.|图|Table|TABLE|表)|\n\n|$)",
        re.IGNORECASE
    )
    table_pattern = re.compile(
        r"(?:Table|TABLE|表)\s*(\d+|[IVX]+|[A-Z])[:\.\s]*(.+?)(?=\n(?:Figure|Fig\.|图|Table|TABLE|表)|\n\n|$)",
        re.IGNORECASE
    )
    ref_pattern = re.compile(r"(?:References|Bibliography|参考文献)", re.IGNORECASE)

    in_references = False
    figure_counter = 0

    for page_num in range(page_count):
        page = doc[page_num]
        text = page.get_text()
        full_text += text + "\n\n"

        page_data = {
            "page_number": page_num + 1,
            "text": text,
            "rendered_figures": [],
            "warnings": []
        }

        # Render full page for AI figure identification / fallback
        if pages_dir:
            try:
                pix_full = page.get_pixmap(dpi=150)
                full_filename = f"page_{page_num+1:02d}.png"
                pix_full.save(str(pages_dir / full_filename))
                page_data["full_page_image"] = f"figures/pages/{full_filename}"
            except Exception:
                page_data["full_page_image"] = ""

        # ====== 核心: 渲染完整Figure图 ======
        page_rendered_figures = []
        
        # 1. 获取页面上所有图片区域
        image_infos = page.get_image_info()
        
        # 2. 过滤: 排除太小的图片（图标、inline公式等），保留宽度>80pt且高度>80pt的
        large_images = []
        for img in image_infos:
            bbox = img["bbox"]
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            # Filter: min size 150x100pt, aspect ratio between 0.15 and 8
            if w > 150 and h > 100:
                ratio = w / max(h, 1)
                if 0.15 < ratio < 8:  # skip extremely thin/wide images
                    large_images.append((bbox[0], bbox[1], bbox[2], bbox[3]))
        
        # 3. 合并相邻区域（同一张Figure常被PDF切成多个碎片）
        if large_images:
            merged_regions = merge_nearby_rects(large_images, x_gap=30, y_gap=20)
        else:
            merged_regions = []
        
        # 4. 渲染每个合并后的区域为高清PNG
        for region_idx, (rx0, ry0, rx1, ry1) in enumerate(merged_regions):
            try:
                # 稍微扩大裁剪区域（加边距）
                margin = 15
                clip_rect = fitz.Rect(
                    max(0, rx0 - margin),
                    max(0, ry0 - margin),
                    min(page.rect.width, rx1 + margin),
                    min(page.rect.height, ry1 + margin)
                )
                
                pix = page.get_pixmap(clip=clip_rect, dpi=render_dpi)
                figure_counter += 1
                filename = f"figure_{figure_counter:02d}_p{page_num+1}.png"
                rel_path = f"figures/{filename}"
                
                if figures_dir:
                    pix.save(str(figures_dir / filename))
                
                page_rendered_figures.append({
                    "id": f"Figure_{figure_counter}",
                    "filename": filename,
                    "rel_path": rel_path,
                    "page": page_num + 1,
                    "bbox": [rx0, ry0, rx1, ry1],
                    "width_px": pix.width,
                    "height_px": pix.height,
                    "dpi": render_dpi
                })
            except Exception as e:
                page_data["warnings"].append(f"Figure render failed region {region_idx}: {e}")
        
        # 5. 如果页面没有检测到图片区域，但有 Figure caption，
        #    渲染整页作为备选（可能Figure是矢量图，无嵌入位图）
        if not page_rendered_figures:
            # 检查该页是否有 Figure caption
            has_fig_caption = figure_pattern.search(text) is not None
            if has_fig_caption:
                try:
                    pix = page.get_pixmap(dpi=render_dpi)
                    figure_counter += 1
                    filename = f"figure_{figure_counter:02d}_p{page_num+1}_full.png"
                    rel_path = f"figures/{filename}"
                    
                    if figures_dir:
                        pix.save(str(figures_dir / filename))
                    
                    page_rendered_figures.append({
                        "id": f"Figure_{figure_counter}",
                        "filename": filename,
                        "rel_path": rel_path,
                        "page": page_num + 1,
                        "bbox": [0, 0, page.rect.width, page.rect.height],
                        "width_px": pix.width,
                        "height_px": pix.height,
                        "dpi": render_dpi,
                        "note": "full_page_fallback"
                    })
                except Exception as e:
                    page_data["warnings"].append(f"Full page render failed: {e}")
        
        page_data["rendered_figures"] = page_rendered_figures
        extracted_figures.extend(page_rendered_figures)

        # ====== Figure/Table Caption 提取 ======
        for match in figure_pattern.finditer(text):
            fig_id = match.group(1)
            caption = match.group(2).strip()
            
            # 尝试匹配到渲染的Figure
            matched_img_path = ""
            caption_y = 0
            # 找到caption在页面上的位置
            caption_search = page.search_for(match.group(0)[:30])
            if caption_search:
                caption_y = caption_search[0].y0
            
            # 找该页最接近的渲染Figure（通常Figure在其caption上方）
            best_match = None
            best_dist = float("inf")
            for rf in page_rendered_figures:
                if rf["page"] == page_num + 1:
                    # Figure的底部应该靠近caption的顶部
                    fig_bottom = rf["bbox"][3]
                    dist = abs(caption_y - fig_bottom) if caption_y > 0 else 100
                    if dist < best_dist and dist < 400:  # 400pt 以内
                        best_dist = dist
                        best_match = rf
            
            if best_match:
                matched_img_path = best_match["rel_path"]
            
            figure_captions.append({
                "id": f"Figure {fig_id}",
                "caption": caption,
                "page": page_num + 1,
                "image_path": matched_img_path,
                "nearby_text": text[max(0, match.start()-100):min(len(text), match.end()+100)],
                "confidence": "high" if matched_img_path else "medium"
            })

        for match in table_pattern.finditer(text):
            table_id = match.group(1)
            caption = match.group(2).strip()
            table_captions.append({
                "id": f"Table {table_id}",
                "caption": caption,
                "page": page_num + 1,
                "nearby_text": text[max(0, match.start()-100):min(len(text), match.end()+100)],
                "confidence": "medium"
            })

        # ====== 表格检测 ======
        try:
            tabs = page.find_tables()
            if tabs and tabs.tables:
                for tab_idx, table in enumerate(tabs.tables):
                    tab_data = table.extract()
                    if tab_data and len(tab_data) > 1:
                        # 保存在 parsed json 中，不再单独文件
                        page_data.setdefault("detected_tables", []).append({
                            "index": tab_idx,
                            "data": tab_data,
                            "rows": len(tab_data),
                            "cols": len(tab_data[0]) if tab_data else 0
                        })
        except Exception:
            pass

        # ====== 参考文献 ======
        if ref_pattern.search(text):
            in_references = True

        if in_references:
            for line in text.split("\n"):
                if line.strip() and (re.match(r"^\[\d+\]", line) or re.match(r"^\d+\.", line) or len(line) > 30):
                    references.append({"index": len(references) + 1, "text": line.strip()})

        pages.append(page_data)

    # 提取摘要
    abstract_text = ""
    abstract_page = 1
    abstract_confidence = "low"

    for page_data in pages:
        text = page_data["text"]
        abs_match = re.search(
            r"(?:ABSTRACT|Abstract|摘要)[:\s]*(.+?)(?=\n(?:1|INTRODUCTION|Introduction|引言|I\.|\d+\.))",
            text, re.IGNORECASE | re.DOTALL
        )
        if abs_match:
            abstract_text = abs_match.group(1).strip()
            abstract_page = page_data["page_number"]
            abstract_confidence = "high"
            break

    if not abstract_text and pages:
        first_page_text = pages[0]["text"]
        paragraphs = [p.strip() for p in first_page_text.split("\n\n") if len(p.strip()) > 50]
        if paragraphs:
            abstract_text = paragraphs[0]
            abstract_confidence = "medium"

    if not title and pages:
        first_page_text = pages[0]["text"]
        lines = [l.strip() for l in first_page_text.split("\n") if l.strip()]
        if lines:
            title = lines[0]

    # 汇总所有检测到的表格
    all_tables = []
    for page_data in pages:
        all_tables.extend(page_data.get("detected_tables", []))

    # 构建结果
    # Post-process: filter out suspiciously large "figures" that are likely full-page artifacts
    page_area_threshold = 0.7  # if a "figure" covers >70% of the page, it's likely not a real figure
    filtered_figures = []
    for fig in extracted_figures:
        if fig.get("note") == "full_page_fallback":
            continue  # Skip full-page fallbacks entirely
        # Check if the figure bbox covers too much of the page
        if "bbox" in fig and "page_width" in fig and "page_height" in fig:
            fig_area = (fig["bbox"][2] - fig["bbox"][0]) * (fig["bbox"][3] - fig["bbox"][1])
            page_area = fig["page_width"] * fig["page_height"]
            if page_area > 0 and fig_area / page_area > page_area_threshold:
                continue  # Skip this figure
        filtered_figures.append(fig)
    extracted_figures = filtered_figures

    result = {
        "metadata": {
            "title": title,
            "authors": authors,
            "venue": "",
            "year": "",
            "doi": "",
            "arxiv_id": "",
            "keywords": []
        },
        "abstract": {
            "text": abstract_text,
            "page": abstract_page,
            "confidence": abstract_confidence
        },
        "pages": pages,
        "full_text": full_text,
        "figure_captions": figure_captions,
        "table_captions": table_captions,
        "extracted_figures": extracted_figures,
        "detected_tables": all_tables,
        "references": references[:50],
        "extraction_report": {
            "page_count": page_count,
            "text_extraction_status": "success",
            "figure_count": len(extracted_figures),
            "figure_render_dpi": render_dpi,
            "full_page_fallbacks": sum(1 for f in extracted_figures if f.get("note") == "full_page_fallback"),
            "table_count": len(all_tables),
            "is_scanned_pdf": len(extracted_figures) == 0 and page_count > 0,
            "warnings": [],
            "overall_confidence": "medium",
            "parsed_at": datetime.now().isoformat()
        }
    }

    doc.close()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python parse_pdf.py <pdf_path> [output_path] [--dpi 200]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = None
    dpi = 200

    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == "--dpi" and i + 1 < len(sys.argv):
            dpi = int(sys.argv[i + 1])
        elif arg.startswith("--"):
            pass
        else:
            if not output_path:
                output_path = arg

    result = parse_pdf(pdf_path, output_path, render_dpi=dpi)

    report = result["extraction_report"]
    print(f"PDF 解析完成。")
    print(f"标题: {result['metadata']['title'][:80]}")
    print(f"页数: {report['page_count']}")
    print(f"摘要: {'有' if result['abstract']['text'] else '无'}")
    print(f"渲染Figure: {report['figure_count']} 张 (其中 {report['full_page_fallbacks']} 张是全页备选)")
    print(f"检测表格: {report['table_count']} 个")
    print(f"Figure引用: {len(result['figure_captions'])} 个")
    print(f"参考文献: {len(result['references'])} 条")

    if output_path:
        print(f"输出: {output_path}")


if __name__ == "__main__":
    main()
