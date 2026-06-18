# Academic PPT HTML Skill

将学术论文 PDF 一键转换为完整的中文课堂演示包，包括精美的 HTML 演示文稿。

## 功能特点

- ✅ **完整流程**：PDF 解析 → 章节检测 → 内容分析 → 摘要生成 → HTML 演示
- ✅ **精美 HTML**：16:9 宽屏，深色主题，可交互导航
- ✅ **学术导向**：专为研究生课堂论文汇报设计
- ✅ **中文输出**：所有分析、摘要、演讲稿均为中文
- ✅ **完整配套**：包含演讲稿、问答列表、PPT 大纲

## 输出文件

```
{output_dir}/
├── parsed_paper.json          # PDF 解析结果
├── paper_structure.json       # 章节结构
├── novelty_analysis.md        # 新颖性分析
├── method_analysis.md         # 方法分析
├── experiment_analysis.md     # 实验分析
├── figure_table_analysis.md   # 图表分析
├── paper_summary_zh.md        # 中文详细摘要
├── one_page_summary.md        # 一页预习摘要
├── critical_commentary.md     # 批判性评论
├── presentation_outline.md    # PPT 大纲
├── speech_notes.md            # 演讲稿
├── qa_list.md                 # 问答列表
├── presentation.html          # HTML 演示文稿 ⭐
└── workflow_manifest.json     # 工作流清单
```

## 安装

```bash
git clone https://github.com/hanhan328/academic-ppt-html.git
cd academic-ppt-html
pip install -r requirements.txt
```

> 依赖：PyMuPDF >= 1.23.0, Pillow >= 9.0

## 使用方法

### 方法 1: 命令行

```bash
cd academic-ppt-html
python run.py <pdf_path> [选项]
```

**示例**：

```bash
# 基本用法
python run.py paper.pdf

# 指定主题和幻灯片数量
python run.py paper.pdf --theme light --slides 12

# 指定汇报人信息
python run.py paper.pdf --presenter "张三" --course "机器学习" --date "2026 年 6 月 1 日"
```

**选项**：

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--output_dir` | 输出目录 | `outputs/{paper_name}` |
| `--theme` | 主题：dark, light, tech, warm | `dark` |
| `--slides` | 幻灯片数量 | `14` |
| `--presenter` | 汇报人姓名 | `''` |
| `--course` | 课程名称 | `''` |
| `--date` | 汇报日期 | `''` |

### 方法 2: Python API

```python
from run import main

main([
    'run.py',
    'paper.pdf',
    '--theme', 'dark',
    '--slides', '14',
    '--presenter', '张三'
])
```


## 主题选项

| 主题 | 背景色 | 文字色 | 主色 | 强调色 |
|------|--------|--------|------|--------|
| dark | #0f172a | #f8fafc | #3b82f6 | #f59e0b |
| light | #f8fafc | #0f172a | #2563eb | #d97706 |
| tech | #0a0a0a | #10b981 | #06b6d4 | #8b5cf6 |
| warm | #1c1917 | #fef3c7 | #f97316 | #fb7185 |

## HTML 演示功能

- ⌨️ **键盘导航**：← → 空格键翻页
- 📊 **Chart.js 支持**：可添加数据图表
- 🎯 **Font Awesome 图标**：丰富视觉效果
- 📱 **16:9 响应式**：全屏演示
- 🖨️ **打印支持**：可导出 PDF

## 工作流程

```
PDF
 │
 ├─→ [阶段 1] PDF 解析 ──→ parsed_paper.json
 │
 ├─→ [阶段 2] 章节检测 ──→ paper_structure.json
 │
 ├─→ [阶段 3] 内容分析 ──→ novelty/method/experiment/figure 分析
 │
 ├─→ [阶段 4] 摘要评论 ──→ summary/one_page/commentary
 │
 ├─→ [阶段 5] 演示准备 ──→ outline/speech/qa
 │
 └─→ [阶段 6] HTML 生成 ──→ presentation.html ⭐
```

## 质量要求

- ✅ 中文输出（除非用户要求英文）
- ✅ 置信度标记（High/Medium/Low）
- ✅ 人工核对提示（低置信度内容）
- ✅ 可追溯性（页码、章节引用）
- ✅ 反幻觉规则（不捏造数据）

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| PDF 无法解析 | 报告错误，停止流程 |
| 章节检测失败 | 使用全文本分析，标记低置信度 |
| 图表提取失败 | 使用 caption 和上下文 |
| HTML 生成失败 | 仍输出大纲和演讲稿 |

## 示例输出

请参考本文档中的使用示例。

## 故障排除

### 问题：中文乱码

确保文件使用 UTF-8 编码保存。

### 问题：HTML 无法打开

检查浏览器是否支持现代 JavaScript。

### 问题：分析内容过于简略

这是预期行为。skill 生成的是**初稿框架**，需要人工填充具体内容。

## 贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。
