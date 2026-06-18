#!/usr/bin/env python3
"""
章节检测器 - 检测并标准化论文章节结构
"""

import json
import re
from pathlib import Path
from datetime import datetime


def detect_sections(parsed_paper_path: str, output_path: str = None):
    """
    检测论文章节结构
    
    Args:
        parsed_paper_path: parsed_paper.json 路径
        output_path: 输出 JSON 路径
    
    Returns:
        dict: 章节结构
    """
    with open(parsed_paper_path, 'r', encoding='utf-8') as f:
        parsed = json.load(f)
    
    title = parsed['metadata']['title']
    abstract = parsed['abstract']['text']
    pages = parsed['pages']
    full_text = parsed['full_text']
    
    # 章节类型映射
    section_patterns = {
        'abstract': [r'abstract', r'摘要'],
        'introduction': [r'introduction', r'引言'],
        'related_work': [r'related work', r'related works', r'literature review', r'background', r'prior work', r'相关工作'],
        'method': [r'method', r'methodology', r'approach', r'proposed', r'model', r'framework', r'algorithm', r'architecture', r'方法'],
        'experiments': [r'experiment', r'evaluation', r'result', r'analysis', r'ablation', r'实验', r'结果', r'评估'],
        'discussion': [r'discussion', r'limitation', r'threat', r'讨论', r'局限'],
        'conclusion': [r'conclusion', r'future work', r'结论', r'总结'],
        'references': [r'references', r'bibliography', r'参考文献'],
        'appendix': [r'appendix', r'supplementary', r'附录']
    }
    
    sections = []
    detected_types = {k: False for k in section_patterns.keys()}
    
    # 检测编号章节
    section_headers = re.finditer(r'^(\d+)\s+([A-Z][a-zA-Z\s]+)$', full_text, re.MULTILINE | re.IGNORECASE)
    
    headers_found = []
    for match in section_headers:
        section_num = match.group(1)
        section_name = match.group(2).strip()
        headers_found.append({
            'num': section_num,
            'name': section_name,
            'start_pos': match.start(),
            'text': match.group(0)
        })
    
    # 按关键词检测
    for norm_type, patterns in section_patterns.items():
        for pattern in patterns:
            matches = list(re.finditer(rf'(?:^|\n)(\d+\s+)?{pattern}', full_text, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                if match.start() not in [h['start_pos'] for h in headers_found]:
                    section_name = match.group(0).strip()
                    headers_found.append({
                        'num': match.group(1) if match.group(1) else '',
                        'name': section_name,
                        'start_pos': match.start(),
                        'text': match.group(0)
                    })
    
    # 按位置排序
    headers_found.sort(key=lambda x: x['start_pos'])
    
    # 去重
    unique_headers = []
    for h in headers_found:
        if not unique_headers or h['start_pos'] - unique_headers[-1]['start_pos'] > 50:
            unique_headers.append(h)
    
    # 构建章节
    for i, header in enumerate(unique_headers):
        start_pos = header['start_pos']
        end_pos = unique_headers[i+1]['start_pos'] if i+1 < len(unique_headers) else len(full_text)
        section_text = full_text[start_pos:end_pos].strip()
        
        # 查找页码
        start_page = 1
        for page in pages:
            if page['text'] and full_text[start_pos:start_pos+50] in page['text']:
                start_page = page['page_number']
                break
        
        # 标准化类型
        norm_type = 'unknown'
        confidence = 'medium'
        for ntype, patterns in section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, header['name'], re.IGNORECASE):
                    norm_type = ntype
                    detected_types[ntype] = True
                    confidence = 'high' if ntype in ['introduction', 'method', 'experiments', 'conclusion'] else 'medium'
                    break
            if norm_type != 'unknown':
                break
        
        sections.append({
            'id': f'sec_{len(sections)+1}',
            'name': header['name'],
            'normalized_type': norm_type,
            'start_page': start_page,
            'end_page': start_page + 2,
            'text': section_text[:5000],
            'subsections': [],
            'evidence_span': {
                'start_text': section_text[:200],
                'end_text': section_text[-200:] if len(section_text) > 400 else section_text
            },
            'confidence': confidence
        })
    
    result = {
        'title': title,
        'abstract': abstract,
        'sections': sections,
        'detected_types': detected_types,
        'warnings': [],
        'overall_confidence': 'high' if len(sections) >= 5 else 'medium',
        'detected_at': datetime.now().isoformat()
    }
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result


def main():
    import sys
    if len(sys.argv) < 2:
        print("用法：python detect_sections.py <parsed_paper.json> [output_path]")
        sys.exit(1)
    
    parsed_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = detect_sections(parsed_path, output_path)
    
    print(f"章节检测完成。")
    print(f"标题：{result['title'][:80]}")
    print(f"检测到的章节:")
    for sec in result['sections']:
        print(f"  {sec['id']}: {sec['name']} -> {sec['normalized_type']}")
    
    if output_path:
        print(f"输出：{output_path}")


if __name__ == "__main__":
    main()
