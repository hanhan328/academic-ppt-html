#!/usr/bin/env python3
"""
论文分析辅助模块 - 提供从 parsed JSON 中提取结构化信息的工具函数。
实际分析内容由 AI 代理生成，本模块仅辅助数据提取和格式化。
"""

import json
import re
from pathlib import Path


def get_section_text(structure: dict, normalized_type: str) -> str:
    """从 structure 中提取指定类型的章节文本"""
    for sec in structure.get("sections", []):
        if sec.get("normalized_type") == normalized_type:
            return sec.get("text", "")
    return ""


def get_all_section_texts(structure: dict) -> dict:
    """提取所有章节文本，按类型分组"""
    result = {}
    for sec in structure.get("sections", []):
        ntype = sec.get("normalized_type", "unknown")
        if ntype not in result:
            result[ntype] = []
        result[ntype].append({
            "name": sec.get("name", ""),
            "text": sec.get("text", ""),
            "start_page": sec.get("start_page", 0),
            "confidence": sec.get("confidence", "medium")
        })
    return result


def extract_abstract(parsed: dict) -> dict:
    """提取摘要信息"""
    abstract = parsed.get("abstract", {})
    return {
        "text": abstract.get("text", ""),
        "page": abstract.get("page", 1),
        "confidence": abstract.get("confidence", "medium")
    }


def extract_metadata(parsed: dict) -> dict:
    """提取论文元数据"""
    meta = parsed.get("metadata", {})
    return {
        "title": meta.get("title", ""),
        "authors": meta.get("authors", ""),
        "venue": meta.get("venue", ""),
        "year": meta.get("year", ""),
        "doi": meta.get("doi", ""),
        "arxiv_id": meta.get("arxiv_id", ""),
        "keywords": meta.get("keywords", [])
    }


def extract_figures(parsed: dict) -> dict:
    """提取图表引用"""
    return {
        "figures": parsed.get("figure_captions", []),
        "tables": parsed.get("table_captions", []),
        "total_figures": len(parsed.get("figure_captions", [])),
        "total_tables": len(parsed.get("table_captions", []))
    }


def get_structured_context(parsed_path: str, structure_path: str) -> dict:
    """
    读取解析结果，返回结构化上下文供 AI 分析使用。
    这是 AI 代理生成分析内容时的主要数据源。
    """
    with open(parsed_path, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    with open(structure_path, "r", encoding="utf-8") as f:
        structure = json.load(f)

    sections = get_all_section_texts(structure)

    return {
        "metadata": extract_metadata(parsed),
        "abstract": extract_abstract(parsed),
        "sections": sections,
        "figures": extract_figures(parsed),
        "full_text": parsed.get("full_text", ""),
        "page_count": parsed.get("extraction_report", {}).get("page_count", 0)
    }
