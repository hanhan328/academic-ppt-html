---
name: academic-ppt-html
description: 将学术论文 PDF 转换为完整的中文课堂演示包，包含 AI 辅助识别的论文原图、表格和精美的 HTML 演示文稿。
---

# Academic PPT HTML — 学术论文 HTML 演示生成器

## Purpose

将学术论文 PDF 一键转换为完整的课堂演示包。核心设计理念：
- **Python 脚本**处理机械任务：PDF 文本提取、整页渲染、章节检测、图片裁剪、HTML 模板渲染
- **AI 代理（你）**处理智能任务：识别 Figure 位置、阅读理解论文、撰写分析、生成摘要

## When to Use

- "帮我把这篇论文转成 PPT"
- "分析这篇论文并生成演示"
- "为这篇论文做一个课堂汇报"

## Workflow — 必须严格按此顺序执行

### Step 1: 确认输入参数

| 参数 | 必需 | 默认值 |
|------|------|--------|
| paper_pdf_path | 是 | — |
| output_dir | 否 | `outputs/{paper_name}/` |
| theme | 否 | `dark` |
| slide_count | 否 | `16` |
| presenter_name | 否 | (空) |
| course_name | 否 | (空) |
| presentation_date | 否 | (空) |

### Step 2: PDF 解析（脚本）

```bash
cd {SKILL_DIR} && python parse_pdf.py "{paper_pdf_path}" "{output_dir}/parsed_paper.json"
```

产出：
- `parsed_paper.json` — 全文、元数据、caption 引用、代码自动检测的 Figure
- `figures/pages/page_01.png` ... — **每页的整页渲染图（150 DPI），供 AI 浏览识别**

### Step 3: AI 识别 Figure 位置（核心步骤）

**这是获取论文原图的关键步骤。** 代码自动检测只能猜个大概，AI 视觉识别才精准。

#### 3a. 浏览页面图片

用 `view_image` 工具查看 `{output_dir}/figures/pages/page_*.png`。

重点关注：哪些页面有 Figure？每张 Figure 大约在页面的什么位置？

#### 3b. 为每张 Figure 确定边界框 — 精确标注指南

用归一化坐标 `[x0, y0, x1, y1]`（0.0~1.0，相对于页面宽高）描述每张 Figure 的位置。

**⚠️ 极其重要的标注规则：**

1. **只框 Figure 本身** — 绝对不要包含：
   - Figure 上方的正文段落
   - Figure 下方的正文段落
   - 页眉、页脚、页码
   - 相邻的 Figure（如果一页有多个独立 Figure，分别标注）

2. **Figure 的边界应包含：**
   - 图片/图表本身
   - 图注（caption）文字（如 "Figure 1: ..."）
   - 子图标签（如 (a), (b), (c)）

3. **一图一框** — 如果页面上有多个不相连的 Figure，每个 Figure 单独一个条目

4. **宁可稍大不要切到内容** — 但绝不能大到包含周围的正文

```json
{
    "figures": [
        {
            "id": "Figure 1",
            "page": 3,
            "description": "模型架构总览图，占据页面上半部分约 40%",
            "bbox_norm": [0.05, 0.06, 0.95, 0.48]
        },
        {
            "id": "Figure 2",
            "page": 5,
            "description": "实验结果对比柱状图，页面中部",
            "bbox_norm": [0.08, 0.35, 0.92, 0.72]
        },
        {
            "id": "Figure 3a",
            "page": 7,
            "description": "消融实验左子图",
            "bbox_norm": [0.05, 0.10, 0.48, 0.45]
        },
        {
            "id": "Figure 3b",
            "page": 7,
            "description": "消融实验右子图",
            "bbox_norm": [0.52, 0.10, 0.95, 0.45]
        }
    ]
}
```

- `id` 必须与 `parsed_paper.json` 中 `figure_captions` 的 `id` 匹配（如 "Figure 1"）
- 如果一页有多个子图，分别为每个子图创建独立条目

将上述 JSON 写入 `{output_dir}/figure_regions.json`。

#### 3c. 执行裁剪

```bash
cd {SKILL_DIR} && python crop_figures.py "{output_dir}"
```

这会根据你的边界框从整页渲染图中裁剪出 `figures/Figure_1_p3.png` 等文件，并更新 `parsed_paper.json` 中的 `image_path`。

### Step 4: 章节检测（脚本）

```bash
cd {SKILL_DIR} && python detect_sections.py "{output_dir}/parsed_paper.json" "{output_dir}/paper_structure.json"
```

### Step 5: 深入阅读论文（AI）

从 `parsed_paper.json` 读取 `full_text`，仔细阅读理解论文。

**绝对禁止使用"待分析"占位符。**

### Step 6: 生成分析文档（AI 撰写）

- **6a.** `novelty_analysis.md`
- **6b.** `method_analysis.md`
- **6c.** `experiment_analysis.md`
- **6d.** `figure_table_analysis.md` — 现在每个 Figure 都有 `image_path` 指向裁剪后的原图，在分析中可以直接引用

### Step 7: 生成摘要与评论（AI 撰写）

- **7a.** `paper_summary_zh.md`
- **7b.** `one_page_summary.md`
- **7c.** `critical_commentary.md`

### Step 8: 生成演示准备材料（AI 撰写）

- **8a.** `presentation_outline.md`
- **8b.** `speech_notes.md`
- **8c.** `qa_list.md`

### Step 9: 生成 HTML 演示文稿

```bash
cd {SKILL_DIR} && python generate_html.py "{output_dir}" "{theme}" {slide_count} "{presenter_name}" "{course_name}" "{presentation_date}"
```

`generate_html.py` 会自动使用 AI 裁剪的高质量 Figure 图片，并根据图片内容（caption关键词）智能匹配到对应的幻灯片位置（如方法图放在方法章节后，实验结果图放在实验章节后）。

### Step 10: 创建工作流清单

创建 `{output_dir}/workflow_manifest.json`。

## 输出文件结构

```
{output_dir}/
├── parsed_paper.json
├── paper_structure.json
├── figure_regions.json        ← AI 识别的 Figure 边界框
├── novelty_analysis.md
├── method_analysis.md
├── experiment_analysis.md
├── figure_table_analysis.md
├── paper_summary_zh.md
├── one_page_summary.md
├── critical_commentary.md
├── presentation_outline.md
├── speech_notes.md
├── qa_list.md
├── figures/
│   ├── pages/                 ← 整页渲染（150 DPI，供 AI 浏览）
│   │   ├── page_01.png
│   │   └── ...
│   ├── Figure_1_p3.png        ← AI 裁剪的 Figure 原图
│   ├── Figure_2_p5.png
│   └── ...
├── presentation.html          ← 最终产物（玻璃拟态设计）
└── workflow_manifest.json
```

## Dependencies

- Python 3.8+
- PyMuPDF >= 1.23.0: `pip install pymupdf`
- Pillow: `pip install Pillow`

## Quality Rules

- **严禁"待分析"占位符**
- Figure 边界框必须精确——只框图片+caption，绝不包含周围正文
- 一页多图时必须分别标注，不要合并
- 中文输出为默认语言
- 反幻觉：不捏造数据

## Error Handling

| 错误 | 处理 |
|------|------|
| PDF 无法解析 | 停止 |
| AI 无法识别 Figure | 使用代码自动检测的 Figure 作为备选（已过滤全页误检） |
| 裁剪失败 | 使用整页图作为备选 |
| HTML 生成失败 | 仍输出大纲和演讲辞 |
