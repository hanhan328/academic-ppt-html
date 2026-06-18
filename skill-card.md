# 🎓 Academic PPT HTML

**版本**: 2.2.0 | **作者**: Academic PPT HTML Contributors | **许可**: MIT

---

## 📝 描述

将学术论文 PDF 一键转换为完整的中文课堂演示包，包括精美的 HTML 演示文稿。

适用于研究生课堂论文汇报、组会分享、学术研讨。

---

## ✨ 功能特点

- ✅ **完整流程**：PDF 解析 → 章节检测 → 内容分析 → 摘要生成 → HTML 演示
- ✅ **精美 HTML**：16:9 宽屏，深色主题，可交互导航
- ✅ **学术导向**：专为研究生课堂论文汇报设计
- ✅ **中文输出**：所有分析、摘要、演讲稿均为中文
- ✅ **完整配套**：包含演讲稿、问答列表、PPT 大纲

---

## 📦 输出文件

| 文件 | 说明 |
|------|------|
| `parsed_paper.json` | PDF 解析结果 |
| `paper_structure.json` | 章节结构 |
| `novelty_analysis.md` | 新颖性分析 |
| `method_analysis.md` | 方法分析 |
| `experiment_analysis.md` | 实验分析 |
| `figure_table_analysis.md` | 图表分析 |
| `paper_summary_zh.md` | 中文详细摘要 |
| `one_page_summary.md` | 一页预习摘要 |
| `critical_commentary.md` | 批判性评论 |
| `presentation_outline.md` | PPT 大纲 |
| `speech_notes.md` | 演讲稿 |
| `qa_list.md` | 问答列表 |
| `presentation.html` | **HTML 演示文稿** ⭐ |
| `workflow_manifest.json` | 工作流清单 |

---

## 🚀 快速开始

### 安装依赖

```bash
pip install pymupdf
```

### 使用

```bash
cd academic-ppt-html
python run.py paper.pdf --theme dark --slides 14
```

### 配合 AI 代理使用

本工具设计为配合 AI 代理（如 Codex / OpenClaw）使用，详见 `SKILL.md` 中的完整工作流程。

---

## 🎨 主题选项

| 主题 | 风格 |
|------|------|
| `dark` | 深色科技风（默认） |
| `light` | 浅色简洁风 |
| `tech` | 极客暗黑风 |
| `warm` | 暖色学术风 |

---

## 📊 HTML 演示功能

- ⌨️ **键盘导航**：← → 空格键翻页
- 📊 **Chart.js 支持**：可添加数据图表
- 🎯 **Font Awesome 图标**：丰富视觉效果
- 📱 **16:9 响应式**：全屏演示
- 🖨️ **打印支持**：可导出 PDF

---

## 📋 工作流程

```
PDF
 │
 ├─→ [阶段 1] PDF 解析 ──→ parsed_paper.json
 │
 ├─→ [阶段 2] 章节检测 ──→ paper_structure.json
 │
 ├─→ [阶段 3] 内容分析 ──→ 4 个分析文件
 │
 ├─→ [阶段 4] 摘要评论 ──→ 3 个摘要文件
 │
 ├─→ [阶段 5] 演示准备 ──→ outline/speech/qa
 │
 └─→ [阶段 6] HTML 生成 ──→ presentation.html ⭐
```

---

## ⚠️ 注意事项

1. **初稿框架**：生成的内容是初稿框架，需要人工填充具体内容
2. **中文乱码**：确保使用 UTF-8 编码
3. **浏览器要求**：需要现代浏览器（Chrome/Edge/Firefox）

---

## 📄 文件结构

```
academic-ppt-html/
├── SKILL.md                 # Skill 规范文档
├── README.md                # 使用说明
├── skill-card.md            # 技能卡片（本文件）
├── _meta.json               # 元数据
├── run.py                   # 主运行脚本
├── parse_pdf.py             # PDF 解析模块
├── detect_sections.py       # 章节检测模块
├── analyze_paper.py         # 内容分析模块
├── generate_html.py         # HTML 生成模块
├── references/
│   └── design-system.md     # 设计系统参考
└── templates/
    └── shell-template.html  # HTML 模板
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。

---

## 📄 许可证

MIT License

---

*最后更新：2026-06-01*
