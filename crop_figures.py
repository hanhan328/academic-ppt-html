#!/usr/bin/env python3
"""
Figure 裁剪器 - 根据 AI 识别的边界框从整页渲染图中裁剪出完整 Figure。

配合 SKILL.md 工作流：AI 浏览 figures/pages/page_*.png，识别每张 Figure 的位置，
写入 figure_regions.json，然后本脚本执行实际裁剪。

v2 改进：
- 支持高 DPI 重渲染（从 PDF 重新渲染裁剪区域）
- 更宽松的 bbox 验证
- 更好的错误处理
"""

import json
import re
from pathlib import Path
from PIL import Image


def crop_figures(output_dir: str, dpi: int = 250):
    """
    根据 figure_regions.json 从整页图中裁剪 Figure。

    figure_regions.json 格式:
    {
        "figures": [
            {
                "id": "Figure 1",
                "page": 3,
                "description": "架构概览图，页面上半部分",
                "bbox_norm": [0.05, 0.08, 0.95, 0.52]
            },
            ...
        ]
    }

    bbox_norm: [x0, y0, x1, y1] 归一化坐标 (0.0-1.0)，相对于页面尺寸
    """
    output_dir = Path(output_dir)
    regions_path = output_dir / "figure_regions.json"
    pages_dir = output_dir / "figures" / "pages"
    figures_dir = output_dir / "figures"

    if not regions_path.exists():
        print("figure_regions.json 不存在，跳过 AI 裁剪。将使用代码自动检测的 Figure。")
        return []

    with open(regions_path, "r", encoding="utf-8") as f:
        regions = json.load(f)

    # Try to get the original PDF path for high-DPI re-rendering
    parsed_path = output_dir / "parsed_paper.json"
    pdf_path = None
    if parsed_path.exists():
        with open(parsed_path, "r", encoding="utf-8") as f:
            parsed = json.load(f)
        # Check workflow manifest for PDF path
        manifest_path = output_dir / "workflow_manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            pdf_path = manifest.get("paper_pdf_path")

    # Try to open PDF for high-DPI rendering
    doc = None
    if pdf_path and Path(pdf_path).exists():
        try:
            import fitz
            doc = fitz.open(pdf_path)
            print(f"  已从 PDF 加载文档，将使用 {dpi} DPI 渲染")
        except Exception:
            doc = None

    cropped = []
    for fig in regions.get("figures", []):
        fig_id = fig.get("id", "unknown")
        page_num = fig.get("page", 0)
        bbox_norm = fig.get("bbox_norm", None)
        description = fig.get("description", "")

        if not bbox_norm or len(bbox_norm) != 4:
            print(f"  跳过 {fig_id}: bbox_norm 无效")
            continue

        # Validate bbox values
        if any(v < 0 or v > 1 for v in bbox_norm):
            print(f"  跳过 {fig_id}: bbox_norm 超出 [0,1] 范围")
            continue

        x0n, y0n, x1n, y1n = bbox_norm
        if x1n <= x0n or y1n <= y0n:
            print(f"  跳过 {fig_id}: bbox_norm 坐标无效 (x1<=x0 或 y1<=y0)")
            continue

        safe_id = fig_id.replace(" ", "_").replace(".", "")
        filename = f"{safe_id}_p{page_num}.png"
        rel_path = f"figures/{filename}"
        save_path = figures_dir / filename

        # Method 1: High-DPI render from PDF (best quality)
        if doc and page_num > 0 and page_num <= len(doc):
            try:
                page = doc[page_num - 1]
                page_rect = page.rect
                pw, ph = page_rect.width, page_rect.height

                # Convert normalized bbox to page coordinates
                crop_rect = fitz.Rect(
                    x0n * pw, y0n * ph,
                    x1n * pw, y1n * ph
                )

                # Render at high DPI, clipped to the figure region
                clip = crop_rect
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=mat, clip=clip)
                pix.save(str(save_path))

                w_px, h_px = pix.width, pix.height
                cropped.append({
                    "id": fig_id,
                    "page": page_num,
                    "filename": filename,
                    "rel_path": rel_path,
                    "description": description,
                    "width_px": w_px,
                    "height_px": h_px,
                    "source": "ai_cropped_hires",
                    "dpi": dpi
                })
                print(f"  [OK-HiRes] {fig_id}: {description} -> {filename} ({w_px}x{h_px}px @ {dpi}DPI)")
                continue
            except Exception as e:
                print(f"  [WARN] {fig_id}: HiRes 渲染失败 ({e}), 回退到页面裁剪")

        # Method 2: Crop from page render (fallback)
        page_img_path = pages_dir / f"page_{page_num:02d}.png"
        if not page_img_path.exists():
            print(f"  跳过 {fig_id}: 页面图 {page_img_path} 不存在")
            continue

        try:
            img = Image.open(page_img_path)
            w, h = img.size

            x0 = int(x0n * w)
            y0 = int(y0n * h)
            x1 = int(x1n * w)
            y1 = int(y1n * h)

            cropped_img = img.crop((x0, y0, x1, y1))
            cropped_img.save(str(save_path), "PNG")

            cropped.append({
                "id": fig_id,
                "page": page_num,
                "filename": filename,
                "rel_path": rel_path,
                "description": description,
                "width_px": x1 - x0,
                "height_px": y1 - y0,
                "source": "ai_cropped"
            })
            print(f"  [OK] {fig_id}: {description} -> {filename} ({x1-x0}x{y1-y0}px)")

        except Exception as e:
            print(f"  [FAIL] {fig_id}: {e}")

    if doc:
        doc.close()

    print(f"\n裁剪完成: {len(cropped)} 张 Figure")

    # Update parsed_paper.json with cropped figure paths
    if parsed_path.exists():
        with open(parsed_path, "r", encoding="utf-8") as f:
            parsed = json.load(f)

        for fc in parsed.get("figure_captions", []):
            for cr in cropped:
                if fc["id"] == cr["id"]:
                    fc["image_path"] = cr["rel_path"]
                    fc["confidence"] = "high"
                    fc["image_source"] = cr.get("source", "ai_cropped")
                    break

        parsed["ai_cropped_figures"] = cropped

        with open(parsed_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)

    return cropped


def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python crop_figures.py <output_dir> [--dpi 250]")
        print()
        print("需要 output_dir 下存在 figure_regions.json（由 AI 生成）")
        print("和 figures/pages/page_*.png（由 parse_pdf.py 生成）")
        sys.exit(1)

    output_dir = sys.argv[1]
    dpi = 250
    if len(sys.argv) > 3 and sys.argv[2] == "--dpi":
        dpi = int(sys.argv[3])

    crop_figures(output_dir, dpi)


if __name__ == "__main__":
    main()
